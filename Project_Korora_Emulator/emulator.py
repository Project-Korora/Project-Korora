import argparse
import os
import sys
from pathlib import Path

def main() -> int:
    """Emulate a satellite scenario. Returns an exit status."""
    parser = argparse.ArgumentParser(
        description="Emulate a scenario."
    )

    # Retrieve configuration data for the scenario, from a directory (path)
    parser.add_argument(
        "config_dir",
        type=Path,
        help="Directory containing config files for the scenario."
    )

    # Retrieve scenario data from a directory.
    parser.add_argument(
        "data_dir",
        type=Path,
        help="Directory that contains the data for the scenario."
    )

    args = parser.parse_args()

    # Convert to absolute file path
    emulator_directory = Path(__file__).resolve().parent

    project_root = emulator_directory.parent
    satellite_main = project_root / "Project_Korora" / "src" / "main.py"

    emulator_lib = emulator_directory / "lib"

    # Turn given arguments into absolute paths
    config_directory = args.config_dir.resolve()
    data_directory = args.data_dir.resolve()


    # Verify all given paths
    for label, path in (
        ("Configuration Directory", config_directory),
        ("Data Directory", data_directory),
        ("Emulator Library Directory", emulator_lib)
    ):
        if not path.is_dir():
            parser.error(f"The given {label} either does not exist, or is not a directory (folder). Looked at {path}")
        if not os.access(path, os.R_OK):
            parser.error(f"The given {label} is not readable. Looked at {path}")

    if not satellite_main.is_file():
        parser.error(f"main.py was not found. Tried to look at {path}")
