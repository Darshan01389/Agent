"""Store voice-triggered reminders locally."""

from __future__ import annotations

import json
from datetime import datetime

from agents.base import AgentResult, BaseAgent, register
from config import DATA_DIR, REMINDERS_FILE


class ReminderAgent(BaseAgent):
    name = "reminder"
    triggers = ["remind me", "set reminder", "set alarm", "remember to"]

    def handle(self, text: str, history: list[dict]) -> AgentResult:
        content = text
        for trigger in self.triggers:
            if trigger in content.lower():
                idx = content.lower().index(trigger)
                content = content[idx + len(trigger):].strip(" :,.")
                break

        if not content:
            content = text

        DATA_DIR.mkdir(parents=True, exist_ok=True)
        reminders: list[dict] = []
        if REMINDERS_FILE.exists():
            reminders = json.loads(REMINDERS_FILE.read_text(encoding="utf-8"))

        entry = {
            "text": content,
            "created_at": datetime.now().isoformat(),
            "done": False,
        }
        reminders.append(entry)
        REMINDERS_FILE.write_text(
            json.dumps(reminders, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        reply = f"Reminder set: {content[:80]}{'…' if len(content) > 80 else ''}"
        return AgentResult(
            transcript=text,
            agent_name=self.name,
            action_result=reply,
            speak_text=reply,
        )


register(ReminderAgent())
