from typing import List, Dict
import numpy as np
import librosa
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

def assign_speakers(audio_path: str, segments: List[Dict], max_speakers: int = 3) -> List[str]:
    """Lightweight speaker clustering using MFCC means per segment.
    Returns list of speaker labels aligned with segments.
    """
    y, sr = librosa.load(audio_path, sr=None, mono=True)
    feats = []
    for seg in segments:
        start = max(0, int(seg['start'] * sr))
        end = min(len(y), int(seg['end'] * sr))
        if end <= start or end - start < sr * 0.2:  # too short
            # pad with zeros to avoid empty MFCC
            seg_y = np.zeros(sr//2, dtype=y.dtype)
        else:
            seg_y = y[start:end]
        mfcc = librosa.feature.mfcc(y=seg_y, sr=sr, n_mfcc=13)
        vec = mfcc.mean(axis=1)
        feats.append(vec)
    X = np.stack(feats, axis=0)

    best_k = 1
    best_score = -1
    for k in range(1, max_speakers+1):
        if k >= len(X):
            break
        km = KMeans(n_clusters=k, n_init=5, random_state=0)
        labels = km.fit_predict(X)
        if k == 1:
            score = 0.0
        else:
            try:
                score = silhouette_score(X, labels)
            except Exception:
                score = 0.0
        if score > best_score:
            best_score = score
            best_k = k

    km = KMeans(n_clusters=best_k, n_init=10, random_state=0)
    labels = km.fit_predict(X)

    # Map to SPEAKER 1..K based on order of first occurrence
    mapping = {}
    counter = 1
    speakers = []
    for lbl in labels:
        if int(lbl) not in mapping:
            mapping[int(lbl)] = f"SPEAKER {counter}"
            counter += 1
        speakers.append(mapping[int(lbl)])
    return speakers
