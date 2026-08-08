"""
audio_capture.py
----------------
Capture microphone audio as 16-bit mono PCM using sounddevice.
"""

from __future__ import annotations

import queue
import threading

import numpy as np
import sounddevice as sd

from config import CHANNELS, PHRASE_LIMIT_SEC, RECORD_TIMEOUT_SEC, SAMPLE_RATE


class AudioCapture:
    """Record one utterance from the default microphone."""

    def __init__(
        self,
        sample_rate: int = SAMPLE_RATE,
        channels: int = CHANNELS,
    ):
        self.sample_rate = sample_rate
        self.channels = channels

    def record(
        self,
        timeout: float = RECORD_TIMEOUT_SEC,
        phrase_limit: float = PHRASE_LIMIT_SEC,
    ) -> dict:
        """
        Record until silence or phrase_limit is reached.
        Returns: {"pcm": bytes, "sample_rate": int, "error": str|None}
        """
        frames: list[np.ndarray] = []
        q: queue.Queue = queue.Queue()
        done = threading.Event()

        def callback(indata, _frames, _time, status):
            if status:
                print(f"[AudioCapture] {status}")
            q.put(indata.copy())

        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="int16",
                callback=callback,
            ):
                import time

                start = time.time()
                silence_start: float | None = None
                speech_detected = False
                energy_threshold = 300.0

                while True:
                    elapsed = time.time() - start
                    if elapsed > timeout + phrase_limit:
                        break

                    try:
                        chunk = q.get(timeout=0.1)
                    except queue.Empty:
                        if speech_detected and silence_start and (time.time() - silence_start) > 0.8:
                            break
                        if elapsed > timeout and not speech_detected:
                            return {"pcm": b"", "sample_rate": self.sample_rate, "error": "timeout"}
                        continue

                    frames.append(chunk)
                    energy = float(np.abs(chunk).mean())
                    if energy > energy_threshold:
                        speech_detected = True
                        silence_start = None
                    elif speech_detected:
                        if silence_start is None:
                            silence_start = time.time()

                    if speech_detected and elapsed > phrase_limit:
                        break

        except Exception as exc:
            return {"pcm": b"", "sample_rate": self.sample_rate, "error": str(exc)}

        if not frames:
            return {"pcm": b"", "sample_rate": self.sample_rate, "error": "timeout"}

        audio = np.concatenate(frames, axis=0)
        pcm = audio.tobytes()
        return {"pcm": pcm, "sample_rate": self.sample_rate, "error": None}


def record_once(
    timeout: float = RECORD_TIMEOUT_SEC,
    phrase_limit: float = PHRASE_LIMIT_SEC,
) -> dict:
    """Convenience wrapper for a single recording."""
    return AudioCapture().record(timeout=timeout, phrase_limit=phrase_limit)
