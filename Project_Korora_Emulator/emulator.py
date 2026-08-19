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
