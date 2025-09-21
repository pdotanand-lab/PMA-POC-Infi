import os
import subprocess
import tempfile
import shutil
from typing import Tuple

def check_ffmpeg_available() -> bool:
    """Check if ffmpeg is available in PATH."""
    return shutil.which("ffmpeg") is not None

def extract_audio_to_wav_ffmpeg(input_path: str, out_dir: str, target_sr: int = 16000) -> Tuple[str, float]:
    """Uses ffmpeg to extract audio as mono WAV 16kHz. Returns path and duration seconds."""
    os.makedirs(out_dir, exist_ok=True)
    wav_path = os.path.join(out_dir, os.path.splitext(os.path.basename(input_path))[0] + "_mono16k.wav")

    # Convert to mono 16k wav
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-ac", "1", "-ar", str(target_sr),
        wav_path
    ]
    result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # get duration using ffprobe
    try:
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", input_path],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        duration = float(probe.stdout.strip())
    except Exception:
        duration = 0.0

    return wav_path, duration

def extract_audio_to_wav_pydub(input_path: str, out_dir: str, target_sr: int = 16000) -> Tuple[str, float]:
    """Uses pydub to extract audio as mono WAV 16kHz. Returns path and duration seconds."""
    try:
        from pydub import AudioSegment
    except ImportError:
        raise ImportError("pydub is required for audio processing. Install with: pip install pydub")

    os.makedirs(out_dir, exist_ok=True)
    wav_path = os.path.join(out_dir, os.path.splitext(os.path.basename(input_path))[0] + "_mono16k.wav")

    # Load the audio file (pydub can handle many formats)
    audio = AudioSegment.from_file(input_path)

    # Convert to mono and set sample rate
    audio = audio.set_channels(1)  # mono
    audio = audio.set_frame_rate(target_sr)  # target sample rate

    # Calculate duration in seconds
    duration = len(audio) / 1000.0

    # Export as WAV
    audio.export(wav_path, format="wav")

    return wav_path, duration

def extract_audio_to_wav_librosa(input_path: str, out_dir: str, target_sr: int = 16000) -> Tuple[str, float]:
    """Uses librosa to extract audio as mono WAV 16kHz. Returns path and duration seconds."""
    try:
        import librosa
        import soundfile as sf
    except ImportError:
        raise ImportError("librosa and soundfile are required when ffmpeg is not available. Install with: pip install librosa soundfile")

    os.makedirs(out_dir, exist_ok=True)
    wav_path = os.path.join(out_dir, os.path.splitext(os.path.basename(input_path))[0] + "_mono16k.wav")

    # Load audio file
    y, sr = librosa.load(input_path, sr=target_sr, mono=True)

    # Calculate duration
    duration = len(y) / sr

    # Save as WAV file
    sf.write(wav_path, y, sr)

    return wav_path, duration

def extract_audio_to_wav_moviepy(input_path: str, out_dir: str, target_sr: int = 16000) -> Tuple[str, float]:
    """Uses moviepy to extract audio as mono WAV 16kHz. Returns path and duration seconds."""
    try:
        from moviepy import VideoFileClip
    except ImportError:
        raise ImportError("moviepy is required for video processing. Install with: pip install moviepy")

    os.makedirs(out_dir, exist_ok=True)
    wav_path = os.path.join(out_dir, os.path.splitext(os.path.basename(input_path))[0] + "_mono16k.wav")

    # Load video file and extract audio
    video = VideoFileClip(input_path)
    audio = video.audio

    if audio is None:
        raise ValueError("No audio stream found in the video file")

    # Calculate duration
    duration = audio.duration

    # Export audio as WAV with desired properties
    audio.write_audiofile(
        wav_path,
        fps=target_sr,  # sample rate
        nbytes=2,  # 16-bit
        codec='pcm_s16le',  # PCM 16-bit little-endian
        verbose=False,
        logger=None
    )

    # Clean up
    audio.close()
    video.close()

    return wav_path, duration

def extract_audio_to_wav(input_path: str, out_dir: str, target_sr: int = 16000) -> Tuple[str, float]:
    """Extract audio as mono WAV. Tries multiple methods in order of preference."""

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Try FFmpeg first if available
    if check_ffmpeg_available():
        try:
            return extract_audio_to_wav_ffmpeg(input_path, out_dir, target_sr)
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg failed: {e.stderr.decode() if e.stderr else str(e)}")
            print("Falling back to moviepy...")

    # Try moviepy as primary fallback (includes bundled ffmpeg)
    try:
        return extract_audio_to_wav_moviepy(input_path, out_dir, target_sr)
    except Exception as e:
        print(f"Moviepy failed: {str(e)}")
        print("Falling back to pydub...")

    # Try pydub as secondary fallback
    try:
        return extract_audio_to_wav_pydub(input_path, out_dir, target_sr)
    except Exception as e:
        print(f"Pydub failed: {str(e)}")
        print("Falling back to librosa...")

    # Try librosa as final fallback
    try:
        return extract_audio_to_wav_librosa(input_path, out_dir, target_sr)
    except Exception as e:
        raise RuntimeError(f"Audio extraction failed with all methods. Final error: {str(e)}")
