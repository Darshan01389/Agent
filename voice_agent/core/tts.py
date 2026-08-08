"""Optional text-to-speech via pyttsx3."""

from __future__ import annotations

import threading

from config import TTS_RATE

_engine = None
_lock = threading.Lock()


def _get_engine():
    global _engine
    if _engine is None:
        import pyttsx3
        _engine = pyttsx3.init()
        _engine.setProperty("rate", TTS_RATE)
    return _engine


def speak(text: str, on_done=None):
    def _run():
        with _lock:
            engine = _get_engine()
            engine.say(text)
            engine.runAndWait()
        if on_done:
            on_done()

    threading.Thread(target=_run, daemon=True).start()


def stop():
    with _lock:
        if _engine is not None:
            try:
                _engine.stop()
            except Exception:
                pass
