# Houdini AutoSave Script
A simple Python-based autosave utility for SideFX Houdini. This script automatically saves your scene at configurable time intervals, helping you avoid data loss and keep versioned backups of your work.


## Features
- Automatic scene saving every _N_ minutes
- Customizable save directory and filename prefix
- Configurable maximum number of backup files to retain
- Lightweight and easy to integrate into any Houdini session


## Requirements
- SideFX Houdini (version 18.0 or later recommended)
- Python 3.x (bundled with Houdini)
- No external Python packages required


## Installation
1. Copy `scripts` folder to "C:/Users/`<USERNAME>`/Documents/houdini20.5/" or whatever Houdini version you are using.
2. Restart Houdini.
3. run the `autosave.py` script from the inside Houdini Python console:
   ```python
   import autosave
   autosave.run()
   ```
4. (Optional) Add the script to a shelf tool:
   - Create a new shelf or select an existing one.
   - Add a button with the following Python callback:
     ```python
     import autosave
     autosave.run()
     ```


## Configuration
Open `scripts/python/autosave.py` and adjust the following variables at the top of the file:
- `SAVE_INTERVAL`: Time interval (in minutes) between each autosave
