from collections.abc import Iterable
from typing import ContextManager

from rich.console import Console as RichConsole
from rich.console import RenderableType
from rich.text import Text

PREFIX_STYLES = (
    ("== ", "bold cyan"),
    ("!! ", "bold red"),
    ("*** ", "bold yellow"),
    ("[", "magenta"),
)


def styled(line: str) -> Text:
    for prefix, style in PREFIX_STYLES:
        if line.startswith(prefix):
            return Text(line, style=style)
    return Text(line)


class Console:
    def __init__(self, rich: RichConsole | None = None):
        self.rich = rich or RichConsole(highlight=False)

    def show(self, lines: Iterable[str]) -> None:
        for line in lines:
            self.rich.print(styled(line))

    def render(self, *renderables: RenderableType) -> None:
        for renderable in renderables:
            self.rich.print(renderable)

    def clear(self) -> None:
        self.rich.clear()

    def full_screen(self) -> ContextManager:
        return self.rich.screen(hide_cursor=False)

    def ask(self, prompt: str) -> str:
        return self.rich.input(Text(prompt, style="bold green"))

    def warn(self, message: str) -> None:
        self.rich.print(Text(message, style="yellow"))
