# Voice Agent (NVIDIA NIM)

WhisperFlow-style voice assistant powered by free NVIDIA NIM services:
**Background Noise Removal**, **Nemotron ASR**, and **Nemotron LLM**.

## Features

- **Noisy-environment transcription**: BNR denoising before ASR
- **Activation modes**: wake word, keyboard hotkey (`Space`), on-screen mic toggle
- **Task agents**: chat, notes (`take note`), reminders (`remind me`)
- **Copy transcript**: one-click copy for dictation workflows

## Quick Setup

### 1. Install dependencies

**Windows:** Install [FFmpeg](https://ffmpeg.org/download.html) and add to PATH.

```bash
cd voice_agent
pip install -r requirements.txt
```

### 2. Configure API key

Get a **free** NVIDIA API key at https://build.nvidia.com/settings (no credit card).

```bash
copy .env.example .env
# Edit .env and set NVIDIA_API_KEY
```

### 3. Run

```bash
python main.py
```

## Usage

| Action | How |
|---|---|
| **Push-to-talk** | Click mic button or press `Space` |
| **Wake word** | Enable toggle, say "Hey Agent" |
| **Copy transcript** | Click copy icon on any transcript bubble |
| **Clear chat** | Click trash icon |

## Agent Triggers

| Phrase | Agent |
|---|---|
| `take note`, `write down` | NoteAgent → saves to `data/notes.md` |
| `remind me`, `set reminder` | ReminderAgent → saves to `data/reminders.json` |
| (default) | ChatAgent → Nemotron LLM response |

## Project Structure

```
voice_agent/
├── main.py              # Entry point
├── config.py            # Settings
├── core/                # Audio capture, orchestration, wake word
├── nvidia/              # BNR, ASR, LLM clients
├── agents/              # Task agents + router
├── ui/                  # Flet interface
└── data/                # Notes and reminders storage
```

## NVIDIA Services Used

| Service | Model | Purpose |
|---|---|---|
| BNR | Background Noise Removal | Denoise audio before transcription |
| ASR | Nemotron ASR Streaming | Speech-to-text |
| LLM | Nemotron (OpenAI-compatible) | Agent reasoning |

Free tier: ~40 requests/minute at build.nvidia.com.

## Troubleshooting

**Mic not working?**
```bash
python -c "import sounddevice as sd; print(sd.query_devices())"
```

**429 rate limit:** Wait a moment between utterances; free tier is ~40 RPM.

**BNR unavailable:** App falls back to local `noisereduce` denoising automatically.
