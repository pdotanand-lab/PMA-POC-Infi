# Backend (FastAPI)

## Quickstart

1. Create & activate venv

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

2. Install deps

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and edit paths:

- Set `WHISPER_BIN` to your whisper.cpp binary (e.g., `./main` or `whisper`).
- Set `WHISPER_MODEL` to a GGUF model file path (e.g., `./models/ggml-base.en.gguf`).
- Ensure `OLLAMA_BASE` is running locally and you've pulled models:
  ```bash
  ollama pull llama3.1:8b
  ollama pull nomic-embed-text
  ```
- Ensure `ffmpeg` is on PATH.

4. Run API

```bash
bash run.sh

# or:

uvicorn main:app --host 0.0.0.0 --port 8000 --reload

```

Open docs at: http://localhost:8000/docs

## Pipeline

- Upload file -> `/upload`
- Start processing -> `/meetings/{id}/process`
- List meetings -> `/meetings`
- Segments -> `/meetings/{id}/segments`
- Summary -> `/meetings/{id}/summary`
- Search -> `/search?q=...`
- Topic graph -> `/meetings/{id}/graph`

Data is stored in SQLite (`app.db`) and Chroma at `backend/chroma/`.
