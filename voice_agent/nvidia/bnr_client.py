"""
bnr_client.py
-------------
Audio denoising for noisy environments.
Primary: local noisereduce (always available).
Optional: NVIDIA BNR hosted gRPC when nim-clients protos are present.
"""

from __future__ import annotations

import io
import wave

import numpy as np

from config import BNR_INTENSITY, NVIDIA_API_KEY, SAMPLE_RATE


def _local_denoise(pcm: bytes, sample_rate: int) -> bytes:
    import noisereduce as nr

    audio = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
    reduced = nr.reduce_noise(y=audio, sr=sample_rate, stationary=True)
    strength = max(0.0, min(1.0, BNR_INTENSITY))
    blended = audio * (1.0 - strength) + reduced * strength
    return (blended * 32768.0).clip(-32768, 32767).astype(np.int16).tobytes()


def _pcm_to_wav(pcm: bytes, sample_rate: int) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm)
    return buf.getvalue()


def _wav_to_pcm(wav_bytes: bytes) -> bytes:
    with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
        return wf.readframes(wf.getnframes())


def _try_nvidia_bnr(pcm: bytes, sample_rate: int) -> bytes | None:
    """
    Attempt NVIDIA hosted BNR via gRPC.
    Requires nvidia-maxine-bnr protos (optional dependency).
    Returns cleaned PCM or None on failure.
    """
    if not NVIDIA_API_KEY:
        return None

    try:
        import grpc
        from config import BNR_FUNCTION_ID, BNR_HOST

        # Maxine BNR gRPC stub (from NVIDIA-Maxine/nim-clients)
        try:
            from maxine_bnr_pb2 import EnhanceAudioRequest  # type: ignore
            from maxine_bnr_pb2_grpc import BNRStub  # type: ignore
        except ImportError:
            return None

        wav_bytes = _pcm_to_wav(pcm, sample_rate)
        metadata = (
            ("function-id", BNR_FUNCTION_ID),
            ("authorization", f"Bearer {NVIDIA_API_KEY}"),
        )
        channel = grpc.secure_channel(
            BNR_HOST,
            grpc.ssl_channel_credentials(),
        )
        stub = BNRStub(channel)
        request = EnhanceAudioRequest(
            audio=wav_bytes,
            intensity_ratio=BNR_INTENSITY,
        )
        response = stub.EnhanceAudio(request, metadata=metadata)
        channel.close()
        return _wav_to_pcm(response.audio)

    except Exception as exc:
        print(f"[BNR] NVIDIA API unavailable: {exc}")
        return None


def denoise(pcm: bytes, sample_rate: int = SAMPLE_RATE) -> dict:
    """
    Denoise PCM audio (16-bit mono).
    Returns: {"pcm": bytes, "engine": str, "error": str|None}
    """
    if not pcm:
        return {"pcm": pcm, "engine": None, "error": "empty audio"}

    nvidia_pcm = _try_nvidia_bnr(pcm, sample_rate)
    if nvidia_pcm is not None:
        return {"pcm": nvidia_pcm, "engine": "nvidia_bnr", "error": None}

    try:
        cleaned = _local_denoise(pcm, sample_rate)
        return {"pcm": cleaned, "engine": "local", "error": None}
    except Exception as exc:
        return {"pcm": pcm, "engine": None, "error": str(exc)}
