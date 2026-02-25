import sys
from faster_whisper import WhisperModel
from src import config

class SpeechToText:
    def __init__(self):
        print(f"Loading Whisper model '{config.WHISPER_MODEL}' on {config.WHISPER_DEVICE}...")
        self.model = WhisperModel(
            config.WHISPER_MODEL, 
            device=config.WHISPER_DEVICE, 
            compute_type=config.WHISPER_COMPUTE_TYPE
        )
        print("Whisper model loaded.")

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribes the given audio file using faster-whisper.
        Returns the raw transcribed text.
        """
        segments, info = self.model.transcribe(audio_path, beam_size=5)
        # segments is a generator, so we iterate to get all text
        text = "".join([segment.text for segment in segments])
        return text.strip()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        import sounddevice as sd
        import numpy as np
        import scipy.io.wavfile as wavfile
        import time

        print("Recording 3 seconds of audio to test STT...")
        fs = 16000
        recording = sd.rec(int(3 * fs), samplerate=fs, channels=1, dtype='float32')
        sd.wait()
        wavfile.write('/tmp/stt_test.wav', fs, recording)
        
        stt = SpeechToText()
        print("Transcribing...")
        result = stt.transcribe('/tmp/stt_test.wav')
        print(f"Result: {result}")
