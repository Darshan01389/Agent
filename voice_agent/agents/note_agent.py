"""Save notes triggered by voice commands."""

from __future__ import annotations

from datetime import datetime

from agents.base import AgentResult, BaseAgent, register
from config import DATA_DIR, NOTES_FILE


class NoteAgent(BaseAgent):
    name = "note"
    triggers = ["take note", "write down", "note that", "save note"]

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
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = f"\n## {timestamp}\n{content}\n"
        with open(NOTES_FILE, "a", encoding="utf-8") as f:
            f.write(entry)

        reply = f"Note saved: {content[:80]}{'…' if len(content) > 80 else ''}"
        return AgentResult(
            transcript=text,
            agent_name=self.name,
            action_result=reply,
            speak_text=reply,
        )


register(NoteAgent())
