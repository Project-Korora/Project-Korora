# Project Korora Emulator - README

# Main file
[emulator.py](../Project_Korora_Emulator/emulator.py)


- A CLI Argument handler that should set up virtual scenarios from existing files (from [config](../Project_Korora_Emulator/config)).
- Allocates resources (memory, data) for virtual scenarios
- Will call ([main.py](../Project_Korora/src/main.py)) via `runpy` to catch exceptions.
- Should return a dictionary of all global variables

## Subfolders:

- [config](../Project_Korora_Emulator/config)
  - Contains JSON files describing virtual scenarios
  - Should have information on what system satellites has
  - What data each sensor receives at a given time
- [data](../Project_Korora_Emulator/data)
  - Contains files for sensor data, radio transmissions, etc.
- [lib](../Project_Korora_Emulator/lib)
  - Contains the emulated modules the satellite to import & use during emulation.
