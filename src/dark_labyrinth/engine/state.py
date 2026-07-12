"""
Player state and profile manager for Dark Labyrinth RPG.
Handles player stats, inventory, equipment, and save/load persistence.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List

SAVE_PATH = Path.home() / ".dark_labyrinth_save.json"


class PlayerState:
    def __init__(self):
        self.hp = 100
        self.max_hp = 100
        self.atk_base = 10
        self.def_base = 2
        self.level = 1
        self.xp = 0
        self.gold = 50
        self.inventory: List[Dict[str, Any]] = [
            {"name": "Rusty Iron Sword", "type": "weapon", "atk": 5, "def": 0, "desc": "A chipped iron blade. Heavy but effective."},
            {"name": "Minor Health Potion", "type": "potion", "hp": 25, "desc": "A small vial filled with glowing red liquid. Restores 25 HP."},
            {"name": "Rusted Key", "type": "key", "desc": "An old iron key, brown with rust. Matches common wooden doors."}
        ]
        self.equipped_weapon: str = "Rusty Iron Sword"
        self.equipped_armor: str = ""
        self.current_room_path: str = ""

    @property
    def atk(self) -> int:
        """Calculates total attack power including equipped weapon."""
        weapon_bonus = 0
        if self.equipped_weapon:
            for item in self.inventory:
                if item["name"] == self.equipped_weapon and item["type"] == "weapon":
                    weapon_bonus = item.get("atk", 0)
                    break
        return self.atk_base + weapon_bonus

    @property
    def defense(self) -> int:
        """Calculates total defense including equipped armor."""
        armor_bonus = 0
        if self.equipped_armor:
            for item in self.inventory:
                if item["name"] == self.equipped_armor and item["type"] == "armor":
                    armor_bonus = item.get("def", 0)
                    break
        return self.def_base + armor_bonus

    def add_xp(self, amount: int) -> bool:
        """Add XP and return True if leveled up."""
        self.xp += amount
        next_level_xp = self.level * 100
        if self.xp >= next_level_xp:
            self.level += 1
            self.xp -= next_level_xp
            self.max_hp += 20
            self.hp = self.max_hp
            self.atk_base += 3
            self.def_base += 1
            return True
        return False

    def add_item(self, item: Dict[str, Any]):
        """Add an item to the player's inventory."""
        self.inventory.append(item)

    def remove_item(self, item_name: str) -> bool:
        """Remove one instance of an item by name. Return True if found."""
        for i, item in enumerate(self.inventory):
            if item["name"].lower() == item_name.lower():
                self.inventory.pop(i)
                # Unequip if removed
                if self.equipped_weapon and self.equipped_weapon.lower() == item["name"].lower():
                    self.equipped_weapon = ""
                elif self.equipped_armor and self.equipped_armor.lower() == item["name"].lower():
                    self.equipped_armor = ""
                return True
        return False

    def has_key(self, key_name: str) -> bool:
        """Check if the player has a key by name."""
        return any(item["name"].lower() == key_name.lower() and item["type"] == "key" for item in self.inventory)

    def use_potion(self, potion_name: str) -> str:
        """Drink a potion and restore HP. Returns result message."""
        found_potion = None
        for item in self.inventory:
            if item["name"].lower() == potion_name.lower() and item["type"] == "potion":
                found_potion = item
                break

        if not found_potion:
            return f"❌ You do not have a '{potion_name}' in your inventory."

        heal_amount = found_potion.get("hp", 0)
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + heal_amount)
        self.inventory.remove(found_potion)
        self.save()
        return f"🍷 Drank {found_potion['name']}. Healed {self.hp - old_hp} HP! (HP: {self.hp}/{self.max_hp})"

    def equip_gear(self, gear_name: str) -> str:
        """Equip weapon or armor from inventory."""
        found_gear = None
        for item in self.inventory:
            if item["name"].lower() == gear_name.lower() and item["type"] in ("weapon", "armor"):
                found_gear = item
                break

        if not found_gear:
            return f"❌ You do not have '{gear_name}' in your inventory."

        if found_gear["type"] == "weapon":
            self.equipped_weapon = found_gear["name"]
            self.save()
            return f"⚔️ Equipped weapon: {found_gear['name']} (+{found_gear['atk']} ATK)"
        else:
            self.equipped_armor = found_gear["name"]
            self.save()
            return f"🛡️ Equipped armor: {found_gear['name']} (+{found_gear['def']} DEF)"

    def load(self) -> bool:
        """Load player state from save file. Returns True if successful."""
        if not SAVE_PATH.exists():
            return False
        try:
            with open(SAVE_PATH, "r") as f:
                data = json.load(f)
            self.hp = data.get("hp", 100)
            self.max_hp = data.get("max_hp", 100)
            self.atk_base = data.get("atk_base", 10)
            self.def_base = data.get("def_base", 2)
            self.level = data.get("level", 1)
            self.xp = data.get("xp", 0)
            self.gold = data.get("gold", 50)
            self.inventory = data.get("inventory", [])
            self.equipped_weapon = data.get("equipped_weapon", "")
            self.equipped_armor = data.get("equipped_armor", "")
            self.current_room_path = data.get("current_room_path", "")
            return True
        except Exception:
            return False

    def save(self):
        """Save player state to JSON file."""
        data = {
            "hp": self.hp,
            "max_hp": self.max_hp,
            "atk_base": self.atk_base,
            "def_base": self.def_base,
            "level": self.level,
            "xp": self.xp,
            "gold": self.gold,
            "inventory": self.inventory,
            "equipped_weapon": self.equipped_weapon,
            "equipped_armor": self.equipped_armor,
            "current_room_path": self.current_room_path
        }
        try:
            with open(SAVE_PATH, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass
