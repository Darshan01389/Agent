"""General conversational agent using Nemotron LLM."""

from __future__ import annotations

from agents.base import AgentResult, BaseAgent, register
from nvidia.llm_client import chat


class ChatAgent(BaseAgent):
    name = "chat"
    triggers: list[str] = []

    def matches(self, text: str) -> bool:
        return True  # default fallback

    def handle(self, text: str, history: list[dict]) -> AgentResult:
        history = history + [{"role": "user", "content": text}]
        result = chat(history)
        reply = result["text"] or "Sorry, I couldn't generate a response."
        if result["error"]:
            reply = f"Error: {result['error']}"
        return AgentResult(
            transcript=text,
            agent_name=self.name,
            action_result=reply,
            speak_text=reply if not result["error"] else "",
            history_entry={"role": "assistant", "content": reply},
        )


register(ChatAgent())
