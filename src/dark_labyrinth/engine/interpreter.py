"""
Interpreter for Shell Explorer Mode in Dark Labyrinth RPG.
Parses local directory state, executes player actions, and modifies the filesystem.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any

from dark_labyrinth.engine.state import PlayerState
from dark_labyrinth.generator.builder import write_room_md


def get_local_room() -> Dict[str, Any]:
    """Retrieve room data if running in a valid dungeon room directory."""
    data_path = Path(".") / ".room_data.json"
    if not data_path.exists():
        return {}
    try:
        with open(data_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading room data: {e}")
        return {}


def save_local_room(room_data: Dict[str, Any]):
    """Save updated room data and re-render room.md."""
    data_path = Path(".") / ".room_data.json"
    with open(data_path, "w") as f:
        json.dump(room_data, f, indent=2)
    write_room_md(Path("."), room_data)


def execute_look(player: PlayerState) -> str:
    """Read and format the current room's details."""
    room = get_local_room()
    if not room:
        return "⚠️ You are not in a valid room of the labyrinth. CD into a labyrinth folder to explore."

    # Update player save file with current room location
    player.current_room_path = str(Path(".").resolve())
    player.save()

    lines = []
    lines.append(f"🏰 [bold cyan]{room['name']}[/bold cyan] (Depth: {room['depth']})")
    lines.append("-" * len(room['name']))
    lines.append(room['description'])
    lines.append("")
    
    if room.get("monster") and room["monster"].get("hp", 0) > 0:
        m = room["monster"]
        lines.append(f"👹 [bold red]MONSTER[/bold red]: A [bold]{m['name']}[/bold] stands here!")
        lines.append(f"   HP: {m['hp']}/{m['max_hp']} | ATK: {m['atk']} | DEF: {m['def']}")
        lines.append(f"   *\"{m['desc']}\"*")
        lines.append("")
    
    if room.get("loot") and room["loot"].get("name"):
        l = room["loot"]
        lines.append(f"🎁 [bold yellow]LOOT[/bold yellow]: You see a [bold]{l['name']}[/bold].")
        lines.append(f"   *\"{l['desc']}\"*")
        lines.append("")

    lines.append("🚪 [bold green]Exits:[/bold green]")
    for exit_name, info in room.get("exits", {}).items():
        clean_name = exit_name.replace("_", " ").title()
        if info["locked"]:
            if info["type"] == "key":
                lines.append(f"   🔒 {clean_name} (Requires: {info['key_needed']})")
            else:
                lines.append(f"   🔒 {clean_name} (Riddle Seal: \"{info['riddle_question']}\")")
        else:
            lines.append(f"   🚶 {clean_name} (./{exit_name})")

    return "\n".join(lines)


def execute_take(player: PlayerState) -> str:
    """Attempt to pick up loot from the room."""
    room = get_local_room()
    if not room:
        return "⚠️ You are not in a valid room of the labyrinth."

    loot = room.get("loot")
    if not loot or not loot.get("name"):
        return "💨 There is nothing of value here to take."

    player.add_item(loot)
    room["loot"] = {}
    
    save_local_room(room)
    player.save()
    
    return f"🎁 [bold yellow]Picked up[/bold yellow]: {loot['name']}\n*\"{loot['desc']}\"*"


def execute_attack(player: PlayerState) -> str:
    """Fight the room monster for one round."""
    room = get_local_room()
    if not room:
        return "⚠️ You are not in a valid room of the labyrinth."

    monster = room.get("monster")
    if not monster or monster.get("hp", 0) <= 0:
        return "🍃 There are no enemies here."

    lines = []
    
    # 1. Player attacks monster
    player_dmg = max(1, player.atk - monster["def"])
    monster["hp"] = max(0, monster["hp"] - player_dmg)
    lines.append(f"⚔️ You strike the [bold]{monster['name']}[/bold] for [bold red]{player_dmg}[/bold red] damage!")

    if monster["hp"] <= 0:
        # Monster dies
        lines.append(f"💀 [bold green]Victory![/bold green] You have slain the {monster['name']}!")
        lines.append(f"💰 Found {monster['gold']} gold coins and gained {monster['xp']} XP.")
        
        player.gold += monster["gold"]
        leveled_up = player.add_xp(monster["xp"])
        if leveled_up:
            lines.append(f"🎉 [bold yellow]LEVEL UP![/bold yellow] You reached Level {player.level}! Max HP increased.")
        
        room["monster"] = {}
        save_local_room(room)
        player.save()
        return "\n".join(lines)

    # 2. Monster retaliates
    monster_dmg = max(1, monster["atk"] - player.defense)
    player.hp = max(0, player.hp - monster_dmg)
    lines.append(f"💥 The [bold]{monster['name']}[/bold] hits you back for [bold red]{monster_dmg}[/bold red] damage!")

    if player.hp <= 0:
        # Player dies
        lines.append("")
        lines.append("💀💀💀 [bold red]YOU HAVE DIED[/bold red] 💀💀💀")
        lines.append("Your broken body joins the bones of the labyrinth...")
        lines.append("Respawning at the nearest camp (health restored, gold penalized by 50%).")
        
        player.hp = player.max_hp
        player.gold = int(player.gold * 0.5)
        # Try to find root dungeon path to send them back if saved
        player.save()
    else:
        lines.append(f"❤️ Your HP: {player.hp}/{player.max_hp} | Monster HP: {monster['hp']}/{monster['max_hp']}")

    # Save changes
    room["monster"] = monster
    save_local_room(room)
    player.save()

    return "\n".join(lines)


