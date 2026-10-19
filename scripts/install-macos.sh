#!/bin/bash
# Install a tested game revision without Git, Homebrew, sudo, or shell changes.
set -euo pipefail

if [[ "$(uname -s)" != Darwin ]]; then
    echo 'This installer is for macOS.' >&2
    exit 1
fi

GAME_REVISION=50b9edfb7c4b3e9e2e61b12f6df2287f9ff907db
GAME_HOME="${BIRD_INSTALL_DIR:-$HOME/Library/Application Support/BirdInTheCity}"
GAME_SOURCE="$GAME_HOME/releases/$GAME_REVISION"
GAME_UV="$GAME_HOME/tools/uv"
GAME_LAUNCHER="$GAME_HOME/Play Bird in the City.command"
GAME_TEMP="$(mktemp -d "${TMPDIR:-/tmp}/bird-install.XXXXXX")"
trap 'rm -rf "$GAME_TEMP"' EXIT
trap 'echo "Installation stopped. Check the error above and run the command again to retry." >&2' ERR

mkdir -p "$GAME_HOME/releases"
export UV_CACHE_DIR="$GAME_HOME/cache"
export UV_PYTHON_INSTALL_DIR="$GAME_HOME/python"
export UV_PYTHON_BIN_DIR="$GAME_HOME/python-bin"
export MPLCONFIGDIR="$GAME_HOME/matplotlib"

if [[ ! -x "$GAME_UV" ]]; then
    echo '[1/4] Downloading the Python environment manager...'
    curl --fail --location --retry 3 --connect-timeout 20 \
        https://astral.sh/uv/install.sh -o "$GAME_TEMP/install-uv.sh"
    UV_INSTALL_DIR="$GAME_HOME/tools" UV_NO_MODIFY_PATH=1 \
        /bin/sh "$GAME_TEMP/install-uv.sh"
fi

if [[ ! -f "$GAME_SOURCE/run.py" ]]; then
    echo '[2/4] Downloading Bird in the City...'
    curl --fail --location --retry 3 --connect-timeout 20 \
        "https://codeload.github.com/092135/bird-in-the-city/zip/$GAME_REVISION" \
        -o "$GAME_TEMP/game.zip"
    /usr/bin/unzip -q "$GAME_TEMP/game.zip" -d "$GAME_TEMP"
    mv "$GAME_TEMP/bird-in-the-city-$GAME_REVISION" "$GAME_SOURCE"
fi

if [[ ! -x "$GAME_HOME/venv/bin/python" ]]; then
    echo '[3/4] Preparing Python 3.12 (no system Python changes)...'
    "$GAME_UV" venv --managed-python --python 3.12 "$GAME_HOME/venv"
fi

if [[ ! -f "$GAME_HOME/installed-requirements.txt" ]] || \
   ! cmp -s "$GAME_SOURCE/requirements.txt" "$GAME_HOME/installed-requirements.txt"; then
    echo '[4/4] Installing game libraries. The first download may take several minutes...'
    "$GAME_UV" pip install --python "$GAME_HOME/venv/bin/python" \
        --only-binary=:all: --requirement "$GAME_SOURCE/requirements.txt"
    cp "$GAME_SOURCE/requirements.txt" "$GAME_HOME/installed-requirements.txt"
fi

# The launcher uses absolute, safely quoted paths and works offline after setup.
{
    printf '%s\n' '#!/bin/bash' 'set -euo pipefail'
    printf 'GAME_HOME=%q\n' "$GAME_HOME"
    printf 'GAME_SOURCE=%q\n' "$GAME_SOURCE"
    cat <<'LAUNCHER'
export MPLCONFIGDIR="$GAME_HOME/matplotlib"
cd "$GAME_SOURCE"
echo 'Click PLAY. Right index finger: move; left pinch: shoot.'
echo '10 rounds per magazine. Open all LEFT fingers for 0.5s; keyboard: hold E.'
echo 'K: keyboard | C: camera | H: guide | R: replay after game over'
"$GAME_HOME/venv/bin/python" "$GAME_SOURCE/run.py" "$@"
LAUNCHER
} > "$GAME_LAUNCHER"
chmod +x "$GAME_LAUNCHER"

# Do not overwrite an unrelated file in Applications.
GAME_SHORTCUT="$HOME/Applications/Bird in the City.command"
if [[ -z "${BIRD_INSTALL_DIR:-}" ]] && [[ ! -e "$GAME_SHORTCUT" && ! -L "$GAME_SHORTCUT" ]]; then
    mkdir -p "$HOME/Applications"
    ln -s "$GAME_LAUNCHER" "$GAME_SHORTCUT"
fi

echo
echo "Installed. To play next time, double-click: $GAME_LAUNCHER"
echo 'If macOS asks for camera access, allow it for the launching app.'
echo 'If camera control is unavailable, press K for keyboard controls.'
# Keep stdin attached to the terminal when the installer was piped into bash.
if [[ -t 1 ]]; then
    /bin/bash "$GAME_LAUNCHER" "$@" < /dev/tty
else
    /bin/bash "$GAME_LAUNCHER" "$@"
fi
