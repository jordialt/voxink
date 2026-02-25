import os
import sys
import time
import threading

# Add the project directory to sys.path so 'src' can be imported directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import RECORD_HOTKEY, USE_AI_FORMATTING
from src.hotkey import HotkeyListener
from src.audio import AudioRecorder
from src.stt import SpeechToText
from src.llm import LLMFormatter
from src.injector import TextInjector
import subprocess

class VoxinkDaemon:
    def __init__(self):
        print("Initializing Voxink components...")
        self.audio = AudioRecorder()
        self.stt = SpeechToText()
        self.llm = LLMFormatter()
        self.injector = TextInjector()
        
        # Lock to ensure we don't spam recordings
        self.is_processing = False

        self.hotkey_listener = HotkeyListener(
            key_name=RECORD_HOTKEY,
            on_press=self.on_hotkey_press,
            on_release=self.on_hotkey_release
        )

    def _notify(self, title: str, message: str):
        try:
            subprocess.run(['notify-send', title, message], check=False)
        except Exception:
            pass

    def on_hotkey_press(self):
        if self.is_processing:
            return
        print("\n--- Hotkey Pressed: Start Recording ---")
        self._notify("Voxink", "🎙️ Recording Started")
        self.audio.start_recording()

    def on_hotkey_release(self):
        if self.is_processing or not self.audio.recording:
            return
        print("--- Hotkey Released: Stop Recording ---")
        self._notify("Voxink", "⏳ Analyzing Audio...")
        
        # run processing in background thread to not block hotkey listener
        threading.Thread(target=self._process_audio).start()

    def _process_audio(self):
        self.is_processing = True
        try:
            audio_path = self.audio.stop_recording()
            if not audio_path:
                print("No audio captured.")
                self.is_processing = False
                return
            
            # Step 1: STT
            print("Transcribing...")
            raw_text = self.stt.transcribe(audio_path)
            print(f"Raw transcription: {raw_text}")
            
            if not raw_text:
                self._notify("Voxink", "❌ No speech detected.")
                self.is_processing = False
                return

            # Step 2: LLM formatting
            final_text = raw_text
            if USE_AI_FORMATTING:
                print("Formatting with AI...")
                final_text = self.llm.format_text(raw_text)
                print(f"AI Formatted: {final_text}")
            
            # Step 3: Inject Text
            print("Injecting into active window...")
            self.injector.inject_text(final_text)
            self._notify("Voxink", "✅ Text Inserted")
        except Exception as e:
            print(f"Error during processing: {e}")
            self._notify("Voxink", f"⚠️ Error: {e}")
        finally:
            self.is_processing = False

    def run(self):
        print("\nStarting Voxink Daemon...")
        print(f"Hold '{RECORD_HOTKEY}' to dictate.")
        print(f"AI Formatting (Ollama): {'ON' if USE_AI_FORMATTING else 'OFF'}")
        self.hotkey_listener.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.hotkey_listener.stop()

if __name__ == "__main__":
    daemon = VoxinkDaemon()
    daemon.run()
