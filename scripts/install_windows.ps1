# Vocal Separator — Windows Installer
# Run in PowerShell as Administrator:
# irm https://raw.githubusercontent.com/YOUR_USERNAME/vocal-separator/main/scripts/install_windows.ps1 | iex

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Vocal Separator — Windows Installer" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check for Python 3.10+
$python = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $ver = & $cmd -c "import sys; print(sys.version_info >= (3,10))" 2>$null
        if ($ver -eq "True") {
            $python = $cmd
            break
        }
    } catch {}
}

if (-not $python) {
    Write-Host "📦 Python 3.10+ not found. Installing via winget..." -ForegroundColor Yellow
    winget install -e --id Python.Python.3.12 --silent
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    $python = "python"
    Write-Host "✅ Python installed" -ForegroundColor Green
} else {
    Write-Host "✅ Python found: $python" -ForegroundColor Green
}

# 2. Install packages
Write-Host "📦 Installing demucs AI model (may take a few minutes)..." -ForegroundColor Yellow
& $python -m pip install --quiet --upgrade pip
& $python -m pip install --quiet certifi demucs
Write-Host "✅ Packages installed" -ForegroundColor Green

# 3. Install app to AppData
$appDir = "$env:APPDATA\VocalSeparator"
New-Item -ItemType Directory -Force -Path $appDir | Out-Null
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Copy-Item "$scriptDir\..\vocal_separator.py" "$appDir\vocal_separator.py" -Force
Write-Host "✅ App files installed to $appDir" -ForegroundColor Green

# 4. Create Desktop shortcut
$pythonFull = (Get-Command $python).Source
$wsh = New-Object -ComObject WScript.Shell
$shortcut = $wsh.CreateShortcut("$env:USERPROFILE\Desktop\Vocal Separator.lnk")
$shortcut.TargetPath = $pythonFull
$shortcut.Arguments = "`"$appDir\vocal_separator.py`""
$shortcut.WorkingDirectory = $appDir
$shortcut.Description = "Vocal Separator — Split vocals and instrumentals"
$shortcut.Save()
Write-Host "✅ Desktop shortcut created" -ForegroundColor Green

# 5. Also add to Start Menu
$startMenu = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Vocal Separator.lnk"
$shortcut2 = $wsh.CreateShortcut($startMenu)
$shortcut2.TargetPath = $pythonFull
$shortcut2.Arguments = "`"$appDir\vocal_separator.py`""
$shortcut2.WorkingDirectory = $appDir
$shortcut2.Description = "Vocal Separator — Split vocals and instrumentals"
$shortcut2.Save()
Write-Host "✅ Start Menu shortcut created" -ForegroundColor Green

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "   Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "   -> Double-click 'Vocal Separator' on your Desktop"
Write-Host "   -> Your browser opens automatically"
Write-Host "   -> Close the terminal window to quit"
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
