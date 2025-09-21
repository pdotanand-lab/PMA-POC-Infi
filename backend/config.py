import os
from dotenv import load_dotenv

load_dotenv()

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

OLLAMA_BASE = os.getenv("OLLAMA_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "uploads"))
PROCESSED_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "processed"))
CHROMA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "chroma"))
