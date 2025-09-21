import os
from typing import List, Tuple
import chromadb
from chromadb.config import Settings
import requests
from config import CHROMA_DIR, OLLAMA_BASE, OLLAMA_EMBED_MODEL

def get_chroma_client():
    os.makedirs(CHROMA_DIR, exist_ok=True)
    client = chromadb.PersistentClient(path=CHROMA_DIR, settings=Settings(allow_reset=False))
    return client

def _embed(texts: List[str]) -> List[List[float]]:
    url = f"{OLLAMA_BASE}/api/embeddings"
    embeddings = []

    # Process each text individually since Ollama expects single prompt
    for text in texts:
        payload = {"model": OLLAMA_EMBED_MODEL, "prompt": text}
        r = requests.post(url, json=payload, timeout=300)
        r.raise_for_status()
        data = r.json()
        # Ollama returns {embedding: [...]}
        emb = data.get("embedding", [])
        if emb:
            embeddings.append(emb)

    return embeddings

def upsert_meeting_segments(meeting_id: int, meeting_title: str, segments: List[Tuple[int, str]]):
    client = get_chroma_client()
    coll = client.get_or_create_collection(name="meetings")
    ids = [f"{meeting_id}:{seg_id}" for seg_id, _ in segments]
    texts = [text for _, text in segments]
    metadatas = [{"meeting_id": meeting_id, "meeting_title": meeting_title, "segment_id": seg_id} for seg_id, _ in segments]
    embeddings = _embed(texts)
    coll.upsert(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)

def search(query: str, top_k: int = 8):
    client = get_chroma_client()
    coll = client.get_or_create_collection(name="meetings")

    # Get embeddings for the query
    embeddings = _embed([query])
    if not embeddings or not embeddings[0]:
        return []  # Return empty results if embedding fails

    q_emb = embeddings[0]
    res = coll.query(query_embeddings=[q_emb], n_results=top_k, include=["documents", "distances", "metadatas"])

    # Check if we have results
    if not res.get("ids") or not res["ids"][0]:
        return []  # Return empty results if no matches

    hits = []
    ids_list = res["ids"][0]
    documents_list = res.get("documents", [[]])[0]
    distances_list = res.get("distances", [[]])[0]
    metadatas_list = res.get("metadatas", [[]])[0]

    for i in range(len(ids_list)):
        if i < len(metadatas_list) and i < len(documents_list) and i < len(distances_list):
            md = metadatas_list[i]
            hits.append({
                "meeting_id": md["meeting_id"],
                "meeting_title": md["meeting_title"],
                "segment_id": md["segment_id"],
                "text": documents_list[i],
                "score": float(1.0 - distances_list[i])  # invert distance
            })
    return hits
