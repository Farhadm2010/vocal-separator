import os
import sys
import shutil
import threading
import subprocess
import tempfile
import json
import webbrowser
import multiprocessing
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

APP_TITLE = "Vocal Separator — Suno Tools"

CPU_CORES = max(1, multiprocessing.cpu_count())
JOBS = max(1, CPU_CORES - 1)


def install(pkg: str) -> None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])


try:
    import certifi
except ImportError:
    install("certifi")
    import certifi

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

try:
    import demucs  # noqa: F401
except ImportError:
    install("demucs")


# Global app state
state = {
    "selected_file": "",
    "output_dir": "",
    "output_format": "wav",
    "model": "mdx_q",
    "status": "ready",       # ready | separating | done | error
    "message": "",
    "saved_dir": "",
}


HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Vocal Separator</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: #F5F8FF;
    display: flex;
    flex-direction: column;
    align-items: center;
    min-height: 100vh;
  }
  header {
    width: 100%;
    background: #4F8DFF;
    color: white;
    text-align: center;
    padding: 18px;
    font-size: 24px;
    font-weight: 700;
  }
  .card {
    background: white;
    border: 1px solid #CFE0FF;
    border-radius: 16px;
    padding: 36px 40px;
    margin-top: 40px;
    width: 560px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
  }
  h2 { font-size: 22px; color: #111827; text-align: center; }
  .sub { color: #5F6B7A; font-size: 14px; text-align: center; }

  /* FILE PICK */
  .file-pick {
    width: 100%;
    background: #EAF2FF;
    border: 2px dashed #4F8DFF;
    border-radius: 12px;
    padding: 0;
    overflow: hidden;
  }
  .file-pick label {
    display: block;
    width: 100%;
    padding: 22px;
    text-align: center;
    font-size: 16px;
    font-weight: 600;
    color: #111827;
    cursor: pointer;
  }
  .file-pick label:hover { background: #d8eaff; }
  .file-pick input[type=file] { display: none; }

  /* FORMAT */
  .format-row {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  .format-row span { font-weight: 600; color: #111827; }
  .fmt-btn {
    padding: 10px 28px;
    border-radius: 8px;
    border: 2px solid #4F8DFF;
    background: white;
    color: #4F8DFF;
    font-size: 15px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.15s;
  }
  .fmt-btn.active {
    background: #4F8DFF;
    color: white;
  }
  .fmt-btn:hover { opacity: 0.85; }

  /* OUTPUT */
  .output-box {
    width: 100%;
    background: #EAF2FF;
    border-radius: 8px;
    padding: 12px 16px;
    color: #5F6B7A;
    font-size: 13px;
    font-weight: 600;
    text-align: center;
    word-break: break-all;
  }

  /* PROGRESS */
  .progress-wrap {
    width: 100%;
    background: #EAF2FF;
    border-radius: 99px;
    height: 12px;
    overflow: hidden;
    display: none;
  }
  .progress-wrap.active { display: block; }
  .progress-bar {
    height: 100%;
    background: #4F8DFF;
    width: 0%;
    border-radius: 99px;
    animation: indeterminate 1.4s infinite ease-in-out;
  }
  @keyframes indeterminate {
    0%   { width: 0%; margin-left: 0%; }
    50%  { width: 60%; margin-left: 20%; }
    100% { width: 0%; margin-left: 100%; }
  }

  /* STATUS */
  .status { font-size: 14px; font-weight: 600; color: #111827; }

  /* SEPARATE BUTTON */
  .sep-btn {
    width: 100%;
    padding: 18px;
    background: #4F8DFF;
    color: white;
    border: none;
    border-radius: 12px;
    font-size: 18px;
    font-weight: 700;
    cursor: pointer;
    transition: background 0.15s;
  }
  .sep-btn:hover { background: #2F6FEA; }
  .sep-btn:disabled { background: #C7DAFF; color: #6B7280; cursor: not-allowed; }

  /* TOAST */
  .toast {
    display: none;
    position: fixed;
    bottom: 30px;
    left: 50%;
    transform: translateX(-50%);
    background: #111827;
    color: white;
    padding: 14px 28px;
    border-radius: 12px;
    font-size: 15px;
    font-weight: 600;
    z-index: 999;
  }
  .toast.show { display: block; }
  .toast.success { background: #16a34a; }
  .toast.error { background: #dc2626; }

  .gpt-banner {
    margin-top: 24px;
    width: 580px;
    background: linear-gradient(135deg, #4F8DFF 0%, #2F6FEA 100%);
    border-radius: 14px;
    padding: 20px 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    color: white;
    margin-bottom: 40px;
  }
  .gpt-banner .gpt-text h3 { font-size: 15px; font-weight: 700; margin-bottom: 4px; }
  .gpt-banner .gpt-text p { font-size: 13px; opacity: 0.9; }
  .gpt-banner a {
    background: white;
    color: #4F8DFF;
    font-weight: 700;
    font-size: 14px;
    padding: 10px 20px;
    border-radius: 8px;
    text-decoration: none;
    white-space: nowrap;
    flex-shrink: 0;
  }
  .gpt-banner a:hover { opacity: 0.9; }
</style>
</head>
<body>
<header>Vocal Separator</header>
<div class="card">
  <h2>Separate Vocals + Instrumental</h2>
  <p class="sub">Create vocals and instrumental as WAV or MP3</p>

  <div class="file-pick">
    <label id="file-label">
      📂 Choose Audio File
      <input type="file" id="file-input" accept=".wav,.mp3,.flac,.m4a,.aac">
    </label>
  </div>

  <div class="format-row">
    <span>Output format:</span>
    <button class="fmt-btn active" id="btn-wav" onclick="setFormat('wav')">WAV</button>
    <button class="fmt-btn" id="btn-mp3" onclick="setFormat('mp3')">MP3</button>
  </div>

  <div class="output-box" id="output-box">Output folder will be created beside the song</div>

  <div class="progress-wrap" id="progress-wrap">
    <div class="progress-bar"></div>
  </div>

  <div class="status" id="status-label">Ready</div>

  <button class="sep-btn" id="sep-btn" onclick="separate()">Separate Vocals</button>
</div>

<div class="toast" id="toast"></div>

<script>
let selectedPath = "";
let outputFormat = "wav";

document.getElementById("file-input").addEventListener("change", function() {
  const file = this.files[0];
  if (!file) return;
  const name = file.name;
  document.getElementById("file-label").innerHTML =
    "✅ " + name + '<input type="file" id="file-input" accept=".wav,.mp3,.flac,.m4a,.aac">';
  document.getElementById("file-input").addEventListener("change", arguments.callee);

  // Send path to server
  fetch("/set_file", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({name: name})
  })
  .then(r => r.json())
  .then(data => {
    selectedPath = data.path;
    document.getElementById("output-box").textContent = "Output: " + data.output_dir;
    document.getElementById("status-label").textContent = "File selected";
  });
});

function setFormat(fmt) {
  outputFormat = fmt;
  document.getElementById("btn-wav").classList.toggle("active", fmt === "wav");
  document.getElementById("btn-mp3").classList.toggle("active", fmt === "mp3");
  fetch("/set_format", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({format: fmt})
  });
}

function separate() {
  if (!selectedPath) {
    showToast("Please choose an audio file first.", "error");
    return;
  }
  document.getElementById("sep-btn").disabled = true;
  document.getElementById("status-label").textContent = "Separating... please wait";
  document.getElementById("progress-wrap").classList.add("active");

  fetch("/separate", {method: "POST"})
  .then(r => r.json())
  .then(data => {
    document.getElementById("progress-wrap").classList.remove("active");
    document.getElementById("sep-btn").disabled = false;
    if (data.ok) {
      document.getElementById("status-label").textContent = "Ready";
      document.getElementById("file-label").innerHTML =
        "📂 Choose Audio File" +
        '<input type="file" id="file-input" accept=".wav,.mp3,.flac,.m4a,.aac">';
      document.getElementById("file-input").addEventListener("change", function() {
        const file = this.files[0];
        if (!file) return;
        const name = file.name;
        document.getElementById("file-label").innerHTML =
          "✅ " + name + '<input type="file" id="file-input" accept=".wav,.mp3,.flac,.m4a,.aac">';
        fetch("/set_file", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({name: name})
        })
        .then(r => r.json())
        .then(d => {
          selectedPath = d.path;
          document.getElementById("output-box").textContent = "Output: " + d.output_dir;
          document.getElementById("status-label").textContent = "File selected";
        });
      });
      document.getElementById("output-box").textContent = "Output folder will be created beside the song";
      selectedPath = "";
      showToast("Done! Saved to: " + data.saved_dir, "success", 6000);
    } else {
      document.getElementById("status-label").textContent = "Error";
      showToast("Error: " + data.error, "error", 8000);
    }
  });
}

function showToast(msg, type, duration) {
  duration = duration || 4000;
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.className = "toast show " + (type || "");
  setTimeout(() => { t.className = "toast"; }, duration);
}
</script>

<div class="gpt-banner">
  <div class="gpt-text">
    <h3>🤖 Need help writing Suno prompts or lyrics?</h3>
    <p>Try Suno Copilot — AI tools built for Suno music creators.</p>
  </div>
  <a href="https://chatgpt.com/g/g-69d8c51ce4808191b256b49d623b99db-suno-copilot-ai-song-generator-v5-5" target="_blank">Open Suno Copilot →</a>
</div>

</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # silence server logs

    def _json(self, data, code=200):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def _html(self):
        body = HTML.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._html()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw) if raw else {}
        except Exception:
            data = {}

        path = urlparse(self.path).path

        if path == "/set_file":
            name = data.get("name", "")
            # Try common locations
            for folder in [
                os.path.expanduser("~/Downloads"),
                os.path.expanduser("~/Desktop"),
                os.path.expanduser("~/Music"),
                os.path.expanduser("~/Documents"),
            ]:
                candidate = os.path.join(folder, name)
                if os.path.isfile(candidate):
                    state["selected_file"] = candidate
                    base = os.path.splitext(name)[0]
                    state["output_dir"] = os.path.join(folder, f"{base}_separated")
                    self._json({"path": candidate, "output_dir": state["output_dir"]})
                    return
            # fallback — file not found in known folders
            self._json({"path": "", "output_dir": "", "error": "File not found in Downloads/Desktop/Music"})

        elif path == "/set_format":
            state["output_format"] = data.get("format", "wav")
            self._json({"ok": True})

        elif path == "/separate":
            if not state["selected_file"]:
                self._json({"ok": False, "error": "No file selected"})
                return
            result = {"ok": False, "error": "Unknown error", "saved_dir": ""}
            event = threading.Event()

            def run():
                temp_dir = tempfile.mkdtemp(prefix="vocal_separator_")
                try:
                    os.makedirs(state["output_dir"], exist_ok=True)
                    cmd = [
                        sys.executable, "-m", "demucs.separate",
                        "--two-stems", "vocals",
                        "-n", state["model"],
                        "--jobs", str(JOBS),
                        "-o", temp_dir,
                        state["selected_file"],
                    ]
                    subprocess.run(cmd, check=True, text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

                    vocals_file = instrumental_file = None
                    for folder, _, files in os.walk(temp_dir):
                        for fn in files:
                            fp = os.path.join(folder, fn)
                            if fn.lower() == "vocals.wav":
                                vocals_file = fp
                            elif fn.lower() == "no_vocals.wav":
                                instrumental_file = fp

                    if not vocals_file or not instrumental_file:
                        raise RuntimeError("vocals.wav or no_vocals.wav not found after separation.")

                    fmt = state["output_format"]
                    if fmt == "wav":
                        shutil.copy2(vocals_file, os.path.join(state["output_dir"], "vocals.wav"))
                        shutil.copy2(instrumental_file, os.path.join(state["output_dir"], "instrumental.wav"))
                    else:
                        _convert_to_mp3(vocals_file, os.path.join(state["output_dir"], "vocals.mp3"))
                        _convert_to_mp3(instrumental_file, os.path.join(state["output_dir"], "instrumental.mp3"))

                    result["ok"] = True
                    result["saved_dir"] = state["output_dir"]
                    state["selected_file"] = ""
                    state["output_dir"] = ""

                except subprocess.CalledProcessError as e:
                    result["error"] = e.stdout if e.stdout else str(e)
                except Exception as e:
                    result["error"] = str(e)
                finally:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    event.set()

            t = threading.Thread(target=run, daemon=True)
            t.start()
            event.wait()
            self._json(result)
        else:
            self._html()


def _convert_to_mp3(input_wav, output_mp3):
    if not shutil.which("ffmpeg"):
        raise RuntimeError(
            "FFmpeg is required for MP3 export. Install with: brew install ffmpeg"
        )
    subprocess.run(
        ["ffmpeg", "-y", "-i", input_wav, "-codec:a", "libmp3lame", "-b:a", "320k", output_mp3],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )


def main():
    port = 7878
    server = HTTPServer(("127.0.0.1", port), Handler)
    url = f"http://127.0.0.1:{port}"
    print(f"Opening Vocal Separator at {url}")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
