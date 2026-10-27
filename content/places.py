from dataclasses import dataclass


@dataclass(frozen=True)
class LocationKind:
    names: tuple[str, ...]
    descriptions: tuple[str, ...]
    danger: int
    encounters: tuple[str, ...]
    occupations: tuple[str, ...]
    safe: bool = False


LOCATION_KINDS = {
    "village": LocationKind(
        names=("Oakvale", "Millbrook", "Thornwick", "Ashford", "Brindlemere"),
        descriptions=(
            "Thatched cottages cluster around a stone well, and smoke curls from the chimney of a busy inn.",
            "A palisade of sharpened logs rings a quiet farming hamlet of muddy lanes and barking dogs.",
        ),
        danger=0,
        encounters=(),
        occupations=("elder", "merchant", "innkeeper"),
        safe=True,
    ),
    "crossroads": LocationKind(
        names=("Kingsroad Crossing", "The Weeping Signpost", "Hollow Fork"),
        descriptions=(
            "Four rutted roads meet beneath a leaning signpost, its arrows long since scratched illegible.",
            "A wayside shrine marks where the trade roads cross; fresh cart tracks lead in every direction.",
        ),
        danger=1,
        encounters=("bandit", "wolf"),
        occupations=("traveler",),
    ),
    "forest": LocationKind(
        names=("Whisperwood", "The Briar Thicket", "Elderglade"),
        descriptions=(
            "Ancient oaks crowd the path, their canopy so thick the light turns green and dim.",
            "Brambles snag at your cloak as birdsong falls suddenly, uneasily silent.",
        ),
        danger=1,
        encounters=("wolf", "giant rat", "bandit"),
        occupations=("hunter",),
    ),
    "ruins": LocationKind(
        names=("Fallen Chapel of Varn", "The Shattered Abbey", "Old Watchpost"),
        descriptions=(
            "Broken columns jut from the earth like ribs, and a cold draft rises from a collapsed crypt.",
            "Moss swallows the carvings on toppled walls; something has disturbed the old graves.",
        ),
        danger=2,
        encounters=("skeleton", "goblin"),
        occupations=("scholar",),
    ),
    "swamp": LocationKind(
        names=("Mirefen", "The Drowned Mere"),
        descriptions=(
            "Black water stretches between hummocks of reed, and the air hums with biting insects.",
            "Fog clings to the bog; every step sinks ankle-deep into sucking mud.",
        ),
        danger=2,
        encounters=("giant rat", "giant spider"),
        occupations=("hermit",),
    ),
    "cave": LocationKind(
        names=("Goblin Warrens", "Echoing Grotto", "Spider Hollow"),
        descriptions=(
            "A jagged cave mouth exhales stale air; crude tally marks are scratched beside the entrance.",
            "Water drips in the darkness, and thick webs glisten deeper inside.",
        ),
        danger=2,
        encounters=("goblin", "giant spider", "orc"),
        occupations=(),
    ),
    "keep": LocationKind(
        names=("Blackstone Keep", "The Ruined Bastion"),
        descriptions=(
            "A crumbling fortress squats on the hill, banners of a forgotten lord rotting on its walls.",
            "Arrow slits stare down from cracked towers, and the gate hangs from a single hinge.",
        ),
        danger=3,
        encounters=("orc", "ogre", "bandit"),
        occupations=("prisoner",),
    ),
}

WORLD_LAYOUT = ("village", "crossroads", "forest", "ruins", "swamp", "cave", "keep")
EXTRA_PATHS = 2

RACE_NAMES = {
    "human": (
        ("Aldric", "Mara", "Tobin", "Elsbeth", "Garrick", "Wynn"),
        ("Ashdown", "Fletcher", "Holloway", "Marsh"),
    ),
    "elf": (
        ("Aelar", "Sariel", "Thamior", "Naivara", "Erevan"),
        ("Galanodel", "Liadon", "Siannodel", "Amakiir"),
    ),
    "dwarf": (
        ("Bruenor", "Helja", "Thorin", "Vistra", "Dain"),
        ("Ironfist", "Battlehammer", "Gorunn", "Holderhek"),
    ),
    "halfling": (
        ("Pip", "Rosie", "Milo", "Lavinia", "Cade"),
        ("Tealeaf", "Goodbarrel", "Underbough", "Brushgather"),
    ),
    "half-orc": (
        ("Grosh", "Baggi", "Thokk", "Volen", "Shautha"),
        ("Skullsplitter", "the Quiet", "Ironhide", "Ashborn"),
    ),
}

PERSONALITIES = (
    "gruff but fair",
    "nervous and talkative",
    "cheerful",
    "suspicious of strangers",
    "wise and patient",
    "greedy",
    "melancholic",
    "boastful",
)

WEATHER = ("clear", "overcast", "light rain", "fog", "strong wind", "drizzle")
