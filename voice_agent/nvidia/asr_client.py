"""
asr_client.py
-------------
Nemotron ASR Streaming via NVIDIA hosted gRPC (Riva client).
"""

from __future__ import annotations

import io
import wave

import riva.client

from config import (
    NEMOTRON_ASR_FUNCTION_ID,
    NEMOTRON_ASR_HOST,
    NEMOTRON_LANGUAGE_CODE,
    NVIDIA_API_KEY,
    SAMPLE_RATE,
)


def _build_auth() -> riva.client.Auth:
    if not NVIDIA_API_KEY:
        raise RuntimeError("NVIDIA_API_KEY not set")
    return riva.client.Auth(
        uri=NEMOTRON_ASR_HOST,
        use_ssl=True,
        metadata_args=[
            ["function-id", NEMOTRON_ASR_FUNCTION_ID],
            ["authorization", f"Bearer {NVIDIA_API_KEY}"],
        ],
    )


def _pcm_to_wav(pcm: bytes, sample_rate: int = SAMPLE_RATE) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm)
    return buf.getvalue()


def transcribe(pcm: bytes, sample_rate: int = SAMPLE_RATE) -> dict:
    """
    Transcribe PCM audio using Nemotron ASR.
    Returns: {"text": str, "engine": "nemotron_asr", "error": str|None}
    """
    if not pcm:
        return {"text": "", "engine": None, "error": "empty audio"}

    try:
        auth = _build_auth()
        asr_service = riva.client.ASRService(auth)
        wav_bytes = _pcm_to_wav(pcm, sample_rate)

        config = riva.client.RecognitionConfig(
            language_code=NEMOTRON_LANGUAGE_CODE,
            max_alternatives=1,
            enable_automatic_punctuation=True,
            encoding=riva.client.AudioEncoding.LINEAR_PCM,
            sample_rate_hertz=sample_rate,
            audio_channel_count=1,
        )

        response = asr_service.offline_recognize(wav_bytes, config)

        if not response.results:
            return {"text": "", "engine": "nemotron_asr", "error": "no speech detected"}

        text = response.results[0].alternatives[0].transcript.strip()
        return {"text": text, "engine": "nemotron_asr", "error": None}

    except Exception as exc:
        err = str(exc)
        if "429" in err or "rate" in err.lower():
            err = "Rate limit reached (~40 RPM free tier). Please wait a moment."
        return {"text": "", "engine": None, "error": err}
