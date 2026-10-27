from dataclasses import dataclass

ALIASES = {
    "help": "help",
    "?": "help",
    "look": "look",
    "l": "look",
    "go": "go",
    "move": "go",
    "travel": "go",
    "walk": "go",
    "map": "map",
    "exits": "map",
    "explore": "explore",
    "talk": "talk",
    "speak": "talk",
    "ask": "talk",
    "attack": "attack",
    "hit": "attack",
    "fight": "attack",
    "dodge": "dodge",
    "flee": "flee",
    "run": "flee",
    "use": "use",
    "drink": "use",
    "ability": "ability",
    "special": "ability",
    "cast": "ability",
    "rest": "rest",
    "sleep": "rest",
    "camp": "rest",
    "shop": "shop",
    "buy": "buy",
    "inventory": "inventory",
    "inv": "inventory",
    "i": "inventory",
    "stats": "stats",
    "sheet": "stats",
    "character": "stats",
    "quests": "quests",
    "journal": "quests",
    "check": "check",
    "roll": "roll",
    "save": "save",
    "load": "load",
    "quit": "quit",
    "exit": "quit",
}

FILLER_WORDS = {"to", "with", "the", "at", "into", "towards", "a", "an"}

COMBAT_VERBS = {
    "attack",
    "dodge",
    "flee",
    "use",
    "ability",
    "look",
    "stats",
    "inventory",
    "roll",
    "help",
    "quit",
}

HELP = (
    ("look", "Describe where you are, who is here and where paths lead."),
    ("go <place>", "Travel to a connected place (2 hours)."),
    ("map", "Show the places you know and how they connect."),
    ("explore", "Search the area for loot, secrets or trouble (1 hour)."),
    (
        "talk <person> [message]",
        "Speak with someone here, e.g. 'talk elder about the ruins'.",
    ),
    (
        "<anything else>",
        "Describe an action in your own words; the DM may call for a skill check.",
    ),
    ("attack [enemy]", "Attack in combat with your weapon."),
    (
        "dodge",
        "In combat, impose disadvantage on attacks against you until your next turn.",
    ),
    ("flee", "In combat, try to escape (Acrobatics check)."),
    ("use <item>", "Drink a healing potion."),
    ("ability [enemy]", "Use your class feature."),
    ("rest", "Long rest for 8 hours. Uses rations outside settlements."),
    ("shop / buy [quantity] <item>", "Trade with a merchant."),
    ("inventory, stats, quests", "Show your pack, character sheet or quest journal."),
    ("check <skill>", "Roll a skill check yourself, e.g. 'check perception'."),
    ("roll <dice>", "Roll dice, e.g. 'roll 2d6+3' or 'roll 4d6kh3'."),
    (
        "save [name] / load [name]",
        "Save or load a game (default name: your character).",
    ),
    ("quit", "Autosave and leave the game."),
)


@dataclass(frozen=True)
class Command:
    verb: str
    args: str
    raw: str


def parse(text: str) -> Command:
    raw = text.strip()
    words = raw.split()
    if not words:
        return Command("", "", "")
    verb = ALIASES.get(words[0].lower())
    if verb is None:
        return Command("do", raw, raw)
    rest = words[1:]
    while rest and rest[0].lower() in FILLER_WORDS:
        rest = rest[1:]
    return Command(verb, " ".join(rest), raw)
