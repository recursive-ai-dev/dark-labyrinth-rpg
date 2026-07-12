"""
Command Line Interface (CLI) for Dark Labyrinth RPG.
Provides commands for dungeon generation and shell explorer / TUI play.
"""

import sys
import argparse
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from dark_labyrinth.generator.builder import build_dungeon
from dark_labyrinth.engine.state import PlayerState
from dark_labyrinth.engine.interpreter import (
    execute_look, execute_take, execute_attack, execute_unlock, execute_read
)
from dark_labyrinth.engine.game import run_tui

console = Console()

BANNER = r"""
 [bold crimson]
  ██████╗  █████╗ ██████╗ ██╗  ██╗    ██╗      █████╗ ██████╗ ██╗   ██╗██████╗ ██╗███╗   ██╗████████╗██╗  ██╗
  ██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝    ██║     ██╔══██╗██╔══██╗╚██╗ ██╔╝██╔══██╗██║████╗  ██║╚══██╔══╝██║  ██║
  ██║  ██║███████║██████╔╝█████╔╝     ██║     ███████║██████╔╝ ╚████╔╝ ██████╔╝██║██╔██╗ ██║   ██║   ███████║
  ██║  ██║██╔══██║██╔══██╗██╔═██╗     ██║     ██╔══██║██╔══██╗  ╚██╔╝  ██╔══██╗██║██║╚██╗██║   ██║   ██╔══██║
  ██████╔╝██║  ██║██║  ██║██║  ██╗    ███████╗██║  ██║██████╔╝   ██║   ██║  ██║██║██║ ╚████║   ██║   ██║  ██║
  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝    ╚══════╝╚═╝  ╚═╝╚═════╝    ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝
 [/bold crimson]
 [dim]         ~ File System Dungeon Crawler & Procedural Text Adventure Engine v0.1.0 ~ [/dim]
"""


def print_status(player: PlayerState):
    """Print the player status details in a beautiful table."""
    table = Table(title="[bold cyan]Player Status & Inventory[/bold cyan]", box=box.ROUNDED)
    table.add_column("Stat", style="dim")
    table.add_column("Value", style="bold")

    table.add_row("Level", f"{player.level}")
    table.add_row("XP", f"{player.xp} / {player.level * 100}")
    table.add_row("HP", f"{player.hp} / {player.max_hp}")
    table.add_row("Gold", f"{player.gold}")
    table.add_row("Equipped Weapon", player.equipped_weapon or "[dim]None[/dim]")
    table.add_row("Equipped Armor", player.equipped_armor or "[dim]None[/dim]")

    console.print()
    console.print(table)

    # Inventory
    inv_table = Table(title="[bold yellow]Backpack[/bold yellow]", box=box.SIMPLE)
    inv_table.add_column("Name", style="yellow")
    inv_table.add_column("Type", style="dim")
    inv_table.add_column("Description")

    for item in player.inventory:
        inv_table.add_row(item["name"], item["type"], item["desc"])

    console.print(inv_table)


