"""
Dungeon Labyrinth Builder for Dark Labyrinth RPG.
Recursively creates folder structures and populates them with room.md files and state JSONs.
"""

import os
import json
import random
from pathlib import Path
from typing import List, Dict, Any, Set

from dark_labyrinth.generator.themes import (
    merge_themes, generate_room_name, sanitize_name
)
from dark_labyrinth.generator.templates import (
    generate_room_description, spawn_loot, spawn_monster, RIDDLES
)


def create_room_files(
    room_path: Path,
    room_name: str,
    depth: int,
    theme_bank: Dict[str, List[str]],
    exits: List[str]
) -> Dict[str, Any]:
    """Create room.md and .room_data.json in the specified path."""
    desc = generate_room_description(room_name, theme_bank)
    monster = spawn_monster(depth)
    loot = spawn_loot(depth)

    # Initialize locked states for exits
    exits_data = {}
    for ex in exits:
        if ex.startswith("locked_"):
            lock_type = "riddle"
            lock_detail = ""
            key_needed = ""

            if "wood" in ex:
                lock_type = "key"
                key_needed = "Rusted Key"
            elif "skeletal" in ex:
                lock_type = "key"
                key_needed = "Skeleton Key"
            elif "crimson" in ex:
                lock_type = "key"
                key_needed = "Crimson Key"
            elif "abyssal" in ex:
                lock_type = "key"
                key_needed = "Abyssal Key"
            elif "riddle" in ex:
                lock_type = "riddle"
                riddle_obj = random.choice(RIDDLES)
                lock_detail = riddle_obj["question"]
                key_needed = riddle_obj["answer"]  # Store correct answer here

            exits_data[ex] = {
                "locked": True,
                "type": lock_type,
                "key_needed": key_needed,
                "riddle_question": lock_detail
            }
        else:
            exits_data[ex] = {"locked": False}

    room_data = {
        "name": room_name.replace("_", " ").title(),
        "description": desc,
        "depth": depth,
        "monster": monster,
        "loot": loot,
        "exits": exits_data,
        "cleared": False
    }

    # Write the hidden room data JSON
    data_path = room_path / ".room_data.json"
    with open(data_path, "w") as f:
        json.dump(room_data, f, indent=2)

    # Write the user-facing room.md
    write_room_md(room_path, room_data)

    return room_data


def write_room_md(room_path: Path, room_data: Dict[str, Any]):
    """Write the room.md markdown file based on the room data."""
    md_path = room_path / "room.md"
    
    lines = []
    lines.append(f"# {room_data['name']}")
    lines.append("")
    lines.append(room_data['description'])
    lines.append("")
    lines.append("## Chamber Environment")
    lines.append("")

    if room_data["monster"] and room_data["monster"].get("hp", 0) > 0:
        m = room_data["monster"]
        lines.append(f"⚠️ **MONSTER ENCOUNTER**: A **{m['name']}** stalks this area!")
        lines.append(f"> *{m['desc']}*")
        lines.append(f"> Stats: HP {m['hp']}/{m['max_hp']} | ATK {m['atk']} | DEF {m['def']}")
        lines.append("")
    else:
        lines.append("🍃 The air is quiet. No threats are currently visible.")
        lines.append("")

    if room_data["loot"] and room_data["loot"].get("name"):
        loot = room_data["loot"]
        lines.append(f"📦 **LOOT DETECTED**: You see a **{loot['name']}** on the ground.")
        lines.append(f"> *{loot['desc']}*")
        lines.append("")

    lines.append("## Visible Passages")
    lines.append("")
    if room_data["exits"]:
        for exit_name, lock_info in room_data["exits"].items():
            clean_name = exit_name.replace("_", " ").title()
            if lock_info["locked"]:
                if lock_info["type"] == "key":
                    lines.append(f"- 🔒 **{clean_name}** *(Locked - requires {lock_info['key_needed']})*")
                else:
                    lines.append(f"- 🔒 **{clean_name}** *(Locked by a Riddle Seal: \"{lock_info['riddle_question']}\")*")
            else:
                lines.append(f"- 🚶 **[{clean_name}](./{exit_name})**")
    else:
        lines.append("- 🚫 No further exits. This is a dead end.")

    lines.append("")
    lines.append("---")
    lines.append("*Commands:* Use `dark-labyrinth look` to inspect this room. Run `dark-labyrinth take` or `dark-labyrinth attack` to interact.")

    with open(md_path, "w") as f:
        f.write("\n".join(lines))


def build_dungeon(
    keywords: List[str],
    max_depth: int,
    breadth: int,
    chaos: float,
    output_dir: str
) -> int:
    """Build the physical folder structure and files. Returns the count of created rooms."""
    theme_bank, merged_name = merge_themes(keywords)
    output_path = Path(output_dir).resolve()
    
    used_names: Set[str] = set()
    created_count = 0

    def generate_node(current_path: Path, current_name: str, current_depth: int) -> List[str]:
        """Creates the directory, recursively creates child folders, and writes files. Returns actual child names."""
        nonlocal created_count
        current_path.mkdir(parents=True, exist_ok=True)
        created_count += 1

        child_names = []
        if current_depth < max_depth:
            # Determine breadth with chaos
            variance = int(breadth * chaos)
            branch_count = breadth
            if variance > 0:
                branch_count = max(1, breadth + random.randint(-variance, variance))

            # Generate and recurse into child branches
            for _ in range(branch_count):
                room_semantic_name = generate_room_name(theme_bank, used_names, current_depth + 1)
                
                # Chance of a locked door/gate (25% for depth >= 0)
                if random.random() < 0.25:
                    lock_flavor = random.choice(["wood_door", "skeletal_door", "crimson_gate", "abyssal_gate", "riddle_door"])
                    folder_name = f"locked_{lock_flavor}_{room_semantic_name}"
                else:
                    folder_name = room_semantic_name
                
                child_names.append(folder_name)
                # Recurse
                generate_node(current_path / folder_name, room_semantic_name, current_depth + 1)

        # Create files for the current node using the actual child names as exits
        create_room_files(current_path, current_name, current_depth, theme_bank, child_names)
        return child_names

    # Build starting from root
    root_name = f"{keywords[0]}_labyrinth"
    generate_node(output_path / root_name, root_name, 0)

    return created_count
