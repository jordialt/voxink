# Voxink

**Voice becomes ink.** A local, offline AI voice dictation daemon for Linux.

Hold a key. Speak. Release. Your words appear — cleaned up, punctuated, and injected directly into whatever window is active. No cloud. No API keys. No data leaving your machine.

---

## What it is

Voxink is a lightweight background daemon that gives Linux a system-wide voice dictation capability. It works across every application — browser, terminal, IDE, chat, anything — without requiring clipboard hacks, browser extensions, or subscriptions.

The full pipeline runs locally: audio capture → Whisper transcription → optional LLM cleanup via Ollama → text injection into the focused window. On typical hardware, the turnaround from releasing the hotkey to seeing text appear is under two seconds.

---

## Features

- **100% offline** — Whisper and Ollama both run locally. No network calls, ever.
- **System-wide** — works in any application that accepts keyboard input.
- **AI cleanup** — removes filler words ("umm", "uhh", "like", "you know") and fixes punctuation automatically using a tiny, fast local model (qwen2.5:0.5b).
- **Lightning Mode** — disable AI formatting entirely for raw, instant transcription.
- **Wayland and X11 support** — auto-detects the session type and uses the right injection method (`wtype`/`wl-copy` on Wayland, `xdotool`/`xclip` on X11).
- **Desktop notifications** — visual feedback at each stage (recording started, processing, inserted).
- **Unobtrusive** — runs as a background daemon, logs to `/tmp/voxink.log`.

---

## How it works

```
  [Hold Alt Gr]
       |
       v
  AudioRecorder            sounddevice streams mic input into a queue;
  (audio.py)               scipy writes it to /tmp/voxink_audio.wav on release

       |
       v
  SpeechToText             faster-whisper loads the audio file and runs
  (stt.py)                 beam-search transcription locally on CPU (or GPU)

       |
       v
  LLMFormatter             ollama.chat() sends the raw transcript to a local
  (llm.py)                 qwen2.5:0.5b instance with a system prompt that
                           strips fillers and fixes punctuation
                           (skipped entirely in Lightning Mode)

       |
       v
  TextInjector             Wayland: wl-copy + wtype Ctrl+V
  (injector.py)            X11:     xclip  + xdotool Ctrl+V

       |
       v
  [Text appears in focused window]
```

The daemon main loop (`main.py`) orchestrates all of this. Audio processing runs in a background thread so the hotkey listener never blocks.

---

## Prerequisites

### System packages

**Wayland:**
```bash
sudo apt install wl-clipboard wtype libnotify-bin
```

**X11:**
```bash
sudo apt install xclip xdotool libnotify-bin
```

Both session types also need access to `/dev/input` for the global hotkey listener. Running the daemon with `sudo` (as the provided `start_daemon.sh` does) handles this.

### Ollama

Ollama must be installed and running as a service before you start Voxink (only required if `USE_AI_FORMATTING = True`).

Install:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Pull the default model:
```bash
ollama pull qwen2.5:0.5b
```

Confirm Ollama is running:
```bash
ollama list
```

### Python