def execute_unlock(player: PlayerState, exit_folder: str, answer_or_key: str = "") -> str:
    """Unlock a locked door/gate by consuming a key or answering a riddle."""
    room = get_local_room()
    if not room:
        return "⚠️ You are not in a valid room of the labyrinth."

    exits = room.get("exits", {})
    if exit_folder not in exits:
        # Try finding key ignoring case
        matching_exit = None
        for ex in exits:
            if ex.lower() == exit_folder.lower():
                matching_exit = ex
                break
        if not matching_exit:
            return f"❌ There is no exit named '{exit_folder}' here."
        exit_folder = matching_exit

    lock_info = exits[exit_folder]
    if not lock_info["locked"]:
        return f"🚶 The passage to '{exit_folder}' is already open."

    success_msg = ""
    if lock_info["type"] == "key":
        key_needed = lock_info["key_needed"]
        if player.has_key(key_needed):
            # Consume key
            player.remove_item(key_needed)
            success_msg = f"🔓 [bold green]UNLOCKED[/bold green]: You unlock the door with the {key_needed}!"
        else:
            return f"❌ Locked door. You need a [bold]{key_needed}[/bold] to pass."

    elif lock_info["type"] == "riddle":
        correct_ans = lock_info["key_needed"].lower().strip()
        user_ans = answer_or_key.lower().strip()

        if not user_ans:
            return f"❓ Riddle Seal: \"{lock_info['riddle_question']}\"\n*Usage:* Run `dark-labyrinth unlock {exit_folder} \"your answer\"`"

        if user_ans == correct_ans:
            success_msg = f"🔓 [bold green]SEAL SHATTERED[/bold green]: The riddle seal fades away!"
        else:
            return f"❌ Incorrect answer. The riddle seal glows crimson: \"{lock_info['riddle_question']}\""
    else:
        return "❌ Unknown lock type."

    # Shared unlock logic
    lock_info["locked"] = False

    # Rename physical folder
    unlocked_folder = exit_folder[7:] if exit_folder.startswith("locked_") else exit_folder

    if "/" in exit_folder or "\\" in exit_folder or ".." in exit_folder:
        return "❌ Invalid exit name."
    if "/" in unlocked_folder or "\\" in unlocked_folder or ".." in unlocked_folder:
        return "❌ Invalid exit name."

    # Check if target folder name exists to prevent duplicates
    counter = 1
    final_folder = unlocked_folder
    while Path(final_folder).exists():
        final_folder = f"{unlocked_folder}_{counter}"
        counter += 1

    try:
        os.rename(exit_folder, final_folder)
    except Exception as e:
        return f"❌ OS Error renaming folder: {e}"

    # Update exits map
    exits[final_folder] = {"locked": False}
    del exits[exit_folder]

    save_local_room(room)
    player.save()
    return f"{success_msg} The folder has been renamed to '{final_folder}'."


def execute_read(player: PlayerState, scroll_name: str) -> str:
    """Read a scroll from inventory and apply its effect."""
    found_scroll = None
    for item in player.inventory:
        if item["name"].lower() == scroll_name.lower() and item["type"] == "scroll":
            found_scroll = item
            break

    if not found_scroll:
        return f"❌ You do not have a '{scroll_name}' in your inventory."

    effect = found_scroll.get("effect")
    if effect == "heal_full":
        old_hp = player.hp
        player.hp = player.max_hp
        player.inventory.remove(found_scroll)
        player.save()
        return f"📜 You read {found_scroll['name']}. A warm light envelops you, restoring {player.hp - old_hp} HP! (HP: {player.hp}/{player.max_hp})"

    elif effect == "kill_monster":
        room = get_local_room()
        if not room:
            return "⚠️ You are not in a valid room of the labyrinth."
        monster = room.get("monster")
        if not monster or monster.get("hp", 0) <= 0:
            return f"📜 You read {found_scroll['name']} but there are no enemies here. The spell fizzles."

        lines = []
        lines.append(f"📜 You read {found_scroll['name']} and point at the [bold]{monster['name']}[/bold]!")
        lines.append(f"⚡ A blinding flash of light erupts! The {monster['name']} turns to ash.")
        lines.append(f"💰 Found {monster['gold']} gold coins and gained {monster['xp']} XP.")

        player.gold += monster["gold"]
        leveled_up = player.add_xp(monster["xp"])
        if leveled_up:
            lines.append(f"🎉 [bold yellow]LEVEL UP![/bold yellow] You reached Level {player.level}! Max HP increased.")

        room["monster"] = {}
        player.inventory.remove(found_scroll)
        save_local_room(room)
        player.save()
        return "\n".join(lines)

    return "❌ Unknown scroll effect."
