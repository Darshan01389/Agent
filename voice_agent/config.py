import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
NOTES_FILE = DATA_DIR / "notes.md"
REMINDERS_FILE = DATA_DIR / "reminders.json"

# ─── NVIDIA API ───────────────────────────────────────────
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_LLM_BASE_URL = "https://integrate.api.nvidia.com/v1"
NEMOTRON_LLM_MODEL = os.getenv(
    "NEMOTRON_LLM_MODEL", "nvidia/nvidia-nemotron-nano-9b-v2"
)

# Nemotron ASR hosted gRPC
NEMOTRON_ASR_FUNCTION_ID = "bb0837de-8c7b-481f-9ec8-ef5663e9c1fa"
NEMOTRON_ASR_HOST = "grpc.nvcf.nvidia.com:443"
NEMOTRON_LANGUAGE_CODE = os.getenv("NEMOTRON_LANGUAGE_CODE", "en-US")

# Background Noise Removal hosted gRPC
BNR_FUNCTION_ID = "66518fde-1164-479b-a21f-f8240104505a"
BNR_HOST = "grpc.nvcf.nvidia.com:443"
BNR_INTENSITY = float(os.getenv("BNR_INTENSITY", "1.0"))

# ─── Audio ────────────────────────────────────────────────
SAMPLE_RATE = 16000
CHANNELS = 1
RECORD_TIMEOUT_SEC = 6
PHRASE_LIMIT_SEC = 12

# ─── Activation ─────────────────────────────────────────────
WAKE_WORDS = [
    w.strip().lower()
    for w in os.getenv("WAKE_WORDS", "hey agent,hi agent,hello agent").split(",")
    if w.strip()
]
HOTKEY = os.getenv("HOTKEY", "space")

# ─── TTS ──────────────────────────────────────────────────
ENABLE_TTS = os.getenv("ENABLE_TTS", "false").lower() in ("1", "true", "yes")
TTS_RATE = int(os.getenv("TTS_RATE", "175"))

# ─── Assistant Persona ────────────────────────────────────
SYSTEM_PROMPT = (
    "You are a helpful, concise voice assistant powered by NVIDIA Nemotron. "
    "Keep responses short and conversational (2-3 sentences max) since they "
    "will be spoken aloud. Avoid markdown, bullet points, or special characters."
)
