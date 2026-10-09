# Code guide

[Back to the project](../README.md)

## Entry points

`run.py` resolves `main/` relative to its own file, switches to that working directory, and runs `main/test.py` as `__main__`. It restores the caller's directory on exit, including exceptions. This preserves the original game and its relative font, sound, and high-score paths.

`main/test.py` is the original application, despite its filename. It contains three classes:

| Class | Responsibility |
| :--- | :--- |
| `GameConfig` | Window settings, damage, progression, asset paths, sounds, and power-up settings |
| `MenuState` | Mouse-operated menu and introduction screens |
| `Game` | Webcam input, assets, game state, collisions, scoring, rendering, audio, and cleanup |

## Input pipeline

1. OpenCV captures camera `0`, mirrors the frame, resizes it to 320 × 240, and converts BGR to RGB.
2. MediaPipe Hands detects up to two hands and returns landmarks and handedness labels.
3. The right index fingertip (landmark `8`) maps to the left third of the 800 × 600 game window. A smoothing factor of `0.15` reduces abrupt movement.
4. The left thumb tip (`4`) and index tip (`8`) trigger shooting when their normalized 2D distance is below `0.05`, subject to cooldown.
5. Pygame updates hazards, bullets, collisions, power-ups, score, and level, then renders the scene. The loop targets 60 FPS; actual performance depends on the machine and camera.

## Visual state

`Game.draw()` selects both the background and bird animation using health thresholds of 75 and 25. The bird has four animation frames for each of its three living states. Other assets include impact and recovery effects, glass and smog hazards, high-rise enemies, power-up icons, and menu screens.

The death portrait in the README character lineup is supplied presentation artwork; the gameplay animation sets are the three living states above.

## Dependencies

The requirements target Python 3.11 and the original MediaPipe Solutions API. The MediaPipe [0.10.21 release](https://pypi.org/project/mediapipe/0.10.21/) provides Python 3.11 wheels. OpenCV's [contrib distribution](https://pypi.org/project/opencv-contrib-python/4.11.0.86/) supplies `cv2` and is also a MediaPipe dependency; avoid installing multiple OpenCV distributions into the same environment.

This file pins direct dependencies, not the complete transitive dependency tree. Fresh installation and live-camera play should be verified on the target computer before treating this as a reproducible release.

## Known implementation limitations

- `init_camera()` records `use_camera = False` on failure, but `handle_input()` still reads the capture directly. The printed keyboard-fallback message does not reflect an implemented control mode.
- Font and sound paths are relative to the working directory. The root launcher supplies the expected directory; these paths have not been rewritten throughout the game.
- `highscore.txt` is local mutable state. An original score file is already tracked in the repository; adding it to `.gitignore` does not untrack it.
- Gameplay timers mostly count frames. The configured FPS is a target, not a measured performance result.
- There is no automated gameplay test suite or documented player evaluation in this repository.

## Suggested next refactor

Separate configuration, camera input, gameplay state, and rendering only alongside regression checks. A useful first boundary is an input adapter that returns movement and shooting intentions, allowing the same game logic to accept either camera or keyboard input. Camera-failure handling can then select a real alternative control mode.

This documentation update adds a discoverable launcher and a dedicated documentation directory while preserving the original gameplay implementation and asset layout.
