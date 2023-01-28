# Survivalistic Parser

## About

This script is used to automatically generate new database files for the Stardew Valley mod [Survivalistic](https://www.nexusmods.com/stardewvalley/mods/12179).

It lets you select any directory (for example your "Mods" folder) and automatically scans for all Json Assets to turn them into database files in the output directory.

## Usage

### Installer (Windows Only)

- Download the latest release [HERE](https://github.com/Moonwolf287/survivalistic_parser/releases/latest)
- Open the `.exe` file.
- Select your Stardew Valley/Mods folder
- After it is done you can find the new databases in the output folder next to the executable.

### Script

- Install python 3
- Install json5 package `pip install json5`
- Download the script
- Run the script `python survivalistic_parser.py`
- Select your Stardew Valley/Mods folder
- After it is done you can find the new databases in the output folder next to the script.

## Configuration

There are some configuration options inside the script. You can edit them to configure handling of thirst for Food items.

```python
# How much thirst you recover from drinkable items
DRINKABLE_THIRST_RECOVERY = 80

# Cooked food base thirst recovery
COOKED_THIRST_RECOVERY = 10

# Cooked Foods that count as watery and give extra thirst recovery
WATERY_FOODS = ['Stew', 'Soup', 'Gumbo', 'Broth', 'Ramen', 'Elixir']

# Watery cooked food thirst recover
COOKED_WATERY_THIRST_RECOVERY = 40

# How much console output you see (Possible values "VERBOSE", "DEBUG", "INFO")
LOG_LEVEL = "INFO"
```

## Executable Creation

The executable was created with PyInstaller:  
`python -m PyInstaller -F -n "Survivalistic Parser" survivalistic_parser.py`
