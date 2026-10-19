# Validation record

## Compact pixel ammunition HUD — 2026-10-19

- Replaced the large reload panel with ten pixel cartridges beneath the ammo count. Remaining rounds are gold; refilling slots show reload progress in green.
- A small pixel-font instruction appears below capacity, hides when full, and reads RELOADING during an active reload. Power-up labels retain a fixed vertical position.
- Rendered full, partial, empty, and reloading states using real assets and simulated camera input; visually inspected partial and reload views. This change only affects drawing; gameplay/input checks were not rerun.

## Reload anytime and right-side ammunition HUD — 2026-10-19

- Supersedes the empty-magazine-only rule below: any magazine below 10 rounds can now be topped up by holding the left hand open (or E) for 500 ms.
- Ammo is at the upper right. The reload hint/progress panel appears only below 10 rounds; active power-up labels sit underneath without overlapping it. The bottom camera hint no longer repeats the reload prompt.
- All **24 tests passed**, including partial reloads at 0, 3, and 9 rounds, full-magazine exclusion, cancellation, replay, and firing limits.
- Visually inspected full/partial/empty right-side HUD and guide renders with simulated camera input and all power-up labels active. Live-camera accuracy is not newly verified.

## Magazine and open-palm reload — 2026-10-19

- All **24 tests passed** using the project virtual environment, dummy video/audio, real game assets, and simulated inputs.
- Holding fire stops after 10 rounds. Empty shots produce no firing sound and consume no power-up uses. A powered volley consumes one round.
- Only an empty magazine can reload: hold the left palm open (all five fingers extended), or hold E in keyboard mode, for 500 ms. Interrupted detection, shooting, and opening the guide cancel progress. Replay restores 10 rounds.
- Synthetic landmarks check open left palm, folded fingers, right-hand exclusion, and in-plane rotation. These do not establish real-camera recognition accuracy.
- Visually inspected 800 × 600 camera-mode empty-magazine/progress and controls-guide renders. No live-camera playtest or real audio output is claimed.
- Updated the Mac installer's pinned gameplay revision to `8dd5e4dced1f491d1d25315a3c8ae77de322cc6b` and checked shell syntax. The earlier full installer validation below was for the previous build; a fresh network installation was not repeated for this change.

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
