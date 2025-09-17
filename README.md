








# Transcript → Bullet Summarizer (Local / Ollama)

Paste any transcript and get a short bullet-point summary.  
Runs **fully on your computer** using **Ollama** (no API key or billing).  
You can also **download the bullets as a PDF**.

---

## ✨ Features
- Paste transcript text → 6–12 concise bullets
- Local LLM via **Ollama** (default: `llama3.2:3b`)
- Simple controls (temperature, chunk size/overlap, max chunks)
- **Download PDF** of the bullets
- Optional: switch to OpenAI later if you want

## 🧱 Tech Stack


- **Python 3.9+**
- **Streamlit** — UI framework for the web app
- **LangChain** — orchestration around LLM calls
- **langchain-community · ChatOllama** — LangChain chat wrapper for local models
- **Ollama** — runs local LLMs (default: `llama3.2:3b`)
- **ReportLab** — generates the PDF download
- **tiktoken** — token utilities (optional, installed via requirements)
- **python-dotenv** — loads environment variables from `.env` (optional)

**Optional (cloud alternative):**
- **langchain-openai** + **OpenAI API** — swap in `ChatOpenAI` if you prefer hosted models

---

## Requirements
- Python 3.9+
- [Ollama](https://ollama.com/) installed and a model pulled (e.g. `llama3.2:3b`)

---

# =========================
# Quickstart (Windows / PowerShell)
# =========================

# [1] Create + activate virtual env
python -m venv .venv
& .\.venv\Scripts\Activate.ps1

# [2] Install Python deps
pip install -r requirements.txt

# [3] Ensure Ollama is installed (installs if missing)
if (!(Test-Path "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe")) {
  winget install -e --id Ollama.Ollama
}

# [4] Point to Ollama executable and show version
$OL = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
& $OL --version

# [5] Start Ollama server in a background window (ignore if already running)
Start-Process -WindowStyle Minimized -FilePath $OL -ArgumentList 'serve'

# [6] Pull a local model (fast, small)
& $OL pull llama3.2:3b

# [7] Run the app
python -m streamlit run app.py

## 🧑‍💻 How to Use

1. Run the Quickstart commands (see above) to start the app:
   - venv activates
   - dependencies install
   - Ollama server runs
   - model `llama3.2:3b` is pulled
   - Streamlit opens at `http://localhost:8501`

2. In the app:
   - Paste your transcript into the big textbox
   - Click **Generate bullets**
   - (Optional) Click **Download PDF** to save the summary

**Sample text to test:**
[Host] Today we’ll learn the Pomodoro Technique for focused work. Pick one clear task, set a 25-minute timer, work without distractions, then take a 5-minute break. After four sessions, take a longer 15–30 minute break. Common mistakes include vague tasks, skipping breaks, and multitasking.


---

## 📁 Files in this Repo

.
├─ app.py # Streamlit app (local Ollama summarizer + PDF export)

├─ requirements.txt # Python dependencies

├─ README.md # Project documentation

├─ .gitignore # Ignore venv, caches, and secrets


└─ .env.example # Placeholder (not needed for local mode)


## License
MIT © Usama Waheed

