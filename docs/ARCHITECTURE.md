# Code guide

[Back to the project](../README.md)

## Entry points

`run.py` resolves `main/` relative to its own file, switches to that working directory, and runs `main/test.py` as `__main__`. It restores the caller's directory on exit, including exceptions. This preserves the original game and its relative font, sound, and high-score paths.

`main/test.py` is the game application, despite its filename. Input adapters now live in `main/controls.py`. The main responsibilities are:

| Class | Responsibility |
| :--- | :--- |
| `GameConfig` | Window settings, damage, progression, asset paths, sounds, and power-up settings |
| `MenuState` | Mouse-operated menu and introduction screens |
| `Game` | Applies input intentions; owns assets, state, collisions, scoring, rendering, audio, and cleanup |
| `InputState` | Immutable movement / target / shooting intention |
| `KeyboardInput` | WASD / arrows and Space; normalized diagonal movement |
| `CameraInput` | Lazy camera dependencies, landmark interpretation, preview, resource cleanup |
| `InputController` | Mode selection, camera-error fallback, retry, and user-facing hints |

## Input pipeline

1. OpenCV captures the selected camera (default `0`), mirrors the frame, resizes it to 320 × 240, and converts BGR to RGB.
2. MediaPipe Hands detects up to two hands and returns landmarks and handedness labels.
3. The right index fingertip (landmark `8`) maps to the left third of the 800 × 600 game window. A smoothing factor of `0.15` reduces abrupt movement.
4. The left thumb tip (`4`) and index tip (`8`) trigger shooting when their normalized 2D distance is below `0.05`, subject to cooldown.
5. Pygame updates hazards, bullets, collisions, power-ups, score, and level, then renders the scene. The loop targets 60 FPS; actual performance depends on the machine and camera.

Keyboard input produces a relative movement vector; camera input produces a normalized absolute target. `Game.handle_input()` applies movement, clamps position, and owns shooting cooldown and invincibility timers. A camera failure closes its resources and reads keyboard input in the same frame, so timers continue. No detected hand produces a neutral intention, without treating it as a camera failure. K / C select the preferred input on the pre-game mode screen; camera capture starts only after the ammo choice. `start_round()` locks settings and shows contextual onboarding. `return_home()` releases camera resources, clears round state, and unlocks configuration. The main loop supports repeated menu/play cycles without closing Pygame.

## Visual state

`Game.draw()` selects both the background and bird animation using health thresholds of 75 and 25. The bird has four animation frames for each of its three living states. Other assets include impact and recovery effects, glass and smog hazards, high-rise enemies, power-up icons, and menu screens.

The death portrait in the README character lineup is supplied presentation artwork; the gameplay animation sets are the three living states above.

## Dependencies

The requirements target Python 3.11 / 3.12 and the original MediaPipe Solutions API. The MediaPipe [0.10.21 release](https://pypi.org/project/mediapipe/0.10.21/) provides Python 3.11 wheels. OpenCV's [contrib distribution](https://pypi.org/project/opencv-contrib-python/4.11.0.86/) supplies `cv2` and is also a MediaPipe dependency; avoid installing multiple OpenCV distributions into the same environment.

This file pins direct dependencies, not the complete transitive dependency tree. Fresh installation and live-camera play should be verified on the target computer before treating this as a reproducible release.

## Known implementation limitations

- Font and sound paths are relative to the working directory. The root launcher supplies the expected directory; these paths have not been rewritten throughout the game.
- `highscore.txt` is local mutable state. An original score file is already tracked in the repository; adding it to `.gitignore` does not untrack it.
- Gameplay timers mostly count frames. The configured FPS is a target, not a measured performance result.
- Automated input and rendering regression checks live in `tests/`. There is no documented player evaluation in this repository.

## Scope of this refactor

The input boundary is implemented. The original game rules, asset directories, camera smoothing, pinch threshold, and shooting cooldown are retained. Configuration, menus, and rendering stay together until a concrete feature calls for another separation.

Validation and remaining manual checks are recorded in [VALIDATION.md](VALIDATION.md).
