#!/bin/bash
set -e

echo ""
echo "🎵 Vocal Separator — Mac Installer"
echo "====================================="
echo ""

# 1. Check for Homebrew, install if missing
if ! command -v brew &>/dev/null; then
  echo "📦 Installing Homebrew (needed for Python)..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  if [ -f "/opt/homebrew/bin/brew" ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  fi
else
  echo "✅ Homebrew already installed"
fi

# 2. Find or install Python 3.10+
PYTHON=""
for cmd in python3.12 python3.11 python3.10 python3; do
  if command -v "$cmd" &>/dev/null; then
    VER=$("$cmd" -c "import sys; print(sys.version_info >= (3,10))" 2>/dev/null)
    if [ "$VER" = "True" ]; then
      PYTHON="$cmd"
      break
    fi
  fi
done

if [ -z "$PYTHON" ]; then
  echo "📦 Installing Python 3.12..."
  brew install python@3.12
  PYTHON="python3.12"
else
  echo "✅ Python found: $PYTHON"
fi

# 3. Install Python packages
echo "📦 Installing demucs AI model and dependencies..."
$PYTHON -m pip install --quiet --upgrade pip
$PYTHON -m pip install --quiet certifi demucs
echo "✅ Packages installed"

# 4. Install app files
APP_DIR="$HOME/.vocal-separator"
mkdir -p "$APP_DIR"
curl -fsSL https://raw.githubusercontent.com/Farhadm2010/vocal-separator/main/vocal_separator.py -o "$APP_DIR/vocal_separator.py"
echo "✅ App files installed"

# 5. Create .app bundle in /Applications
APP_PATH="/Applications/Vocal Separator.app"
mkdir -p "$APP_PATH/Contents/MacOS"
mkdir -p "$APP_PATH/Contents/Resources"

PYTHON_FULL=$(command -v $PYTHON)

cat > "$APP_PATH/Contents/MacOS/launch" << LAUNCHER
#!/bin/bash
"$PYTHON_FULL" "$APP_DIR/vocal_separator.py"
LAUNCHER
chmod +x "$APP_PATH/Contents/MacOS/launch"

cat > "$APP_PATH/Contents/Info.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleExecutable</key>
  <string>launch</string>
  <key>CFBundleName</key>
  <string>Vocal Separator</string>
  <key>CFBundleIdentifier</key>
  <string>com.sunotools.vocalseparator</string>
  <key>CFBundleVersion</key>
  <string>1.2</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>CFBundleShortVersionString</key>
  <string>1.2</string>
</dict>
</plist>
PLIST

echo ""
echo "======================================"
echo "✅ Installation complete!"
echo ""
echo "   → Open Finder"
echo "   → Go to Applications"
echo "   → Double-click 'Vocal Separator'"
echo ""
echo "Your browser will open automatically."
echo "Press Ctrl+C in Terminal to quit the app."
echo "======================================"
echo ""
