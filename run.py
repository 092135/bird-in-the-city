"""Launch the original game with its expected asset working directory."""

import os
from pathlib import Path
import runpy


def main():
    game_dir = Path(__file__).resolve().parent / "main"
    previous_dir = Path.cwd()
    try:
        os.chdir(game_dir)
        runpy.run_path(str(game_dir / "test.py"), run_name="__main__")
    finally:
        os.chdir(previous_dir)


if __name__ == "__main__":
    main()
