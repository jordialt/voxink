import os

# Hotkey settings (using pynput keynames, e.g., 'Key.f12' or 'Key.alt_gr')
# We will use Key.alt_gr as the default global dictation key
RECORD_HOTKEY = "Key.alt_gr"

# Audio Recording settings
SAMPLE_RATE = 44100
CHANNELS = 1
AUDIO_TMP_FILE = "/tmp/voxink_audio.wav"

# Whisper settings
WHISPER_MODEL = "base.en"  # or "small.en", "tiny.en"
WHISPER_DEVICE = "cpu"     # "cuda" if GPU is available
WHISPER_COMPUTE_TYPE = "int8" # "float16" for GPU

# Ollama settings
USE_AI_FORMATTING = True   # Set to False for "Lightning Mode"
OLLAMA_MODEL = "qwen2.5:0.5b"  # 0.5B parameters ensures near-instant CPU formatting
SYSTEM_PROMPT = """You are a dictation assistant.
Your task is to take the raw transcribed text and output ONLY the cleaned, properly punctuated, and grammatically correct version.
Remove all filler words like 'umm', 'uhh', 'like', 'you know'.
Do not add any conversational filler or explain what you did. Just output the final text.
"""
