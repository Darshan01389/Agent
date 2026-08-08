"""Voice Agent entry point."""

import flet as ft

from ui.app import build_app


def main(page: ft.Page):
    build_app(page)


if __name__ == "__main__":
    ft.app(target=main)
