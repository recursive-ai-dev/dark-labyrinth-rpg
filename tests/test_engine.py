"""
Unit tests for the RPG engine logic (combat, player stats, items, inventory).
"""

import unittest
import unittest.mock
from dark_labyrinth.engine.state import PlayerState


class TestRPGEngine(unittest.TestCase):
    def setUp(self):
        self.player = PlayerState()
        # Reset defaults for test consistency
        self.player.hp = 100
        self.player.max_hp = 100
        self.player.atk_base = 10
        self.player.def_base = 2
        self.player.level = 1
        self.player.xp = 0
        self.player.gold = 50
        self.player.inventory = [
            {"name": "Rusty Iron Sword", "type": "weapon", "atk": 5, "def": 0, "desc": "Sword"},
            {"name": "Minor Health Potion", "type": "potion", "hp": 25, "desc": "Potion"}
        ]
        self.player.equipped_weapon = "Rusty Iron Sword"
        self.player.equipped_armor = ""

    def test_calculated_stats(self):
        """Test that attack and defense stats dynamically include equipped items."""
        # Base ATK is 10 + Rusty Iron Sword (5) = 15
        self.assertEqual(self.player.atk, 15)
        # Base DEF is 2 + no armor = 2
        self.assertEqual(self.player.defense, 2)

        # Equip armor
        self.player.inventory.append({"name": "Chainmail", "type": "armor", "def": 4, "desc": "Armor"})
        self.player.equipped_armor = "Chainmail"
        
        self.assertEqual(self.player.defense, 6)

    def test_xp_and_level_up(self):
        """Test that accumulating enough XP triggers character level up."""
        # Level 1 needs 100 XP
        leveled_up = self.player.add_xp(50)
        self.assertFalse(leveled_up)
        self.assertEqual(self.player.level, 1)

        leveled_up = self.player.add_xp(55)
        self.assertTrue(leveled_up)
        self.assertEqual(self.player.level, 2)
        # Check attribute updates
        self.assertEqual(self.player.max_hp, 120)
        self.assertEqual(self.player.hp, 120)
        self.assertEqual(self.player.xp, 5)  # Overflow carried over

    def test_massive_xp_gain(self):
        """Test that gaining a massive amount of XP correctly progresses multiple levels."""
        # Player is level 1, xp 0.
        # Level 1 -> 2 needs 100
        # Level 2 -> 3 needs 200
        # Level 3 -> 4 needs 300
        # Total to reach level 4, xp 50 is: 100 + 200 + 300 + 50 = 650
        leveled_up = self.player.add_xp(650)
        self.assertTrue(leveled_up)
        self.assertEqual(self.player.level, 4)
        self.assertEqual(self.player.xp, 50)

        # Max HP base was 100. Gained 3 levels (3 * 20 = 60). New Max HP should be 160.
        self.assertEqual(self.player.max_hp, 160)
        self.assertEqual(self.player.hp, 160)

    def test_item_backpack_management(self):
        """Test item additions and removals."""
        # Check has key
        self.assertFalse(self.player.has_key("Abyssal Key"))

        # Add key
        self.player.add_item({"name": "Abyssal Key", "type": "key", "desc": "Key"})
        self.assertTrue(self.player.has_key("Abyssal Key"))

        # Remove key
        removed = self.player.remove_item("Abyssal Key")
        self.assertTrue(removed)
        self.assertFalse(self.player.has_key("Abyssal Key"))

    def test_potion_consumption(self):
        """Test drinking potions to heal damage."""
        self.player.hp = 50
        
        msg = self.player.use_potion("Minor Health Potion")
        self.assertIn("Healed 25 HP", msg)
        self.assertEqual(self.player.hp, 75)
        
        # Potion should be consumed
        self.assertFalse(any(it["name"] == "Minor Health Potion" for it in self.player.inventory))

    @unittest.mock.patch("dark_labyrinth.engine.interpreter.save_local_room")
    @unittest.mock.patch("dark_labyrinth.engine.interpreter.get_local_room")
    def test_scroll_consumption(self, mock_get_room, mock_save_room):
        """Test reading scrolls (Healing and Banishing)."""
        from dark_labyrinth.engine.interpreter import execute_read

        # 1. Test Scroll of Healing
        self.player.hp = 10
        self.player.inventory.append({"name": "Scroll of Healing", "type": "scroll", "effect": "heal_full", "desc": "Scroll"})
        
        msg = execute_read(self.player, "Scroll of Healing")
        self.assertIn("restoring 90 HP", msg)
        self.assertEqual(self.player.hp, 100)
        self.assertFalse(any(it["name"] == "Scroll of Healing" for it in self.player.inventory))

        # 2. Test Scroll of Banishing (No Monster)
        self.player.inventory.append({"name": "Scroll of Banishing", "type": "scroll", "effect": "kill_monster", "desc": "Scroll"})
        mock_get_room.return_value = {
            "name": "Shadow Crypt",
            "monster": {}
        }
        msg = execute_read(self.player, "Scroll of Banishing")
        self.assertIn("no enemies here", msg)
        self.assertTrue(any(it["name"] == "Scroll of Banishing" for it in self.player.inventory))

        # 3. Test Scroll of Banishing (With Monster)
        mock_get_room.return_value = {
            "name": "Shadow Crypt",
            "monster": {"name": "Shadow Fiend", "hp": 40, "max_hp": 40, "atk": 10, "def": 3, "xp": 45, "gold": 25, "desc": "Fiend"}
        }
        msg = execute_read(self.player, "Scroll of Banishing")
        self.assertIn("turns to ash", msg)
        self.assertIn("gained 45 XP", msg)
        self.assertEqual(self.player.gold, 75)
        self.assertEqual(self.player.xp, 45)
        self.assertFalse(any(it["name"] == "Scroll of Banishing" for it in self.player.inventory))
        mock_save_room.assert_called_once()


if __name__ == "__main__":
    unittest.main()
