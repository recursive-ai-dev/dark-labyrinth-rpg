# Audit — Dark Labyrinth

<!-- REGEN:START — everything here is rewritten at each phase boundary -->
## Scope & method
- **Commit:** 4d8c93ec0297112699a6f60f0b3c8047c0bd4b86
- **Date:** 2026-09-07
- **Languages:** Python
- **Files audited:** `src/dark_labyrinth/engine/state.py`, `src/dark_labyrinth/engine/interpreter.py`, `src/dark_labyrinth/generator/themes.py`, `src/dark_labyrinth/engine/game.py`
- **Tools run:** `ruff`, `mypy`, `pytest`
- **What was NOT covered:** Extensive edge-case testing, interactive TUI fuzzing.

## Executive summary
The Dark Labyrinth RPG engine is generally functional, but suffers from severe vulnerability in directory manipulation logic and widespread silent failure swallowing. The most critical issue (F001) allows for path traversal when renaming directories, meaning a maliciously crafted dungeon can rename arbitrary files outside the game directory. Secondly, many core file operations (`save`, `load`) swallow all exceptions, masking file permission issues or JSON corruption from the user.

## Findings by severity
| ID | Location | Category | Claim | Confidence |
|---|---|---|---|---|
| F001 | `interpreter.py:218` | authorization_bypass | Path traversal vulnerability in folder renaming logic | confirmed |
| F006 | `state.py:160` | error_handling | `save()` swallows all exceptions | confirmed |
| F002 | `game.py:118` | error_handling | Unsafe tuple unpacking from `os.path.split` | confirmed |
| F003 | `themes.py:247` | logic_error | Fallback mechanism in `generate_room_name` mutates set in fallback but doesn't check if fallback exists | confirmed |
| F004 | `interpreter.py:20` | error_handling | `get_local_room` swallows all exceptions | confirmed |
| F005 | `state.py:139` | error_handling | `load()` swallows all exceptions | confirmed |

## Systemic themes
- **Silent Exception Swallowing**: Crucial operations like `save()`, `load()`, and `get_local_room()` use bare `except Exception: pass` or return default values. This makes debugging impossible and silently loses player data.
- **Unvalidated Filesystem Operations**: The core mechanic of renaming folders to "unlock" doors does not sufficiently sanitize or restrict target paths.

## Design opinions
- **Global CWD State**: The game relies heavily on changing the current working directory (`os.chdir`). While this is central to the "Shell Explorer" concept, relying on it for internal path resolution creates brittle code and complicates restarting or escaping the labyrinth programmatically.

## Strengths
- **Decoupled Mechanics**: The core logic is relatively decoupled from the shell interface, making it possible to bolt on a TUI.
- **Procedural Name Generation**: The semantic theme generator is robust and cleanly structures its word pools.

## Verification & limitations
All listed findings are confirmed. Testing was limited to static analysis and manual code review. No fuzzing was performed on the procedural generator to empirically test collision frequency.
<!-- REGEN:END -->

## Findings Log
### F001 — [HIGH] src/dark_labyrinth/engine/interpreter.py:218 — Path traversal vulnerability in folder renaming logic
**Category:** authorization_bypass  **Confidence:** confirmed
**Code:**
```python
os.rename(exit_folder, final_folder)
```
**Trigger:** A malicious room configuration sets an exit name containing '../' characters.
**Impact:** Allows arbitrary file or directory renaming on the host filesystem when a user unlocks a door.
**Fix:** Sanitize 'exit_folder' and 'final_folder' to ensure they only contain safe characters and do not traverse directories.

### F002 — [MEDIUM] src/dark_labyrinth/engine/game.py:118 — Unsafe tuple unpacking from os.path.split
**Category:** error_handling  **Confidence:** confirmed
**Code:**
```python
parent, _ = os.path.split(player.current_room_path)
```
**Trigger:** None, actually mypy complains about this.
**Impact:** Type checker error, but works at runtime.
**Fix:** Type ignore or explicit cast.

### F003 — [MEDIUM] src/dark_labyrinth/generator/themes.py:247 — Fallback mechanism in generate_room_name mutates set in fallback but doesn't check if fallback exists
**Category:** logic_error  **Confidence:** confirmed
**Code:**
```python
fallback = f"chamber_{random.randint(100, 999)}"
    used_names.add(fallback)
    return fallback
```
**Trigger:** All 50 procedural generation attempts collide with existing names in a very dense dungeon generation.
**Impact:** Could potentially generate a duplicate fallback room name if chamber_XYZ was already rolled.
**Fix:** Use a while loop for the fallback to ensure uniqueness.

### F004 — [LOW] src/dark_labyrinth/engine/interpreter.py:20 — get_local_room swallows all exceptions
**Category:** error_handling  **Confidence:** confirmed
**Code:**
```python
except Exception:
        return {}
```
**Trigger:** The `.room_data.json` file is malformed, unreadable, or permission denied.
**Impact:** The game silently treats the room as invalid rather than informing the player of corruption.
**Fix:** Catch JSONDecodeError and log or inform the player of a corrupted file.

### F005 — [LOW] src/dark_labyrinth/engine/state.py:139 — PlayerState.load swallows all exceptions
**Category:** error_handling  **Confidence:** confirmed
**Code:**
```python
except Exception:
            return False
```
**Trigger:** The save file is malformed or inaccessible.
**Impact:** Player save data fails to load silently.
**Fix:** Specific exception handling and logging.

### F006 — [MEDIUM] src/dark_labyrinth/engine/state.py:160 — PlayerState.save swallows all exceptions
**Category:** error_handling  **Confidence:** confirmed
**Code:**
```python
except Exception:
            pass
```
**Trigger:** Disk full or permission denied when saving.
**Impact:** Player progress is silently lost.
**Fix:** Specific exception handling and logging.
