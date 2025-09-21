import json
import os
import whisper
from typing import List, Dict, Any
from config import WHISPER_MODEL

# Load whisper model once at module level
_whisper_model = None

def get_whisper_model():
    """Get or load the whisper model."""
    global _whisper_model
    if _whisper_model is None:
        # Use base model if no specific model specified or file doesn't exist
        model_name = "base"
        if WHISPER_MODEL and not WHISPER_MODEL.startswith("/"):
            # If it looks like a model name (not a path), use it
            model_name = WHISPER_MODEL.replace("ggml-", "").replace(".en.gguf", "").replace(".gguf", "")
        try:
            _whisper_model = whisper.load_model(model_name)
        except Exception as e:
            print(f"Failed to load model {model_name}, falling back to base: {e}")
            _whisper_model = whisper.load_model("base")
    return _whisper_model

def transcribe_with_whisper_cpp(audio_path: str, output_dir: str) -> List[Dict[str, Any]]:
    """Transcribe audio using OpenAI Whisper and return list of segments with start, end, text."""
    os.makedirs(output_dir, exist_ok=True)

    try:
        model = get_whisper_model()

        # First try direct transcription (requires ffmpeg)
        try:
            result = model.transcribe(audio_path, language="en")
        except Exception as whisper_error:
            print(f"Direct Whisper transcription failed: {whisper_error}")
            print("Attempting to load audio with librosa and pass as numpy array...")

            # Fallback: Load audio with librosa and pass as numpy array
            try:
                import librosa
                import numpy as np

                # Load the audio file (whisper expects 16kHz)
                audio_data, sr = librosa.load(audio_path, sr=16000, mono=True)

                # Whisper expects audio as float32
                audio_data = audio_data.astype(np.float32)

                # Transcribe with numpy array
                result = model.transcribe(audio_data, language="en")

            except ImportError:
                raise RuntimeError("librosa is required for audio loading when ffmpeg is not available")
            except Exception as librosa_error:
                raise RuntimeError(f"Both direct transcription and librosa fallback failed. Whisper: {whisper_error}, Librosa: {librosa_error}")

        segments = []
        for segment in result.get("segments", []):
            start = float(segment.get("start", 0.0))
            end = float(segment.get("end", 0.0))
            text = segment.get("text", "").strip()
            if text:
                segments.append({"start": start, "end": end, "text": text})

        # If no segments but we have text, create a single segment
        if not segments and result.get("text", "").strip():
            segments.append({
                "start": 0.0,
                "end": 0.0,
                "text": result["text"].strip()
            })

        # Save the result as JSON for debugging/logging
        base = os.path.splitext(os.path.basename(audio_path))[0]
        json_path = os.path.join(output_dir, f"{base}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"segments": segments, "text": result.get("text", "")}, f, indent=2)

        return segments

    except Exception as e:
        raise RuntimeError(f"Whisper transcription failed: {str(e)}")