def main():
    parser = argparse.ArgumentParser(
        description="Dark Labyrinth RPG: Procedural folder-based dungeon game CLI.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: generate
    gen_parser = subparsers.add_parser("generate", help="Procedurally build a new dungeon structure.")
    gen_parser.add_argument("--keywords", "-k", nargs="+", default=["dungeon"], help="Themes/Keywords (e.g. hell shadows)")
    gen_parser.add_argument("--depth", "-d", type=int, default=3, help="Max dungeon tree depth")
    gen_parser.add_argument("--breadth", "-b", type=int, default=3, help="Exits/branching count per chamber")
    gen_parser.add_argument("--chaos", "-c", type=float, default=0.2, help="Dungeon branching variance factor (0.0 to 1.0)")
    gen_parser.add_argument("--output", "-o", type=str, default="./labyrinth_output", help="Root folder for output")

    # Command: play
    play_parser = subparsers.add_parser("play", help="Launch interactive TUI dashboard mode.")
    play_parser.add_argument("dungeon_path", type=str, nargs="?", default="", help="Path to the dungeon root folder to play in")

    # Command: status
    subparsers.add_parser("status", help="Show player stats and inventory backpack.")

    # Command: look
    subparsers.add_parser("look", help="[Shell Mode] Look around the current chamber folder.")

    # Command: take
    subparsers.add_parser("take", help="[Shell Mode] Pick up loot in the current folder room.")

    # Command: attack
    subparsers.add_parser("attack", help="[Shell Mode] Attack the monster in the current folder.")

    # Command: unlock
    unlock_parser = subparsers.add_parser("unlock", help="[Shell Mode] Unlock a door/gate in this folder.")
    unlock_parser.add_argument("passage", type=str, help="Folder name of the locked passage (e.g. locked_wood_door_vault)")
    unlock_parser.add_argument("answer", type=str, nargs="?", default="", help="Answer to a riddle (if riddle lock)")

    # Command: drink
    drink_parser = subparsers.add_parser("drink", help="[Shell Mode] Drink a healing potion.")
    drink_parser.add_argument("potion", type=str, help="Name of potion (e.g. 'Minor Health Potion')")

    # Command: read
    read_parser = subparsers.add_parser("read", help="[Shell Mode] Read a scroll from inventory.")
    read_parser.add_argument("scroll", type=str, help="Name of scroll (e.g. 'Scroll of Healing')")

    # Command: equip
    equip_parser = subparsers.add_parser("equip", help="[Shell Mode] Equip gear from inventory.")
    equip_parser.add_argument("gear", type=str, help="Name of weapon/armor")

    args = parser.parse_args()

    # Default action: print banner & help
    if not args.command:
        console.print(BANNER)
        parser.print_help()
        sys.exit(0)

    # Initialize and load PlayerState
    player = PlayerState()
    player.load()

    if args.command == "generate":
        console.print(BANNER)
        console.print(f"🔨 [bold cyan]Forging Labyrinth...[/bold cyan]")
        console.print(f"   Keywords: {', '.join(args.keywords)}")
        console.print(f"   Depth:    {args.depth} | Breadth: {args.breadth}")
        console.print(f"   Output:   {args.output}")
        console.print()

        try:
            created = build_dungeon(
                keywords=args.keywords,
                max_depth=args.depth,
                breadth=args.breadth,
                chaos=args.chaos,
                output_dir=args.output
            )
            console.print(f"🎉 [bold green]Dungeon Forged Successfully![/bold green]")
            console.print(f"   Rooms Created: {created}")
            root_folder = f"{args.keywords[0]}_labyrinth"
            console.print(f"   To start playing, run: `dark-labyrinth play {Path(args.output) / root_folder}`")
            console.print(f"   Or: `cd {Path(args.output) / root_folder}` and use `dark-labyrinth look` in shell mode!")
        except Exception as e:
            console.print(f"❌ [bold red]Generation Failed:[/bold red] {e}")
            sys.exit(1)

    elif args.command == "play":
        # Resolve target dungeon path
        dungeon_path = args.dungeon_path
        if not dungeon_path:
            # Check if current directory is a dungeon room
            if Path(".room_data.json").exists():
                dungeon_path = "."
            elif player.current_room_path and Path(player.current_room_path).exists():
                dungeon_path = player.current_room_path
            else:
                console.print("❌ [red]Error:[/red] Please specify a dungeon root path. Example: `dark-labyrinth play ./labyrinth_output/dungeon_labyrinth`")
                sys.exit(1)

        run_tui(dungeon_path)

    elif args.command == "status":
        print_status(player)

    elif args.command == "look":
        res = execute_look(player)
        console.print(res)

    elif args.command == "take":
        res = execute_take(player)
        console.print(res)

    elif args.command == "attack":
        res = execute_attack(player)
        console.print(res)

    elif args.command == "unlock":
        res = execute_unlock(player, args.passage, args.answer)
        console.print(res)

    elif args.command == "drink":
        res = player.use_potion(args.potion)
        console.print(res)

    elif args.command == "read":
        res = execute_read(player, args.scroll)
        console.print(res)

    elif args.command == "equip":
        res = player.equip_gear(args.gear)
        console.print(res)


if __name__ == "__main__":
    main()
