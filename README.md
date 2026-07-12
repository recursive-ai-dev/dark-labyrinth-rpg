# 🏰 Dark Labyrinth RPG

**Dark Labyrinth RPG** is an immersive, procedural, file-system-based dungeon crawler and text adventure engine. It transforms raw directories on your computer into dark-fantasy chambers filled with treasures, monsters, traps, and locked passages.

The game is designed with a unique **Dual Gameplay Engine**:
1. **Shell Explorer Mode**: Navigate the dungeon directly inside your operating system's shell (`bash`, `zsh`) using standard OS commands like `cd`, `ls`, and `cat`, interacting with the rooms via the `dark-labyrinth` CLI. Unlocking gates actually renames the directories in real-time!
2. **Interactive TUI Dashboard**: Launch a terminal dashboard interface powered by `rich` to visualize the chamber, manage your inventory, and fight combat encounters using an old-school menu system.

---

## 🛠️ Installation

Clone or locate this directory and install it locally using your python package manager:

```bash
cd /root/Downloads/Attachments/dark-labyrinth-rpg
pip install -e .
```

This registers the command `dark-labyrinth` in your local path environment.

---

## 🎲 Gameplay Guide

### 1. Forging a Labyrinth
To generate a procedurally mapped labyrinth, use the `generate` command:

```bash
dark-labyrinth generate --keywords hell shadows --depth 4 --breadth 3 --output ./my_dungeons
```
- `--keywords` / `-k`: Themes for room descriptors (e.g. `hell`, `shadows`, `plague`, `swamp`, `iron`, `blood`, `bone`).
- `--depth` / `-d`: How deep the folder nesting runs.
- `--breadth` / `-b`: Branching factor (number of exits per chamber).
- `--chaos` / `-c`: Randomness factor (0.0 to 1.0) altering branch counts.

This will build a new directory tree starting with `hell_labyrinth`.

---

### 2. Shell Explorer Mode (Pure CLI)
Enter the dungeon physically using your terminal shell:

```bash
cd ./my_dungeons/hell_labyrinth
```

Once inside, you will see a `room.md` file describing the chamber, showing current monster encounters, items on the ground, and exits. Use the following commands to play:

- **Look Around**: Inspect the room contents and exits.
  ```bash
  dark-labyrinth look
  ```
- **Take Items**: Pick up scrolls, potions, or weapons found on the ground.
  ```bash
  dark-labyrinth take
  ```
- **Fight Monsters**: Attack the monster inhabiting the room. (Resolves a single combat turn).
  ```bash
  dark-labyrinth attack
  ```
- **Check Status**: Show your character level, stats, HP, gold, and inventory.
  ```bash
  dark-labyrinth status
  ```
- **Equip Weapons or Armor**:
  ```bash
  dark-labyrinth equip "Dagger of Shadows"
  ```
- **Drink Potions**:
  ```bash
  dark-labyrinth drink "Minor Health Potion"
  ```
- **Unlock Passages**: If an exit is locked (e.g., `locked_wood_door_crypt`), unlock it. This consumes a matching key from your backpack or prompts you to answer a riddle. Once unlocked, the folder on your hard drive is renamed (removing `locked_`), allowing you to `cd` inside!
  ```bash
  # Unlock using a key:
  dark-labyrinth unlock locked_wood_door_crypt
  
  # Unlock by answering a riddle:
  dark-labyrinth unlock locked_riddle_door_chamber "answer"
  ```

---

### 3. TUI Dashboard Mode
For a cohesive, terminal dashboard view that handles movement, combat, and inventory management in a single screen, run:

```bash
dark-labyrinth play ./my_dungeons/hell_labyrinth
```

Use the numbered keyboard inputs to navigate the labyrinth, engage in combat, manage your backpack, and explore!

---

## 🛡️ RPG Elements

### Semantic Themes
The dungeon folders are procedurally named using a combination of **29 distinct thematic keyword pools**, connecting adjectives, nouns, and structures (e.g., `the_third_searing_lake_of_wailing_dead` or `sunken_causeway_of_the_hag`).

### Items & Gear
- **Weapons**: Increase your Attack (ATK) power (e.g. *Rusty Iron Sword*, *Dagger of Shadows*, *Paladin's Bastard Sword*).
- **Armor**: Increases your Defense (DEF) rating (e.g. *Leather Jerkin*, *Chainmail Vest*, *Gilded Plate Mail*).
- **Potions**: Restores health points (HP).
- **Keys**: Matches lock-types on gates (*Rusted*, *Skeleton*, *Crimson*, *Abyssal*).

### Combat & Leveling
Engaging monsters like the **Shadow Fiend** or **Labyrinth Minotaur** grants experience points (XP) and Gold. Gaining enough XP triggers a **Level Up**, fully restoring your health and scaling up your base attributes permanently.
Saving is automatic after key actions. State is written to `~/.dark_labyrinth_save.json`.
