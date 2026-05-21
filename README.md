# 🎵 Vocal Separator

**Free AI-powered tool to split any song into Vocals + Instrumental.**  
Built with [Meta's Demucs](https://github.com/facebookresearch/demucs) · Runs 100% on your computer · No data sent anywhere · No subscription.

> Made by the creator of [Suno Copilot](https://chatgpt.com/g/g-69d8c51ce4808191b256b49d623b99db-suno-copilot-ai-song-generator-v5-5) — AI tools for Suno music creators.

---

## ✨ Features

- 🎤 Separate **vocals** and **instrumental** from any audio file
- ⚡ **Fast mode** (MDX-Q) or **Best Quality** mode (HTDemucs)
- 🖥️ Uses **all your CPU cores** automatically for maximum speed
- 🌐 Clean **browser-based UI** — no clunky desktop app
- 🔒 **100% offline** — your audio never leaves your machine
- 🎵 Output as **WAV** or **MP3 320k**
- ✅ Works on **Mac** and **Windows**

---

## 🚀 Install — Mac (one command, then done forever)

Open **Terminal** and paste this once:

```bash
curl -fsSL https://raw.githubusercontent.com/Farhadm2010/vocal-separator/main/scripts/install_mac.sh -o /tmp/install.sh && bash /tmp/install.sh
```

After that:
- Open **Finder → Applications → Vocal Separator** and double-click
- Your browser opens automatically — done! ✅
- > ✅ Requires Apple Silicon Mac (M1, M2, M3, or M4). Intel Macs not supported yet.

---

## 🚀 Install — Windows (Beta)

Open **PowerShell as Administrator** and paste this once:

```powershell
irm https://raw.githubusercontent.com/Farhadm2010/vocal-separator/main/scripts/install_windows.ps1 | iex
```

After that:
- Double-click **"Vocal Separator"** on your Desktop
- Your browser opens automatically — done! ✅

---

## 🎯 How to Use

1. Click **"Choose Audio File"** — pick any `.mp3`, `.wav`, `.flac`, `.m4a`, or `.aac`
2. Choose **WAV** or **MP3** output
3. Choose **⚡ Fast** or **✨ Best Quality**
4. Click **"Separate Vocals"**
5. Wait 1–3 minutes (first run downloads the AI model ~80MB)
6. Find your files in a `_separated` folder next to your original song

---

## 📁 Output Files

| File | Contents |
|------|----------|
| `vocals.wav` / `vocals.mp3` | Voice only |
| `instrumental.wav` / `instrumental.mp3` | Music without vocals |

---

## ⚡ Speed Tips

- **Fast mode** is 2–3× faster, quality is excellent for most songs
- **Best Quality** mode is better for complex arrangements
- More CPU cores = faster processing (works automatically)
- First run is slower — the AI model (~80MB) downloads once and caches

---

## 🤖 Also check out our GPT Tools for Suno

> [Link to your ChatGPT GPT here]

AI-powered tools to help you write better Suno prompts, lyrics, and song structures.

---

## 🛠 Requirements

| | Mac | Windows |
|--|-----|---------|
| Python | 3.10+ (installer handles it) | 3.10+ (installer handles it) |
| RAM | 4GB minimum, 8GB recommended | 4GB minimum, 8GB recommended |
| Storage | ~500MB (AI model cache) | ~500MB (AI model cache) |
| MP3 output | requires `brew install ffmpeg` | requires [FFmpeg](https://ffmpeg.org) |

---

## 📄 License

MIT — free to use, share, and modify.
