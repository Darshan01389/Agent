"""
orchestrator.py
-----------------
Pipeline: mic → BNR → ASR → agent router → optional TTS.
"""

from __future__ import annotations

import threading

from agents.base import dispatch
from config import ENABLE_TTS
from core.audio_capture import record_once
from core.wake_word import WakeWordDetector
from nvidia.asr_client import transcribe
from nvidia.bnr_client import denoise

# Register all agents on import
import agents.chat_agent  # noqa: F401
import agents.note_agent  # noqa: F401
import agents.reminder_agent  # noqa: F401


class VoiceOrchestrator:
    def __init__(self, callbacks: dict | None = None):
        self._cb = callbacks or {}
        self._history: list[dict] = []
        self._busy = False
        self._wake = WakeWordDetector(on_wake=self._handle_wake)

    def start_wake_word(self):
        self._wake.start()
        self._status("Wake word active — say 'Hey Agent' or press Space")

    def stop_wake_word(self):
        self._wake.stop()
        self._status("Wake word disabled")

    def start_listening(self):
        if self._busy:
            return
        threading.Thread(target=self._pipeline, daemon=True).start()

    def clear_history(self):
        self._history.clear()
        self._status("Conversation cleared.")

    def stop_speaking(self):
        if ENABLE_TTS:
            from core.tts import stop
            stop()

    def _handle_wake(self):
        self._cb.get("on_wake", lambda: None)()
        if not self._busy:
            threading.Thread(target=self._pipeline, daemon=True).start()

    def _pipeline(self):
        self._busy = True
        self._wake.pause()

        try:
            self._status("Listening…")
            self._cb.get("on_listening", lambda _: None)(True)

            rec = record_once()
            self._cb.get("on_listening", lambda _: None)(False)

            if rec["error"] == "timeout":
                self._status("Timed out — try again.")
                return
            if rec["error"] or not rec["pcm"]:
                self._status(rec.get("error") or "No audio captured.")
                return

            self._status("Denoising…")
            denoised = denoise(rec["pcm"], rec["sample_rate"])
            pcm = denoised["pcm"] or rec["pcm"]
            bnr_engine = denoised.get("engine") or "none"

            self._status(f"Transcribing… [{bnr_engine}]")
            asr = transcribe(pcm, rec["sample_rate"])
            if asr["error"] or not asr["text"]:
                self._status(asr.get("error") or "Couldn't understand — try again.")
                return

            user_text = asr["text"]
            self._cb.get("on_transcript", lambda t, e: None)(user_text, asr["engine"])
            self._status(f"Routing… [{asr['engine']}]")

            self._history.append({"role": "user", "content": user_text})
            result = dispatch(user_text, self._history[:-1])
            if result.history_entry:
                self._history.append(result.history_entry)

            self._cb.get("on_agent_result", lambda r: None)(result)
            self._status(f"Done — [{result.agent_name}]")

            if ENABLE_TTS and result.speak_text:
                self._cb.get("on_speaking", lambda _: None)(True)
                from core.tts import speak

                def on_done():
                    self._cb.get("on_speaking", lambda _: None)(False)
                    self._status("Ready — press Space or say 'Hey Agent'")

                speak(result.speak_text, on_done=on_done)
            else:
                self._status("Ready — press Space or say 'Hey Agent'")

        finally:
            self._busy = False
            self._wake.resume()

    def _status(self, msg: str):
        self._cb.get("on_status", lambda _: None)(msg)
