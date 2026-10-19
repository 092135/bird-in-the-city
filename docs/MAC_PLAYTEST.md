# Mac playtest: one-command setup

Open Terminal and paste:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/092135/bird-in-the-city/main/scripts/install-macos.sh)"
```

The script downloads the game, installs uv from its official installer, prepares a dedicated Python 3.12 environment, installs the game libraries, and starts the game. Git, Homebrew, and administrator access are not required. It keeps its files in `~/Library/Application Support/BirdInTheCity` and does not edit shell profiles or system Python.

The first setup needs an internet connection and downloads several hundred MB. Time depends on access to GitHub, Astral's Python downloads, and PyPI; this is not an instant or universally tested Mac app installer. Modern macOS on Apple Silicon or Intel is the intended target; actual dependency-wheel availability determines support.

The game revision is pinned in the installer so friends receive the same build. Running the command again retries incomplete setup without replacing an existing game install or its high score. The installer itself is fetched from this repository's main branch.

The current build defaults to unlimited ammo. Click PLAY, then choose Unlimited or Limited to start. During play, use the guide or press 1 / 2 to switch. In limited mode, whenever below 10 rounds, open all five left-hand fingers for half a second to reload (keyboard: hold E). Replay keeps the selected mode; a new launch starts with unlimited ammo. Run the installation command again to download this build and update the launcher. Older builds and their score files remain in their release folders; scores are not automatically copied between builds.

## After the window opens

1. Allow camera access if macOS asks. Click PLAY to start camera preview and gameplay.
2. Right index finger moves the bird. Pinch the left thumb and index finger to shoot.
3. Press H or click GUIDE for instructions. K selects keyboard; C retries camera.
4. Keyboard mode uses WASD / arrow keys and Space. Click the game window first.
5. After game over, press R to replay. Esc exits.

If camera permission was denied, review the launching app under System Settings → Privacy & Security → Camera, then relaunch. The installer does not change permissions for you.

## Next time

In Finder, press Shift–Command–G, enter `~/Applications`, and double-click **Bird in the City.command**. The created launcher uses the installed environment directly and does not download dependencies on each launch. You can drag this file to the Desktop for easier access.

If setup fails, share the final error text, Mac chip type, and macOS version. If GitHub or PyPI is unreachable, rerun after the connection is working; dependency downloads cannot be skipped on a fresh machine.

## Implementation references

- [uv official installation](https://docs.astral.sh/uv/getting-started/installation/)
- [uv installer path and shell-profile options](https://docs.astral.sh/uv/reference/installer/)
