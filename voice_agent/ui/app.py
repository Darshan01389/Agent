"""
app.py
------
Flet UI: transcript pane, mic toggle, wake-word switch, hotkey support.
"""

from __future__ import annotations

import flet as ft

from agents.base import AgentResult
from core.orchestrator import VoiceOrchestrator

# ── Colour palette ────────────────────────────────────────
BG = "#0D0F14"
SURFACE = "#161920"
SURFACE2 = "#1E2330"
ACCENT = "#76B900"  # NVIDIA green
ACCENT2 = "#7C4DFF"
USER_BG = "#1A2744"
AI_BG = "#151D2E"
TEXT_PRI = "#E8EAF0"
TEXT_SEC = "#6B7280"
SUCCESS = "#00C853"
WARNING = "#FF6D00"


def build_app(page: ft.Page):
    page.title = "Voice Agent"
    page.bgcolor = BG
    page.window.width = 520
    page.window.height = 820
    page.window.resizable = True
    page.padding = 0
    page.theme = ft.Theme(font_family="Segoe UI")

    status_text = ft.Ref[ft.Text]()
    mic_btn = ft.Ref[ft.IconButton]()
    chat_list = ft.ListView(
        expand=True,
        spacing=8,
        padding=ft.padding.symmetric(horizontal=16, vertical=8),
        auto_scroll=True,
    )
    pulse_ring = ft.Ref[ft.Container]()
    service_chip = ft.Ref[ft.Text]()

    def set_status(msg: str):
        if status_text.current:
            status_text.current.value = msg
            page.update()

    def add_transcript_bubble(text: str, engine: str | None):
        bubble = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                "YOU",
                                size=10,
                                color=ACCENT,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    (engine or "mic").upper(),
                                    size=9,
                                    color=ACCENT,
                                ),
                                bgcolor=f"{ACCENT}22",
                                border_radius=4,
                                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                border=ft.border.all(1, ACCENT),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CONTENT_COPY,
                                icon_size=16,
                                icon_color=TEXT_SEC,
                                tooltip="Copy transcript",
                                on_click=lambda _, t=text: page.set_clipboard(t),
                            ),
                        ],
                        spacing=4,
                    ),
                    ft.Text(text, color=TEXT_PRI, size=14, selectable=True),
                ],
                spacing=4,
            ),
            bgcolor=USER_BG,
            border_radius=ft.BorderRadius(12, 12, 2, 12),
            padding=ft.padding.all(14),
            margin=ft.margin.only(left=40),
            border=ft.border.all(1, "#1E3A5F"),
        )
        chat_list.controls.append(bubble)
        page.update()

    def add_agent_bubble(result):
        agent = result.agent_name.upper()
        color_map = {
            "chat": ACCENT2,
            "note": SUCCESS,
            "reminder": WARNING,
        }
        color = color_map.get(result.agent_name, TEXT_SEC)
        if service_chip.current:
            service_chip.current.value = f"● {agent}"
            service_chip.current.color = color

        bubble = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                agent,
                                size=10,
                                color=color,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CONTENT_COPY,
                                icon_size=16,
                                icon_color=TEXT_SEC,
                                tooltip="Copy response",
                                on_click=lambda _, t=result.action_result: page.set_clipboard(t),
                            ),
                        ],
                    ),
                    ft.Text(
                        result.action_result,
                        color=TEXT_PRI,
                        size=14,
                        selectable=True,
                    ),
                ],
                spacing=4,
            ),
            bgcolor=AI_BG,
            border_radius=ft.BorderRadius(12, 12, 12, 2),
            padding=ft.padding.all(14),
            margin=ft.margin.only(right=40),
            border=ft.border.all(1, "#1E2A3F"),
        )
        chat_list.controls.append(bubble)
        page.update()

    def set_listening(active: bool):
        if pulse_ring.current:
            pulse_ring.current.bgcolor = ACCENT if active else "transparent"
            pulse_ring.current.border = ft.border.all(
                2, ACCENT if active else SURFACE2
            )
        if mic_btn.current:
            mic_btn.current.icon_color = ACCENT if active else TEXT_SEC
        page.update()

    def set_speaking(active: bool):
        if pulse_ring.current:
            pulse_ring.current.bgcolor = f"{ACCENT2}44" if active else "transparent"
        page.update()

    callbacks = {
        "on_status": set_status,
        "on_transcript": add_transcript_bubble,
        "on_agent_result": add_agent_bubble,
        "on_listening": set_listening,
        "on_speaking": set_speaking,
        "on_wake": lambda: set_status("Wake word detected!"),
    }

    orchestrator = VoiceOrchestrator(callbacks)

    def on_mic_click(_):
        orchestrator.start_listening()

    def on_clear(_):
        chat_list.controls.clear()
        orchestrator.clear_history()
        page.update()

    def on_wake_toggle(e):
        if e.control.value:
            orchestrator.start_wake_word()
        else:
            orchestrator.stop_wake_word()
            set_status("Wake word off — press Space or tap mic")

    header = ft.Container(
        content=ft.Row(
            [
                ft.Column(
                    [
                        ft.Text(
                            "VOICE AGENT",
                            size=16,
                            color=ACCENT,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            "NVIDIA BNR + Nemotron ASR + Nemotron LLM",
                            size=10,
                            color=TEXT_SEC,
                        ),
                    ],
                    spacing=2,
                    expand=True,
                ),
                ft.Text(
                    ref=service_chip,
                    value="● READY",
                    size=11,
                    color=SUCCESS,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        bgcolor=SURFACE,
        padding=ft.padding.symmetric(horizontal=20, vertical=14),
        border=ft.border.only(bottom=ft.BorderSide(1, SURFACE2)),
    )

    mic_area = ft.Container(
        content=ft.Column(
            [
                ft.Stack(
                    [
                        ft.Container(
                            ref=pulse_ring,
                            width=80,
                            height=80,
                            border_radius=40,
                            bgcolor="transparent",
                            border=ft.border.all(2, SURFACE2),
                            animate=ft.animation.Animation(400, ft.AnimationCurve.EASE_IN_OUT),
                        ),
                        ft.Container(
                            content=ft.IconButton(
                                ref=mic_btn,
                                icon=ft.Icons.MIC,
                                icon_size=28,
                                icon_color=TEXT_SEC,
                                on_click=on_mic_click,
                                tooltip="Press to speak (or press Space)",
                                style=ft.ButtonStyle(
                                    bgcolor={
                                        ft.ControlState.DEFAULT: SURFACE2,
                                        ft.ControlState.HOVERED: "#252D40",
                                    },
                                    shape=ft.CircleBorder(),
                                    padding=ft.padding.all(16),
                                ),
                            ),
                            left=5,
                            top=5,
                        ),
                    ],
                    width=80,
                    height=80,
                ),
                ft.Text(
                    ref=status_text,
                    value="Press mic or Space to speak",
                    size=12,
                    color=TEXT_SEC,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Row(
                    [
                        ft.Row(
                            [
                                ft.Text("Wake Word", size=12, color=TEXT_SEC),
                                ft.Switch(
                                    value=False,
                                    active_color=ACCENT,
                                    on_change=on_wake_toggle,
                                ),
                            ],
                            spacing=6,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_color=TEXT_SEC,
                            icon_size=20,
                            tooltip="Clear conversation",
                            on_click=on_clear,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        bgcolor=SURFACE,
        padding=ft.padding.symmetric(horizontal=20, vertical=16),
        border=ft.border.only(top=ft.BorderSide(1, SURFACE2)),
    )

    def on_keyboard(e: ft.KeyboardEvent):
        if e.key == " " and not e.shift and not e.ctrl and not e.alt:
            orchestrator.start_listening()

    page.on_keyboard_event = on_keyboard

    page.add(
        ft.Column(
            [
                header,
                ft.Container(content=chat_list, expand=True, bgcolor=BG),
                mic_area,
            ],
            expand=True,
            spacing=0,
        )
    )

    add_agent_bubble(
        AgentResult(
            transcript="",
            agent_name="chat",
            action_result=(
                "Hello! I'm your NVIDIA-powered voice agent. "
                "Tap the mic, press Space, or enable wake word to start. "
                "Try 'take note …' or 'remind me …' for task agents."
            ),
        )
    )
    set_status("Ready — tap mic or press Space to speak")
