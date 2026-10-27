from core.commands import parse


def test_alias_and_filler_words_are_normalized():
    command = parse("Travel to the Whisperwood")
    assert command.verb == "go"
    assert command.args == "Whisperwood"


def test_unknown_verbs_become_freeform_actions():
    command = parse("search the altar for runes")
    assert command.verb == "do"
    assert command.args == command.raw == "search the altar for runes"


def test_blank_input():
    assert parse("   ").verb == ""


def test_short_aliases():
    assert parse("i").verb == "inventory"
    assert parse("talk with elder about wolves").args == "elder about wolves"
