"""
Themes and Semantic Word Banks for Dark Labyrinth RPG.
Contains extensive dark fantasy keywords, connectors, templates, and resolution logic.
"""

import random
from typing import List, Dict, Tuple, Set

# Extended templates for folder name generation
THEME_TEMPLATES: List[str] = [
    "{adj}_{root}",
    "{root}_of_{lore}",
    "{root}_{structure}",
    "the_{numeral}_{root}",
    "{structure}_of_{root}",
    "beneath_the_{root}",
    "within_the_{adj}_{structure}",
    "{root}_layer_{numeral}",
    "the_{adj}_{structure}_of_{lore}",
]

NUMERALS: List[str] = [
    "first", "second", "third", "fourth", "fifth", "sixth", "seventh",
    "eighth", "ninth", "tenth", "last", "uppermost", "lowest", "deepest",
    "outermost", "alpha", "omega", "prime", "final",
]

# Combined rich semantic banks from both scaffolds
SEMANTIC_BANKS: Dict[str, Dict[str, List[str]]] = {
    "dungeon": {
        "roots": ["dungeon", "pit", "oubliette", "cellblock", "vault", "crypt", "cell", "warden", "keep"],
        "descriptors": ["forsaken", "rotting", "fetid", "lightless", "dripping", "collapsed", "wretched", "cruel"],
        "structures": ["corridor", "chamber", "shaft", "passage", "tunnel", "alcove", "rack", "sewer"],
        "atmosphere": ["echoing", "stinking", "bone-strewn", "waterlogged", "fungal", "rat-infested", "silent"],
        "lore": ["forgotten", "condemned", "lost", "buried", "sealed", "dead", "unclean"],
    },
    "castle": {
        "roots": ["bastion", "fortress", "citadel", "stronghold", "keep", "tower", "rampart", "gatehouse", "barbican"],
        "descriptors": ["crumbling", "accursed", "siege-scarred", "blighted", "ironclad", "gaunt", "fell", "dire"],
        "structures": ["battlement", "parapet", "portcullis", "moat", "bridge", "hall", "observatory", "watch"],
        "atmosphere": ["wind-scoured", "ash-dusted", "blood-soaked", "fog-shrouded", "raven-haunted", "cold"],
        "lore": ["fallen_king", "dread_iron", "last_siege", "broken_oaths", "lost_empire"],
    },
    "city": {
        "roots": ["ward", "quarter", "district", "borough", "slum", "undercity", "shantytown", "plaza", "market"],
        "descriptors": ["plague-ridden", "desolate", "overcrowded", "soot-blackened", "crime-ridden", "wretched"],
        "structures": ["alley", "crossroads", "square", "den", "tenement", "sewers", "spire"],
        "atmosphere": ["torch-lit", "smog-choked", "corpse-strewn", "rain-lashed", "famine-struck", "screaming"],
        "lore": ["the_desperate", "the_undying", "seven_sins", "broken_chains", "broken_dreams"],
    },
    "hell": {
        "roots": ["abyss", "inferno", "purgatory", "gehenna", "tartarus", "malebolge", "cocytus", "layer", "pit"],
        "descriptors": ["searing", "eternal", "writhing", "sulfurous", "screaming", "bottomless", "burning", "damned"],
        "structures": ["circle", "layer", "plane", "chasm", "rift", "maw", "throne", "lake"],
        "atmosphere": ["fire-scorched", "soul-torn", "demon-patrolled", "ash-filled", "torment-laced", "howling"],
        "lore": ["damned_souls", "wailing_dead", "endless_fire", "eighth_sin", "broken_spirits"],
    },
    "labyrinth": {
        "roots": ["maze", "labyrinth", "web", "tangle", "warren", "catacomb", "necropolis", "spiral"],
        "descriptors": ["endless", "shifting", "cursed", "unknowable", "spiraling", "ancient", "hollow"],
        "structures": ["dead_end", "junction", "spiral", "crossing", "threshold", "nexus", "archive", "shaft"],
        "atmosphere": ["echo-filled", "trap-laden", "mind-breaking", "fog-thick", "minotaur-stalked"],
        "lore": ["no_return", "the_architect", "lost_reason", "final_turn", "stolen_light"],
    },
    "plague": {
        "roots": ["pestilence", "blight", "miasma", "rot", "corruption", "wasting", "necrosis", "pustule", "canker"],
        "descriptors": ["festering", "gangrenous", "pox-marked", "blackened", "weeping", "hollow", "blighted"],
        "structures": ["charnel_house", "mass_grave", "quarantine", "lazar_house", "ossuary", "garden", "feast"],
        "atmosphere": ["stench-soaked", "fly-blown", "death-touched", "fever-dreamed", "plague-sealed", "stagnant"],
        "lore": ["black_death", "rat_king", "gods_abandonment", "the_unclean", "withered_flesh"],
    },
    "shadows": {
        "roots": ["shadow", "darkness", "void", "oblivion", "night", "eclipse", "penumbra", "veil", "wraith", "shroud"],
        "descriptors": ["impenetrable", "creeping", "hungry", "whispering", "consuming", "absolute", "black", "umbral"],
        "structures": ["sanctum", "hollow", "lair", "den", "refuge", "shrine", "walk", "cloister"],
        "atmosphere": ["starless", "moonless", "candleless", "blinding", "soul-draining", "cold", "silent"],
        "lore": ["the_unseen", "dark_god", "stolen_light", "blind_prophet", "broken_shroud"],
    },
    "war": {
        "roots": ["battlefield", "warfront", "siege", "conquest", "massacre", "ruin", "carnage", "wreck"],
        "descriptors": ["ravaged", "scorched", "blood-drenched", "abandoned", "smoldering", "razed", "cruel"],
        "structures": ["trench", "rampart", "palisade", "watchtower", "camp", "graveyard"],
        "atmosphere": ["crow-circled", "arrow-riddled", "ash-choked", "mud-soaked", "death-silent", "screaming"],
        "lore": ["last_stand", "thousand_dead", "no_victors", "the_iron_god", "broken_shields"],
    },
    "ritual": {
        "roots": ["altar", "sanctum", "reliquary", "sepulcher", "shrine", "monolith", "circle", "temple", "chapel"],
        "descriptors": ["bloodstained", "forbidden", "ancient", "profane", "eldritch", "cursed", "hallowed"],
        "structures": ["inner_chamber", "antechamber", "sacrificial_pit", "nave", "cloister", "scriptorium"],
        "atmosphere": ["candle-lit", "incense-heavy", "blood-reeking", "chant-haunted", "god-touched", "whispering"],
        "lore": ["old_faith", "dark_pact", "summoning", "last_rite", "broken_seals"],
    },
    "swamp": {
        "roots": ["bog", "mire", "fen", "quagmire", "marsh", "morass", "slough", "sinkhole"],
        "descriptors": ["stagnant", "toxic", "suffocating", "sucking", "foul", "diseased", "murky"],
        "structures": ["islet", "causeway", "sunken_ruin", "hut", "reed_bed"],
        "atmosphere": ["fog-drenched", "leech-filled", "will-o-wisp-lit", "croaking", "drowning"],
        "lore": ["drowned_king", "the_hag", "forgotten_roads", "dead_armies", "sunken_crown"],
    },
    "blood": {
        "roots": ["blood", "veins", "chalice", "river", "fountain", "pool", "stain", "drip"],
        "descriptors": ["crimson", "sanguine", "clotted", "warm", "fresh", "pulsing", "cursed"],
        "structures": ["altar", "pit", "well", "chasm", "fountain", "basin"],
        "atmosphere": ["metallic", "coagulated", "dripping", "warm", "stench-heavy"],
        "lore": ["vampire_lord", "bloody_sacrifice", "endless_lineage", "red_curse"],
    },
    "iron": {
        "roots": ["iron", "spikes", "chains", "maiden", "cage", "bars", "shackles", "nails", "collar"],
        "descriptors": ["rusted", "cold", "heavy", "forged", "brutal", "blackened", "unyielding"],
        "structures": ["gate", "throne", "rack", "grate", "keep", "door"],
        "atmosphere": ["metallic", "clanking", "cold", "dusty", "gloomy"],
        "lore": ["iron_maidens", "chained_sinners", "the_forge_masters", "eternal_binding"],
    },
    "bone": {
        "roots": ["bone", "skeleton", "skull", "marrow", "ribcage", "spine"],
        "descriptors": ["bleached", "brittle", "calcified", "ancient", "splintered", "dusty"],
        "structures": ["cathedral", "crypt", "yard", "pile", "arch", "throne", "ossuary", "reliquary", "shrine"],
        "atmosphere": ["dry", "bone-strewn", "silent", "drafty", "echoing"],
        "lore": ["bone_collector", "skeletal_legions", "first_necromancer", "broken_ribs"],
    }
}