Python 3.13 or later is required. The project uses [uv](https://docs.astral.sh/uv/) for dependency management.

Install uv if you don't have it:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Microphone

Any microphone visible to ALSA/PipeWire works. Confirm yours is recognized:
```bash
python3 -c "import sounddevice; print(sounddevice.query_devices())"
```

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/voxink.git
cd voxink

# 2. Create the virtual environment and install dependencies
uv sync

# 3. Pull the Ollama model (skip if using Lightning Mode)
ollama pull qwen2.5:0.5b
```

That's it. No build step, no compilation.

---

## Configuration

All settings live in `src/config.py`. Edit them directly — there is no separate config file to manage.

| Setting | Default | Description |
|---|---|---|
| `RECORD_HOTKEY` | `"Key.alt_gr"` | Key to hold for dictation. Uses pynput key names (e.g. `"Key.f12"`, `"Key.ctrl_r"`). |
| `SAMPLE_RATE` | `44100` | Audio sample rate in Hz. |
| `WHISPER_MODEL` | `"base.en"` | Whisper model size. Options: `"tiny.en"`, `"base.en"`, `"small.en"`, `"medium.en"`. Larger = more accurate, slower to load. |
| `WHISPER_DEVICE` | `"cpu"` | `"cpu"` or `"cuda"`. Use `"cuda"` if you have a compatible NVIDIA GPU. |
| `WHISPER_COMPUTE_TYPE` | `"int8"` | Quantization type. `"int8"` for CPU, `"float16"` for GPU. |
| `USE_AI_FORMATTING` | `True` | Set to `False` to enable Lightning Mode — raw transcription only, no Ollama call. |
| `OLLAMA_MODEL` | `"qwen2.5:0.5b"` | Any model available in your local Ollama instance. Larger models clean up text better but add latency. |
| `SYSTEM_PROMPT` | *(see config.py)* | The instruction given to the LLM. Customize this to change formatting behavior. |

### Changing the hotkey

The `RECORD_HOTKEY` value must be a valid pynput key name string. Examples:

```python
RECORD_HOTKEY = "Key.alt_gr"   # Right Alt / AltGr (default)
RECORD_HOTKEY = "Key.f12"      # F12
RECORD_HOTKEY = "Key.ctrl_r"   # Right Ctrl
```

### Using a GPU

If you have a CUDA-capable GPU and the appropriate drivers installed:

```python
WHISPER_DEVICE = "cuda"
WHISPER_COMPUTE_TYPE = "float16"
```

This dramatically reduces transcription time for longer dictations and enables larger Whisper models without noticeable lag.

### Lightning Mode

Disable Ollama entirely for zero-latency raw transcription:

```python
USE_AI_FORMATTING = False
```

Transcription will still run through Whisper, but the LLM formatting step is skipped. Text is injected as-is from Whisper's output.

### Using a different Ollama model

Any model you have pulled locally will work:

```python
OLLAMA_MODEL = "qwen2.5:1.5b"   # More accurate, slightly slower
OLLAMA_MODEL = "llama3.2:1b"    # Alternative small model
OLLAMA_MODEL = "gemma3:1b"      # Another option
```

For dictation cleanup, smaller is generally better — you want speed, not reasoning depth.

---

## Usage

### Run interactively (foreground)

```bash
sudo -E .venv/bin/python src/main.py
```

`sudo` is required for the keyboard listener to read from `/dev/input`. The `-E` flag preserves your environment variables, which is necessary for audio (`PULSE_RUNTIME_PATH`, `XDG_RUNTIME_DIR`) and display session detection.

### Run as a background daemon

```bash
./start_daemon.sh
```

This kills any existing Voxink process, starts a new one in the background with `nohup`, and logs all output to `/tmp/voxink.log`.

Follow the log:
```bash
tail -f /tmp/voxink.log
```

Stop the daemon:
```bash
sudo pkill -f "python src/main.py"
```

### Dictation workflow

1. Focus the window or text field where you want to type.
2. Hold **Alt Gr** (or your configured key). A desktop notification confirms recording has started.
3. Speak naturally. You can speak for as long as you need — there is no timeout.
4. Release the key.
5. Voxink transcribes your audio, optionally runs it through the LLM, and types the result into your focused window.

Desktop notifications give you feedback at each stage:
- `Recording Started` — mic is live.
- `Analyzing Audio...` — transcription and formatting are running.
- `Text Inserted` — done.

---

## Troubleshooting

### No audio captured / sounddevice errors

Confirm your default microphone is accessible:
```bash
python3 -c "import sounddevice as sd; print(sd.query_devices())"
```

If you are running with `sudo`, PulseAudio or PipeWire may not be accessible because the audio server runs as your user. The `start_daemon.sh` uses `sudo -E` to carry your environment variables through, which resolves this in most setups.

If audio still fails under sudo, try running as your user with uinput permissions instead (see the permissions section below).

### Hotkey not detected

The global hotkey listener reads from `/dev/input` directly, which requires root or membership in the `input` group. The simplest fix is using sudo (handled by `start_daemon.sh`). To avoid sudo, add your user to the input group and log out/in:

```bash
sudo usermod -aG input $USER
```

Note that even after adding yourself to the group, the keyboard module may still have issues on some distributions. Using sudo is the most reliable approach.

### Text not injecting on Wayland

Wayland text injection requires `wtype` and `wl-clipboard`:

```bash
sudo apt install wtype wl-clipboard
```

Some compositors (notably GNOME with certain security settings) restrict synthetic input injection. If text does not appear, try a different compositor or check if `wtype` works independently:

```bash
wtype "hello"
```

### Text not injecting on X11

Install the required tools:
```bash
sudo apt install xdotool xclip
```

Test them independently:
```bash
echo "hello" | xclip -selection clipboard
xdotool key ctrl+v
```

### Ollama connection error

Verify Ollama is running:
```bash
curl http://localhost:11434/api/tags
```

If it is not running, start it:
```bash
ollama serve
```

If Ollama is running but the model is missing:
```bash
ollama pull qwen2.5:0.5b
```

### Whisper model download

On first run, faster-whisper downloads the Whisper model weights from Hugging Face. This requires internet access the first time only. Subsequent runs are fully offline. Models are cached in `~/.cache/huggingface/`.

If the download fails or the cache is corrupted:
```bash
rm -rf ~/.cache/huggingface/hub/models--Systran--faster-whisper-base.en
# Then run again to re-download
```

### Permission denied on /dev/input

```
PermissionError: [Errno 13] Permission denied: '/dev/input/event...'
```

Use `sudo -E` as shown in the usage instructions, or add your user to the `input` group and reboot.

### Daemon already running

`start_daemon.sh` automatically kills any existing instance before starting a new one. If you need to do this manually:

```bash
sudo pkill -f "python src/main.py"
```

---

## Project structure

```
voxink/
├── src/
│   ├── main.py       # VoxinkDaemon — orchestrates the full pipeline
│   ├── config.py     # All configuration settings
│   ├── audio.py      # AudioRecorder — sounddevice stream capture
│   ├── stt.py        # SpeechToText — faster-whisper transcription
│   ├── llm.py        # LLMFormatter — Ollama filler-word removal
│   ├── hotkey.py     # HotkeyListener — global key press/release detection
│   └── injector.py   # TextInjector — Wayland/X11 text injection
├── start_daemon.sh   # Background daemon launcher
├── pyproject.toml
└── uv.lock
```

Each module in `src/` can be run directly as a standalone test:

```bash
# Test audio capture (records 3 seconds)
sudo -E .venv/bin/python src/audio.py

# Test STT on a live recording
sudo -E .venv/bin/python src/stt.py --test

# Test LLM formatting
sudo -E .venv/bin/python src/llm.py --test "uhh I think I want to like test this thing"

# Test text injection (focus a text field within 3 seconds)
sudo -E .venv/bin/python src/injector.py "Hello from Voxink"
```

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `faster-whisper` | >=1.2.1 | Local speech-to-text via CTranslate2-optimized Whisper |
| `ollama` | >=0.6.1 | Python client for the local Ollama LLM server |
| `sounddevice` | >=0.5.5 | Cross-platform audio capture |
| `scipy` | >=1.17.1 | WAV file writing |
| `numpy` | >=2.4.2 | Audio buffer handling |
| `pynput` | >=1.8.1 | Keyboard/mouse input monitoring |
| `evdev` | >=1.9.3 | Low-level Linux input device access |
| `keyboard` | >=0.13.5 | Global hotkey detection |

---

## License

MIT License. See [LICENSE](LICENSE) for the full text.

---

## Contributing

Bug reports and pull requests are welcome. Before opening a PR, please test against both Wayland and X11 sessions if the change touches `injector.py` or `hotkey.py`, as behavior differs between display servers.
