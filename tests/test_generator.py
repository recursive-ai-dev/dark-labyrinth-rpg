"""
Unit tests for the Dark Labyrinth Generator.
"""

import unittest
import shutil
import tempfile
from pathlib import Path

from dark_labyrinth.generator.themes import merge_themes, generate_room_name
from dark_labyrinth.generator.builder import build_dungeon


class TestLabyrinthGenerator(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test outputs
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Clean up the directory after tests
        shutil.rmtree(self.test_dir)

    def test_theme_merging(self):
        """Test that themes are correctly merged and resolved from keywords."""
        bank, name = merge_themes(["hell", "shadows"])
        
        self.assertIn("hell+shadows", name)
        # Should contain merged roots and descriptors
        self.assertIn("abyss", bank["roots"])
        self.assertIn("shadow", bank["roots"])
        self.assertIn("searing", bank["descriptors"])
        self.assertIn("impenetrable", bank["descriptors"])

    def test_room_name_generation(self):
        """Test that room name generation avoids name collisions."""
        bank, _ = merge_themes(["dungeon"])
        used = set()
        
        # Generate multiple names and ensure they are sanitized and unique
        for _ in range(20):
            name = generate_room_name(bank, used, 1)
            self.assertTrue(len(name) > 0)
            self.assertNotIn(" ", name)
            self.assertNotIn("/", name)

        self.assertEqual(len(used), 20)

    def test_dungeon_building(self):
        """Test recursive physical directory and file generation."""
        output_path = Path(self.test_dir)
        keywords = ["swamp"]
        
        rooms_created = build_dungeon(
            keywords=keywords,
            max_depth=2,
            breadth=2,
            chaos=0.0,
            output_dir=str(output_path)
        )
        
        # Verify rooms are physically created
        root_folder = output_path / "swamp_labyrinth"
        self.assertTrue(root_folder.exists())
        
        # Check files
        room_md = root_folder / "room.md"
        room_json = root_folder / ".room_data.json"
        
        self.assertTrue(room_md.exists())
        self.assertTrue(room_json.exists())

        # At depth=2, breadth=2, chaos=0:
        # Depth 0: 1 root room (swamp_labyrinth)
        # Depth 1: 2 rooms
        # Depth 2: 2 rooms under each depth 1 room (total 4)
        # Total room folders = 1 + 2 + 4 = 7 rooms
        self.assertEqual(rooms_created, 7)


if __name__ == "__main__":
    unittest.main()
