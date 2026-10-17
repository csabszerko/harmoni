#!/usr/bin/env bash
# Build a local, unsigned macOS application bundle at dist/Harmoni.app.
# Intended for use on this Mac; distribution requires separate signing/notarization.

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

BUILD_VENV="$PROJECT_DIR/.build-venv"
BIN_DIR="$PROJECT_DIR/bin"
ICONSET_DIR="$PROJECT_DIR/build/Harmoni.iconset"
ICON_PATH="$PROJECT_DIR/build/Harmoni.icns"
PYINSTALLER_WORK_DIR="$PROJECT_DIR/build/pyinstaller/Harmoni"
DIST_APP="$PROJECT_DIR/dist/Harmoni.app"

if [[ "$(uname)" != "Darwin" ]]; then
  echo "This script must be run on macOS."
  exit 1
fi

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew is required to bundle FFmpeg. Install it from https://brew.sh/."
  exit 1
fi

echo "Installing build dependencies..."
python3 -m venv "$BUILD_VENV"
"$BUILD_VENV/bin/python" -m pip install --upgrade pip
"$BUILD_VENV/bin/python" -m pip install -r requirements.txt pyinstaller

FFMPEG_PREFIX="$(brew --prefix ffmpeg 2>/dev/null || true)"
if [[ ! -x "$FFMPEG_PREFIX/bin/ffmpeg" ]]; then
  echo "Installing FFmpeg with Homebrew..."
  brew install ffmpeg
  FFMPEG_PREFIX="$(brew --prefix ffmpeg)"
fi

mkdir -p "$BIN_DIR"
cp "$FFMPEG_PREFIX/bin/ffmpeg" "$BIN_DIR/ffmpeg"
cp "$FFMPEG_PREFIX/bin/ffprobe" "$BIN_DIR/ffprobe"

echo "Downloading bundled yt-dlp..."
curl --fail --location \
  "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_macos" \
  --output "$BIN_DIR/yt-dlp"
chmod +x "$BIN_DIR/yt-dlp"

echo "Creating application icon..."
rm -rf "$ICONSET_DIR"
mkdir -p "$ICONSET_DIR"
for size in 16 32 128 256 512; do
  sips -z "$size" "$size" gui/resources/icons/app/app_icon.png \
    --out "$ICONSET_DIR/icon_${size}x${size}.png" >/dev/null
  doubled=$((size * 2))
  sips -z "$doubled" "$doubled" gui/resources/icons/app/app_icon.png \
    --out "$ICONSET_DIR/icon_${size}x${size}@2x.png" >/dev/null
done
iconutil -c icns "$ICONSET_DIR" -o "$ICON_PATH"

QT_UNUSED=(
  QtWebEngineCore QtWebEngineWidgets QtWebEngineQuick QtQml QtQuick
  QtQuickWidgets QtQuick3D QtQuick3DRuntimeRender QtMultimedia
  QtMultimediaWidgets QtPdf QtPdfWidgets QtDesigner QtCharts
  QtDataVisualization QtSensors QtPositioning QtLocation QtBluetooth QtNfc
  QtSerialPort QtSerialBus QtScxml QtStateMachine QtTest QtHelp QtWebSockets
  QtWebChannel QtNetworkAuth QtRemoteObjects QtTextToSpeech Qt3DCore
  Qt3DRender Qt3DInput Qt3DLogic Qt3DAnimation Qt3DExtras QtSql QtSvg
  QtSvgWidgets
)
QT_EXCLUDE_ARGS=()
for module in "${QT_UNUSED[@]}"; do
  QT_EXCLUDE_ARGS+=(--exclude-module "PySide6.$module")
done

echo "Building dist/Harmoni.app..."
if [[ -e "$PYINSTALLER_WORK_DIR" && ! -O "$PYINSTALLER_WORK_DIR" ]] || \
   [[ -e "$DIST_APP" && ! -O "$DIST_APP" ]]; then
  echo "Error: an earlier generated bundle is owned by another user."
  echo "Run this once, then rerun this script:"
  echo "  sudo chown -R \"$USER\":staff \"$PYINSTALLER_WORK_DIR\" \"$PROJECT_DIR/dist/Harmoni\" \"$DIST_APP\""
  exit 1
fi

"$BUILD_VENV/bin/pyinstaller" \
  --noconfirm \
  --windowed \
  --onedir \
  --name Harmoni \
  --distpath dist \
  --workpath build/pyinstaller \
  --specpath build \
  --icon "$ICON_PATH" \
  --hidden-import colorama \
  --add-data "$PROJECT_DIR/gui/resources/icons:gui/resources/icons" \
  --add-data "$PROJECT_DIR/config.json.example:." \
  --add-data "$PROJECT_DIR/data:data" \
  --add-binary "$BIN_DIR/ffmpeg:bin" \
  --add-binary "$BIN_DIR/ffprobe:bin" \
  --add-binary "$BIN_DIR/yt-dlp:bin" \
  "${QT_EXCLUDE_ARGS[@]}" \
  gui_main.py

echo
echo "Built: $PROJECT_DIR/dist/Harmoni.app"
echo "Open it with: open '$PROJECT_DIR/dist/Harmoni.app'"
