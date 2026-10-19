# Validation record

Validated on 2026-10-09, macOS ARM64 (Apple M2 Pro), Python 3.12.14.

## Completed

- Created a new project virtual environment and installed `requirements.txt` successfully.
- Ran `python -m unittest discover -s tests -v`: **15 tests passed**.
- Checked camera-open failure, model-initialization failure, mid-session input failure, keyboard fallback in the same frame, retry, and resource release.
- Checked normalized keyboard movement, shooting cooldown, position boundaries, unchanged gesture mapping/smoothing, and timers continuing after camera failure.
- Loaded the real game artwork, font, and audio files with SDL dummy video/audio devices; ran 120 update/render frames and rendered menu, three health states, shield, game-over, and reset.
- Visually inspected rendered menu and camera-fallback views: the bottom control hint fits within the 800 × 600 window. These were synthetic layout checks, not live-camera screenshots.
- Verified root launching from another working directory, clean exit, and CLI help.
- Started the keyboard-mode desktop process with desktop access; it later exited with status 0. Native window inspection timed out, so this is not recorded as a visually verified desktop playthrough.
- Initialized the actual MediaPipe Hands model and processed a blank 320 × 240 image successfully with desktop graphics access. This checks model execution, not hand-recognition accuracy.

## Dependency caveat

`pip check` reports `mediapipe 0.10.21 is not supported on this platform` on this ARM64 machine. The installed universal2 wheel's internal WHEEL metadata declares `cp312-cp312-macosx_14_0_x86_64`. Import and actual Hands inference succeeded here, but the metadata check is **not clean**. No package metadata was modified to hide this result. Full dependency locking or changing the MediaPipe release should be validated separately on target platforms.

Restricted/headless execution cannot create the macOS OpenGL context required by MediaPipe. The model check was repeated successfully with desktop graphics access. The automated game tests use SDL dummy devices and do not require an actual camera.

## Still requires a person

1. Launch `python run.py`, allow camera access if requested, and select PLAY.
2. Confirm right-index movement and left-hand pinch shooting with both hands visible.
3. Move hands out of frame and back: the mode should remain camera.
4. Press F2: the preview should close and WASD / arrows plus Space should work.
5. Press F3: camera control should resume if the selected camera is available.
6. Check actual sound output and a game-over → R restart.

Use Fn with F2/F3 if the keyboard assigns those keys to system media controls. No live-camera gesture playthrough, hardware-disconnection trial, or audible-output confirmation is claimed by the automated checks.

## Replay regression check — 2026-10-10

- Added a game-loop regression that reaches game over through zero health, sends an R key event, checks fresh-round state, and verifies movement and shooting on the next frame.
- Reproduced inherited spawn/combo counters before the fix. Replay now also clears those counters, transient animations, frame counters, slowdown state, and active sounds while retaining the input controller and high score.
- All **16 tests passed** after the fix. Inspected the rendered game-over view with the explicit instruction to click the game window before pressing R.
- These are simulated keyboard events; live-camera control remains outside this check.

## In-game guide and Mac shortcuts

- K selects keyboard; C starts/retries camera. Existing F2/F3 aliases remain available. H or the clickable GUIDE control opens a modal guide from menus, gameplay, or game over.
- The guide explains both input modes, camera setup, replay, and focus; it includes clickable mode selectors. Gameplay updates and input intentions pause while it is open. Esc closes the guide before it can quit the game.
- All **18 tests passed**, including the new letter shortcuts and modal input behavior. Menu and guide renders were visually inspected at 800 × 600. Live-camera recognition is not newly verified by these checks.

## Mac friend installer — 2026-10-19

- Added `scripts/install-macos.sh` and the one-command Mac playtest guide. The installer pins gameplay revision `9babc6d78778a391a0c0bd9a922f50ea0f1cb0db`.
- Completed a fresh installation in a temporary directory on macOS ARM64 using the actual official uv installer, a newly downloaded managed Python 3.12.15, a GitHub source archive, and 27 resolved packages. No existing project virtual environment was reused.
- Launched the installed game's CLI help successfully. Re-ran setup without downloading/reinstalling dependencies, and checked the generated launcher with a path containing spaces.
- Ran all **18 game tests** under the newly installed Python environment: passed. These use dummy video/audio and simulated inputs; they do not validate a friend's webcam or permissions.
- The dependency preparation/download stage took approximately 12 minutes on the tested connection. First-install time depends on network speed; subsequent installed launches need no dependency download.
- Intel Macs and a separate friend's computer were not tested. The existing MediaPipe wheel-metadata caveat above remains relevant.