KEYWORD_MAP: Dict[str, str] = {
    # Dungeon-like
    "dungeon": "dungeon", "prison": "dungeon", "jail": "dungeon", "cell": "dungeon",
    "pit": "dungeon", "vault": "dungeon", "crypt": "dungeon", "cave": "dungeon",
    "cavern": "dungeon", "underground": "dungeon", "subterranean": "dungeon",
    # Castle-like
    "castle": "castle", "fortress": "castle", "keep": "castle", "tower": "castle",
    "citadel": "castle", "stronghold": "castle", "bastion": "castle", "fort": "castle",
    "walls": "castle", "battlements": "castle",
    # City-like
    "city": "city", "town": "city", "village": "city", "district": "city",
    "quarter": "city", "slum": "city", "streets": "city", "alley": "city",
    "market": "city", "settlement": "city", "outpost": "city",
    # Hell-like
    "hell": "hell", "inferno": "hell", "abyss": "hell", "demon": "hell",
    "devil": "hell", "fire": "hell", "damnation": "hell", "underworld": "hell",
    "hades": "hell", "tartarus": "hell", "gehenna": "hell", "purgatory": "hell",
    # Labyrinth-like
    "labyrinth": "labyrinth", "maze": "labyrinth", "catacomb": "labyrinth",
    "warren": "labyrinth", "tangle": "labyrinth", "web": "labyrinth",
    "minotaur": "labyrinth", "daedalus": "labyrinth",
    # Plague-like
    "plague": "plague", "disease": "plague", "pestilence": "plague", "rot": "plague",
    "blight": "plague", "corruption": "plague", "undead": "plague", "zombie": "plague",
    "necromancy": "plague",
    # Shadow-like
    "shadow": "shadows", "dark": "shadows", "darkness": "shadows", "void": "shadows",
    "night": "shadows", "shade": "shadows", "eclipse": "shadows", "ghost": "shadows",
    "specter": "shadows",
    # War-like
    "war": "war", "battle": "war", "combat": "war", "massacre": "war",
    "conquest": "war", "ruin": "war", "carnage": "war", "bloodshed": "war",
    "army": "war", "siege": "war",
    # Ritual-like
    "ritual": "ritual", "altar": "ritual", "sacrifice": "ritual", "cult": "ritual",
    "occult": "ritual", "magic": "ritual", "summoning": "ritual", "curse": "ritual",
    "hex": "ritual", "temple": "ritual",
    # Swamp-like
    "swamp": "swamp", "bog": "swamp", "marsh": "swamp", "mire": "swamp",
    "fen": "swamp", "swampland": "swamp", "hag": "swamp", "witch": "swamp",
    # Blood-like
    "blood": "blood", "vein": "blood", "chalice": "blood", "river": "blood",
    "fountain": "blood", "vampire": "blood",
    # Iron-like
    "iron": "iron", "chain": "iron", "cage": "iron", "rusted": "iron",
    "spike": "iron", "shackle": "iron",
    # Bone-like
    "bone": "bone", "skeleton": "bone", "skull": "bone", "ossuary": "bone",
}


