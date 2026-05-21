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

# Make sure brew is in PATH (Apple Silicon)
if [ -f "/opt/homebrew/bin/brew" ]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# 2. Always use Homebrew Python (ARM64 native, avoids Intel conflicts)
PYTHON=""
for cmd in /opt/homebrew/bin/python3.12 /opt/homebrew/bin/python3.11 /opt/homebrew/bin/python3.10 /opt/homebrew/bin/python3; do
  if [ -f "$cmd" ]; then
    PYTHON="$cmd"
    break
  fi
done

if [ -z "$PYTHON" ]; then
  echo "📦 Installing Python 3.11 via Homebrew..."
  brew install python@3.11
  PYTHON="/opt/homebrew/bin/python3.11"
else
  echo "✅ Homebrew Python found: $PYTHON"
fi

# 3. Install Python packages
echo "📦 Installing demucs AI model and dependencies..."
"$PYTHON" -m pip install --quiet --upgrade pip
"$PYTHON" -m pip install --quiet certifi demucs diffq
echo "✅ Packages installed"

# 4. Download app file
APP_DIR="$HOME/.vocal-separator"
mkdir -p "$APP_DIR"
curl -fsSL https://raw.githubusercontent.com/Farhadm2010/vocal-separator/main/vocal_separator.py -o "$APP_DIR/vocal_separator.py"
echo "✅ App downloaded"

# 5. Create Desktop launcher
LAUNCHER="$HOME/Desktop/Vocal Separator.command"
printf '#!/bin/bash\nkill $(lsof -ti:7878) 2>/dev/null\n"%s" "%s/vocal_separator.py"\n' "$PYTHON" "$APP_DIR" > "$LAUNCHER"
chmod +x "$LAUNCHER"
echo "✅ Desktop launcher created"

echo ""
echo "======================================"
echo "✅ Installation complete!"
echo ""
echo "   → Double-click 'Vocal Separator.command'"
echo "     on your Desktop to launch"
echo ""
echo "Your browser opens automatically."
echo "Close Terminal window to quit."
echo "======================================"
echo ""
