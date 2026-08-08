"""
base.py
-------
Agent protocol, registry, and intent router.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class AgentResult:
    transcript: str
    agent_name: str
    action_result: str = ""
    speak_text: str = ""
    history_entry: dict = field(default_factory=dict)


class Agent(Protocol):
    name: str
    triggers: list[str]

    def matches(self, text: str) -> bool: ...
    def handle(self, text: str, history: list[dict]) -> AgentResult: ...


class BaseAgent:
    name = "base"
    triggers: list[str] = []

    def matches(self, text: str) -> bool:
        lower = text.lower()
        return any(t in lower for t in self.triggers)

    def handle(self, text: str, history: list[dict]) -> AgentResult:
        raise NotImplementedError


# Keyword routing rules (checked before default agent)
ROUTING_RULES: list[tuple[list[str], str]] = [
    (["take note", "write down", "note that", "save note"], "note"),
    (["remind me", "set reminder", "set alarm", "remember to"], "reminder"),
]

_registry: dict[str, Agent] = {}


def register(agent: Agent):
    _registry[agent.name] = agent


def get_agent(name: str) -> Agent | None:
    return _registry.get(name)


def route(text: str) -> str:
    """Return agent name for the given transcript."""
    lower = text.lower()
    for triggers, agent_name in ROUTING_RULES:
        if any(t in lower for t in triggers):
            return agent_name
    return "chat"


def dispatch(text: str, history: list[dict]) -> AgentResult:
    agent_name = route(text)
    agent = _registry.get(agent_name) or _registry.get("chat")
    if agent is None:
        raise RuntimeError("No agents registered")
    return agent.handle(text, history)
