"""
wake_word.py
------------
Background thread listening for wake-word phrases via lightweight ASR snippets.
"""

from __future__ import annotations

import threading

from config import WAKE_WORDS
from core.audio_capture import record_once


class WakeWordDetector:
    """Runs in a daemon thread; calls on_wake() when a wake word is detected."""

    def __init__(self, on_wake):
        self._on_wake = on_wake
        self._running = False
        self._thread: threading.Thread | None = None
        self._paused = False

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False

    def _loop(self):
        from nvidia.asr_client import transcribe
        from nvidia.bnr_client import denoise

        while self._running:
            if self._paused:
                threading.Event().wait(0.3)
                continue
            try:
                rec = record_once(timeout=3, phrase_limit=4)
                if rec["error"] or not rec["pcm"]:
                    continue

                denoised = denoise(rec["pcm"], rec["sample_rate"])
                pcm = denoised["pcm"] or rec["pcm"]
                result = transcribe(pcm, rec["sample_rate"])
                text = result.get("text", "").lower().strip()
                if text and any(ww in text for ww in WAKE_WORDS):
                    self._on_wake()
            except Exception as exc:
                print(f"[WakeWord] {exc}")
