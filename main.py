import argparse
import random
import sys

from dotenv import load_dotenv
from rich import box
from rich.console import Group
from rich.panel import Panel
from rich.text import Text

from config import Settings, load_settings
from core.character_creation import random_character
from core.game_manager import GameManager
from core.narrator import Narrator, OfflineNarrator
from core.persistence import SaveError, SaveStore
from ui.art import LOGO
from ui.character_wizard import create_character
from ui.console import Console
from ui.screen import Screen
from utils.dice import Dice


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Play a D&D 5e-inspired adventure run by an AI Dungeon Master."
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="use the built-in narrator instead of the OpenAI API",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="skip character creation and play a random hero",
    )
    parser.add_argument("--load", metavar="NAME", help="continue a saved game")
    parser.add_argument(
        "--seed", type=int, help="seed the world and dice for a reproducible run"
    )
    parser.add_argument("--model", help="OpenAI model name (overrides DND_MODEL)")
    return parser.parse_args(argv)


def build_narrator(
    settings: Settings, args: argparse.Namespace, rng: random.Random, console: Console
) -> Narrator:
    if args.offline:
        return OfflineNarrator(rng)
    if not settings.openai_api_key:
        console.warn("OPENAI_API_KEY is not set: using the offline narrator.")
        return OfflineNarrator(rng)
    from core.openai_narrator import OpenAINarrator

    return OpenAINarrator(
        api_key=settings.openai_api_key,
        model=args.model or settings.model,
        history_turns=settings.history_turns,
        fallback=OfflineNarrator(rng),
        on_error=lambda error: console.warn(
            f"AI narrator unavailable ({error}). Using offline narration."
        ),
    )


def start_game(
    args: argparse.Namespace,
    console: Console,
    narrator: Narrator,
    rng: random.Random,
    saves: SaveStore,
) -> GameManager:
    if args.load:
        return GameManager.from_save(saves, args.load, narrator, rng)
    player = (
        random_character(rng) if args.quick else create_character(console, Dice(rng))
    )
    return GameManager.new_game(player, narrator, rng, saves)


def show_title(console: Console) -> None:
    console.render(
        Panel(
            Group(
                Text(LOGO.strip("\n"), style="bold yellow"),
                Text(
                    "A Dungeons & Dragons adventure in your terminal",
                    style="italic grey70",
                    justify="center",
                ),
            ),
            box=box.DOUBLE,
            border_style="yellow",
        )
    )


def play(console: Console, game: GameManager) -> list[str]:
    screen = Screen(console, game)
    with console.full_screen():
        screen.show(game.opening())
        while True:
            command = screen.ask()
            lines = game.handle(command)
            if not game.running:
                return lines
            screen.show(lines, command)


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    args = parse_args(argv)
    settings = load_settings()
    seed = args.seed if args.seed is not None else settings.seed
    rng = random.Random(seed)
    console = Console()
    narrator = build_narrator(settings, args, rng, console)
    saves = SaveStore(settings.save_dir)
    show_title(console)
    try:
        game = start_game(args, console, narrator, rng, saves)
        console.show(play(console, game))
    except SaveError as error:
        console.warn(str(error))
        return 1
    except (KeyboardInterrupt, EOFError):
        console.show(["", "Farewell, adventurer."])
    return 0


if __name__ == "__main__":
    sys.exit(main())
