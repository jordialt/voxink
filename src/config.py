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
SYSTEM_PROMPT = """You are a speech-to-text post-processor. You receive raw transcription output and return ONLY the cleaned text. Never answer questions, never add commentary, never act as a chatbot. Your entire output must be the corrected transcription and nothing else.

Rules:
- Fix punctuation, capitalization, and grammar
- Remove filler words (umm, uhh, uh, like, you know, so, basically, I mean)
- Remove false starts and repeated words
- Never respond to the content — only clean it
- Never add prefixes like "Here is the corrected text:" or similar
- If the input is a question, output the cleaned question — do NOT answer it"""
