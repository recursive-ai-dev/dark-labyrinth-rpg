"""
TUI Game Engine for Dark Labyrinth RPG.
Provides an interactive text-adventure terminal layout with widgets and combat logs.
"""

import sys
import os
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.prompt import Prompt, Confirm
from rich import box

from dark_labyrinth.engine.state import PlayerState
from dark_labyrinth.engine.interpreter import (
    execute_look, execute_take, execute_attack, execute_unlock, get_local_room
)

console = Console()


def get_tui_layout(player: PlayerState, current_room_info: str, combat_log: str) -> Layout:
    """Create a 3-pane layout: Stats top, Room contents left, Actions/Logs right."""
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=4),
        Layout(name="main")
    )
    layout["main"].split_row(
        Layout(name="room", ratio=3),
        Layout(name="log", ratio=2)
    )

    # 1. Header (Player Stats)
    stats_table = Table.grid(expand=True)
    stats_table.add_column(justify="center", ratio=1)
    stats_table.add_column(justify="center", ratio=1)
    stats_table.add_column(justify="center", ratio=1)
    stats_table.add_column(justify="center", ratio=1)
    stats_table.add_column(justify="center", ratio=1)

    stats_table.add_row(
        f"[bold yellow]Level {player.level}[/bold yellow] (XP: {player.xp}/{player.level * 100})",
        f"[bold red]HP: {player.hp}/{player.max_hp}[/bold red]",
        f"[bold green]Gold: {player.gold}[/bold green]",
        f"[bold blue]Weapon: {player.equipped_weapon or 'None'}[/bold blue]",
        f"[bold magenta]Armor: {player.equipped_armor or 'None'}[/bold magenta]"
    )
    layout["header"].update(Panel(stats_table, title="[bold cyan]Player Attributes[/bold cyan]", border_style="cyan"))

    # 2. Left side - Room Details
    layout["room"].update(Panel(current_room_info, title="[bold green]Current Chamber[/bold green]", border_style="green", padding=(1, 2)))

    # 3. Right side - Combat/Action log
    layout["log"].update(Panel(combat_log, title="[bold magenta]Log & Chronicle[/bold magenta]", border_style="magenta", padding=(1, 2)))

    return layout


