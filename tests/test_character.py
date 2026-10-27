from core.character_creation import assign_scores, build_character
from models.character import Character


def test_build_character_applies_race_bonuses_and_priorities():
    hero = build_character("Bruna", "dwarf", "fighter")
    assert hero.abilities["strength"] == 15
    assert hero.abilities["constitution"] == 16
    assert hero.max_hp == hero.hp == 10 + 3
    assert hero.feature_uses == 1


def test_assign_scores_follows_class_priorities():
    scores = assign_scores([8, 15, 10, 14, 12, 13], "wizard")
    assert scores["intelligence"] == 15
    assert scores["strength"] == 8


def test_heavy_armor_ignores_dexterity_and_light_armor_uses_it():
    assert build_character("A", "elf", "fighter").armor_class == 16
    rogue = build_character("B", "elf", "rogue")
    assert rogue.armor_class == 11 + rogue.modifier("dexterity")


def test_finesse_weapon_uses_best_of_strength_and_dexterity():
    rogue = build_character("C", "halfling", "rogue")
    assert rogue.attack_ability == "dexterity"
    assert rogue.damage == "1d6+3"


def test_skill_bonus_includes_proficiency_only_for_class_skills():
    rogue = build_character("D", "human", "rogue")
    dex = rogue.modifier("dexterity")
    assert rogue.skill_bonus("stealth") == dex + 2
    assert rogue.skill_bonus("athletics") == rogue.modifier("strength")


def test_gain_xp_levels_up_and_raises_hp():
    hero = build_character("E", "human", "fighter")
    before = hero.max_hp
    assert hero.gain_xp(900) == [2, 3]
    assert hero.level == 3
    assert hero.max_hp == before + 2 * (6 + hero.modifier("constitution"))


def test_damage_and_healing_are_clamped():
    hero = build_character("F", "human", "cleric")
    assert hero.take_damage(999) == hero.max_hp
    assert hero.hp == 0 and not hero.is_alive
    assert hero.heal(999) == hero.max_hp


def test_inventory_add_and_remove():
    hero = build_character("G", "human", "wizard")
    hero.add_item("rope", 2)
    assert hero.remove_item("rope", 2)
    assert "rope" not in hero.inventory
    assert not hero.remove_item("rope")


def test_round_trip_serialization():
    hero = build_character("H", "half-orc", "fighter")
    assert Character.from_dict(hero.to_dict()) == hero
