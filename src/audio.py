import queue
import time
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
import threading
from src import config

class AudioRecorder:
    def __init__(self):
        self.q = queue.Queue()
        self.recording = False
        self.audio_data = []

    def _callback(self, indata, frames, time_info, status):
        # This is triggered for each audio block
        if status:
            print(f"Audio status: {status}")
        self.q.put(indata.copy())

    def start_recording(self):
        if self.recording:
            return
        
        self.recording = True
        self.audio_data = []
        # Clear the queue
        while not self.q.empty():
            self.q.get()

        self.stream = sd.InputStream(
            samplerate=config.SAMPLE_RATE,
            channels=config.CHANNELS,
            dtype='float32',
            callback=self._callback
        )
        self.stream.start()

        self.record_thread = threading.Thread(target=self._record_loop)
        self.record_thread.start()

    def _record_loop(self):
        while self.recording:
            try:
                # Wait for data, timeout to allow loop exit
                data = self.q.get(timeout=0.1)
                self.audio_data.append(data)
            except queue.Empty:
                pass

    def stop_recording(self) -> str:
        if not self.recording:
            return config.AUDIO_TMP_FILE
        
        self.recording = False
        self.stream.stop()
        self.stream.close()
        
        if self.record_thread.is_alive():
            self.record_thread.join()

        # concatenate all audio chunks
        if self.audio_data:
            audio_np = np.concatenate(self.audio_data, axis=0)
            wavfile.write(config.AUDIO_TMP_FILE, config.SAMPLE_RATE, audio_np)
        return config.AUDIO_TMP_FILE

if __name__ == "__main__":
    # Simple test for AudioRecorder
    recorder = AudioRecorder()
    print("Recording started. Speak now...")
    recorder.start_recording()
    time.sleep(3)
    file_path = recorder.stop_recording()
    print(f"Recording saved to {file_path}")
