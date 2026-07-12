"""
Templates and Procedural Content Generators for the Dark Labyrinth.
Provides items, monsters, room descriptions, and riddles.
"""

import random
from typing import Dict, List, Any

# Riddles database for locked chests and doors
RIDDLES: List[Dict[str, Any]] = [
    {
        "question": "I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?",
        "answer": "echo"
    },
    {
        "question": "The more of them you take, the more you leave behind. What are they?",
        "answer": "footsteps"
    },
    {
        "question": "I have keys but no locks. I have space but no room. You can enter but can't go outside. What am I?",
        "answer": "keyboard"
    },
    {
        "question": "What is always in front of you but cannot be seen?",
        "answer": "future"
    },
    {
        "question": "I am simple, pointing to nothing; yet I guide men through the dark. The more I stand, the shorter I grow. What am I?",
        "answer": "candle"
    },
    {
        "question": "I can run but cannot walk, have a mouth but cannot talk, have a bed but cannot sleep. What am I?",
        "answer": "river"
    },
    {
        "question": "If you feed me I live, but if you give me water I die. What am I?",
        "answer": "fire"
    },
    {
        "question": "A box without hinges, key, or lid, yet golden treasure inside is hid. What is it?",
        "answer": "egg"
    }
]

# Items pool (type, name, stat modifier / usage)
ITEMS: List[Dict[str, Any]] = [
    {"name": "Rusty Iron Sword", "type": "weapon", "atk": 5, "def": 0, "desc": "A chipped iron blade. Heavy but effective."},
    {"name": "Dagger of Shadows", "type": "weapon", "atk": 8, "def": 0, "desc": "A serrated dagger that drinks the light."},
    {"name": "Paladin's Bastard Sword", "type": "weapon", "atk": 15, "def": 2, "desc": "A pristine blade engraved with holy runes."},
    
    {"name": "Rattered Leather Jerkin", "type": "armor", "atk": 0, "def": 2, "desc": "Old leather, smelly but slightly protective."},
    {"name": "Chainmail Vest", "type": "armor", "atk": 0, "def": 5, "desc": "Linked rings of rusted iron."},
    {"name": "Gilded Plate Mail", "type": "armor", "atk": -1, "def": 12, "desc": "Heavy plate armor of a forgotten champion. Reduces speed slightly (+11 net efficiency)."},

    {"name": "Minor Health Potion", "type": "potion", "hp": 25, "desc": "A small vial filled with glowing red liquid. Restores 25 HP."},
    {"name": "Elixir of Vigor", "type": "potion", "hp": 60, "desc": "A thick, golden brew. Restores 60 HP."},
    {"name": "Draught of Rebirth", "type": "potion", "hp": 150, "desc": "Shimmering rainbow fluid. Fully heals your wounds."},

    {"name": "Scroll of Healing", "type": "scroll", "effect": "heal_full", "desc": "A weathered parchment that hums with life-force when read."},
    {"name": "Scroll of Banishing", "type": "scroll", "effect": "kill_monster", "desc": "Contains a sigil of bright light that can instantly destroy a normal monster."},
]

# Key definitions
KEYS: List[Dict[str, Any]] = [
    {"name": "Rusted Key", "type": "key", "desc": "An old iron key, brown with rust. Matches common wooden doors."},
    {"name": "Skeleton Key", "type": "key", "desc": "A bone-carved key with shifting teeth. Matches skeletal locks."},
    {"name": "Crimson Key", "type": "key", "desc": "A blood-stained key made of red crystal. Matches ritual locks."},
    {"name": "Abyssal Key", "type": "key", "desc": "A cold, black key that feels heavy. Matches heavy shadow gates."},
]