def resolve_single_theme(keyword: str) -> Tuple[Dict[str, List[str]], str]:
    """Resolve a single keyword to a semantic bank, with fuzzy fallback."""
    keyword_lower = keyword.lower().strip()

    # Direct match
    if keyword_lower in KEYWORD_MAP:
        bank_name = KEYWORD_MAP[keyword_lower]
        return SEMANTIC_BANKS[bank_name], bank_name

    # Partial match scan
    for key, bank_name in KEYWORD_MAP.items():
        if key in keyword_lower or keyword_lower in key:
            return SEMANTIC_BANKS[bank_name], bank_name

    # Fuzzy match on banks
    for bank_name in SEMANTIC_BANKS:
        if bank_name in keyword_lower:
            return SEMANTIC_BANKS[bank_name], bank_name

    # Default to labyrinth
    return SEMANTIC_BANKS["labyrinth"], "labyrinth"


def merge_themes(keywords: List[str]) -> Tuple[Dict[str, List[str]], str]:
    """Merge multiple keywords' semantic banks together."""
    if not keywords:
        keywords = ["labyrinth"]

    resolved_banks = []
    names = []

    for kw in keywords:
        bank, name = resolve_single_theme(kw)
        resolved_banks.append(bank)
        names.append(name)

    merged = {
        "roots": [],
        "descriptors": [],
        "structures": [],
        "atmosphere": [],
        "lore": []
    }

    for b in resolved_banks:
        for k in merged:
            merged[k].extend(b.get(k, []))

    # Deduplicate lists
    for k in merged:
        merged[k] = list(sorted(set(merged[k])))

    return merged, "+".join(sorted(set(names)))


def sanitize_name(name: str) -> str:
    """Sanitize directory names for general filesystem compatibility."""
    name = name.lower()
    name = name.replace(" ", "_")
    name = name.replace("/", "-")
    name = name.replace("\\", "-")
    safe = ""
    for ch in name:
        if ch.isalnum() or ch in "_-":
            safe += ch
    while "__" in safe:
        safe = safe.replace("__", "_")
    return safe.strip("_")


def generate_room_name(bank: Dict[str, List[str]], used_names: Set[str], depth_hint: int = 0) -> str:
    """Procedurally generate a room name from a semantic bank."""
    attempts = 0
    while attempts < 50:
        template = random.choice(THEME_TEMPLATES)
        
        root = random.choice(bank["roots"])
        adj = random.choice(bank["descriptors"])
        structure = random.choice(bank["structures"])
        atmos = random.choice(bank["atmosphere"])
        lore = random.choice(bank["lore"])
        numeral = random.choice(NUMERALS)

        formatted = template.format(
            root=root,
            adj=adj,
            structure=structure,
            atmos=atmos,
            lore=lore,
            numeral=numeral
        )
        sanitized = sanitize_name(formatted)

        if sanitized not in used_names:
            used_names.add(sanitized)
            return sanitized
        attempts += 1

    # Fallback
    fallback = f"chamber_{random.randint(100, 999)}"
    used_names.add(fallback)
    return fallback