def run_tui(dungeon_root: str):
    """Launch the interactive TUI mode starting at the specified dungeon root directory."""
    dungeon_root = str(Path(dungeon_root).resolve())

    player = PlayerState()
    player.load()

    # Change working directory to the starting dungeon
    try:
        os.chdir(dungeon_root)
    except Exception as e:
        console.print(f"[red]Error entering dungeon: {e}[/red]")
        sys.exit(1)

    player.current_room_path = str(Path(".").resolve())
    player.save()

    combat_log = "⚔️ You enter the dark labyrinth. The heavy stone doors slam shut behind you..."
    
    while True:
        # Check that we are still in a valid room
        room = get_local_room()
        if not room:
            console.print("[red]Error: Not in a valid labyrinth room folder![/red]")
            break

        room_info = execute_look(player)
        
        # Clear screen
        console.clear()
        
        # Draw layout
        layout = get_tui_layout(player, room_info, combat_log)
        console.print(layout)

        # Build options list
        options = []
        action_map = {}

        # 1. Fight monster
        if room.get("monster") and room["monster"].get("hp", 0) > 0:
            options.append("Fight the monster")
            action_map[len(options)] = "fight"
        
        # 2. Take loot
        if room.get("loot") and room["loot"].get("name"):
            options.append("Take the loot")
            action_map[len(options)] = "take"

        # 3. Exits
        for exit_name, info in room.get("exits", {}).items():
            clean_name = exit_name.replace("_", " ").title()
            if info["locked"]:
                options.append(f"Attempt to unlock: {clean_name}")
                action_map[len(options)] = ("unlock", exit_name)
            else:
                options.append(f"Passage: {clean_name}")
                action_map[len(options)] = ("move", exit_name)

        # 4. Parent directory exit
        parent_data = Path("..") / ".room_data.json"
        if parent_data.exists():
            options.append("Retreat to previous chamber (..)")
            action_map[len(options)] = "back"

        # 5. Inventory
        options.append("Open inventory (use potion / equip gear)")
        action_map[len(options)] = "inventory"

        # 6. Exit game
        options.append("Save and quit")
        action_map[len(options)] = "quit"

        # Render menu options
        console.print("\n[bold cyan]What will you do?[/bold cyan]")
        for idx, opt in enumerate(options, 1):
            console.print(f" [bold yellow]{idx}[/bold yellow]. {opt}")

        # Get choice
        choice_str = Prompt.ask("\nEnter choice number", default="1")
        try:
            choice = int(choice_str)
            if choice not in action_map:
                combat_log = "❌ Invalid selection. Focus your mind."
                continue
        except ValueError:
            combat_log = "❌ Enter a number."
            continue

        action = action_map[choice]

        if action == "fight":
            result = execute_attack(player)
            combat_log = result
            if "YOU HAVE DIED" in result:
                # Player died, reset position to dungeon root
                combat_log += "\n💀 You woke up dizzy, with lighter pockets..."
                os.chdir(dungeon_root)
                player.current_room_path = str(Path(".").resolve())
                player.save()
        
        elif action == "take":
            result = execute_take(player)
            combat_log = result
        
        elif isinstance(action, tuple) and action[0] == "unlock":
            exit_name = action[1]
            exits = room.get("exits", {})
            info = exits[exit_name]
            
            if info["type"] == "key":
                result = execute_unlock(player, exit_name)
                combat_log = result
            else:
                # Riddle
                console.print(f"\n❓ [bold cyan]Riddle Seal[/bold cyan]: \"{info['riddle_question']}\"")
                ans = Prompt.ask("[bold magenta]Enter answer[/bold magenta]")
                result = execute_unlock(player, exit_name, ans)
                combat_log = result

        elif isinstance(action, tuple) and action[0] == "move":
            exit_name = action[1]
            try:
                os.chdir(exit_name)
                player.current_room_path = str(Path(".").resolve())
                player.save()
                combat_log = f"🚶 You traveled into: {exit_name.replace('_', ' ').title()}"
            except Exception as e:
                combat_log = f"❌ Passage blocked by rubble: {e}"

        elif action == "back":
            try:
                os.chdir("..")
                player.current_room_path = str(Path(".").resolve())
                player.save()
                combat_log = "🚶 You retreated back one chamber."
            except Exception as e:
                combat_log = f"❌ Retreat blocked: {e}"

        elif action == "inventory":
            combat_log = show_tui_inventory(player)

        elif action == "quit":
            player.save()
            console.print("\n👋 Saving state. Safe travels through the shadows.")
            sys.exit(0)


def show_tui_inventory(player: PlayerState) -> str:
    """Sub-menu for inventory management."""
    console.clear()
    console.print(Panel(f"[bold cyan]Inventory ({len(player.inventory)} items)[/bold cyan]", border_style="cyan"))

    if not player.inventory:
        console.print("   Empty pockets.")
        Prompt.ask("\nPress Enter to return")
        return "💨 Inventory is empty."

    # List items
    for idx, item in enumerate(player.inventory, 1):
        equip_str = ""
        if item["name"] == player.equipped_weapon or item["name"] == player.equipped_armor:
            equip_str = " (Equipped)"
        console.print(f" [bold yellow]{idx}[/bold yellow]. {item['name']} [dim]({item['type']}){equip_str}[/dim] - *{item['desc']}*")

    console.print(f"\n [bold yellow]0[/bold yellow]. Return")
    
    choice_str = Prompt.ask("\nSelect an item to use/equip", default="0")
    try:
        choice = int(choice_str)
        if choice == 0:
            return "Returned to combat log."
        
        if 1 <= choice <= len(player.inventory):
            item = player.inventory[choice - 1]
            if item["type"] == "potion":
                return player.use_potion(item["name"])
            elif item["type"] in ("weapon", "armor"):
                return player.equip_gear(item["name"])
            elif item["type"] == "scroll":
                from dark_labyrinth.engine.interpreter import execute_read
                return execute_read(player, item["name"])
            else:
                return f"ℹ️ The {item['name']} cannot be used directly from menu."
        else:
            return "❌ Invalid item selection."
    except ValueError:
        return "❌ Invalid entry."