# Monsters pool (name, hp, atk, def, xp, gold)
MONSTERS: List[Dict[str, Any]] = [
    {"name": "Flesh Crawler", "hp": 15, "atk": 4, "def": 1, "xp": 10, "gold": 5, "desc": "A multi-legged creature made of writhing muscle tissue."},
    {"name": "Skeletal Sentry", "hp": 25, "atk": 6, "def": 2, "xp": 20, "gold": 12, "desc": "A reanimated skeleton wielding a rusted spear."},
    {"name": "Shadow Fiend", "hp": 40, "atk": 10, "def": 3, "xp": 45, "gold": 25, "desc": "A spectral entity that shifts inside the darkness."},
    {"name": "Plague Rat Swarm", "hp": 18, "atk": 5, "def": 0, "xp": 15, "gold": 3, "desc": "Dozens of red-eyed rats carrying infectious rot."},
    {"name": "Ritual Cultist", "hp": 30, "atk": 8, "def": 2, "xp": 30, "gold": 18, "desc": "A hooded figure reciting curses over bloodstains."},
    {"name": "Labyrinth Minotaur", "hp": 80, "atk": 16, "def": 6, "xp": 120, "gold": 80, "desc": "A hulking, horn-headed beast that guards the deep sectors."},
]


def generate_room_description(room_name: str, bank: Dict[str, List[str]]) -> str:
    """Generate a descriptive flavor text for the room."""
    structures = bank.get("structures", ["chamber"])
    descriptors = bank.get("descriptors", ["dark"])
    atmosphere = bank.get("atmosphere", ["silent"])
    lore = bank.get("lore", ["unknown history"])

    struct = random.choice(structures).capitalize()
    desc = random.choice(descriptors)
    atmos = random.choice(atmosphere)
    lr = random.choice(lore).replace("_", " ")

    templates = [
        f"{struct} of {desc} design. The air is {atmos} and heavy with the smell of old dust. Legends speak of the {lr} here.",
        f"A {desc} {struct.lower()}. You notice the area is {atmos}. A chill runs down your spine as you recall the whispers of the {lr}.",
        f"This {struct.lower()} feels deeply {desc}. The environment is {atmos}. It stands as a silent testament to {lr}.",
        f"Before you lies a {desc} {struct.lower()}. A {atmos} draft sweeps through. This was once the resting place of {lr}."
    ]

    return random.choice(templates)


def spawn_loot(depth: int) -> Dict[str, Any]:
    """Decide what loot to spawn based on dungeon depth."""
    # Spawn rates: 35% nothing, 30% potion, 15% key, 10% weapon, 10% armor/scroll
    roll = random.random()
    if roll < 0.35:
        return {}
    elif roll < 0.65:
        # Potion
        return random.choice([it for it in ITEMS if it["type"] == "potion"])
    elif roll < 0.80:
        # Key
        return random.choice(KEYS)
    elif roll < 0.90:
        # Weapon
        weapons = [it for it in ITEMS if it["type"] == "weapon"]
        # Scale weapon power slightly with depth
        if depth < 3:
            return weapons[0]  # Rusty Iron Sword
        elif depth < 5:
            return weapons[1]  # Dagger of Shadows
        else:
            return weapons[2]  # Paladin's Bastard Sword
    else:
        # Armor or Scroll
        others = [it for it in ITEMS if it["type"] in ("armor", "scroll")]
        return random.choice(others)


def spawn_monster(depth: int) -> Dict[str, Any]:
    """Spawn a monster scaled appropriately with depth."""
    # 40% chance of no monster on shallow levels, 20% on deep levels
    no_monster_chance = 0.40 if depth < 3 else 0.20
    if random.random() < no_monster_chance:
        return {}

    # Select candidate monsters
    if depth < 2:
        candidates = [m for m in MONSTERS if m["hp"] <= 25]
    elif depth < 4:
        candidates = [m for m in MONSTERS if m["hp"] <= 40]
    else:
        candidates = MONSTERS

    monster_base = random.choice(candidates)
    
    # Scale stats slightly based on depth
    multiplier = 1.0 + (depth * 0.1)
    monster = monster_base.copy()
    monster["hp"] = int(monster["hp"] * multiplier)
    monster["max_hp"] = monster["hp"]
    monster["atk"] = int(monster["atk"] * multiplier)
    monster["def"] = int(monster["def"] * multiplier)
    monster["xp"] = int(monster["xp"] * multiplier)
    monster["gold"] = int(monster["gold"] * multiplier)

    return monster
