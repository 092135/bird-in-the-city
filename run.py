"""Launch the original game with its expected asset working directory."""

import os
from pathlib import Path
import runpy
import sys


def main():
    game_dir = Path(__file__).resolve().parent / "main"
    previous_dir = Path.cwd()
    previous_path = sys.path.copy()
    try:
        sys.path.insert(0, str(game_dir))
        os.chdir(game_dir)
        runpy.run_path(str(game_dir / "test.py"), run_name="__main__")
    finally:
        sys.path[:] = previous_path
        os.chdir(previous_dir)


if __name__ == "__main__":
    main()
