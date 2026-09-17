import json
from pathlib import Path
import numpy as np
from rag.embeddings import get_embedder

STORE = Path(__file__).resolve().parent / "index.json"

def save_documents(documents):
    STORE.write_text(json.dumps(documents, ensure_ascii=True), encoding="utf-8")

def load_documents():
    if not STORE.exists(): return []
    return json.loads(STORE.read_text(encoding="utf-8"))

def build_index():
    documents = load_documents()
    return len(documents)

def search(query, top_k=5):
    documents = load_documents()
    if not documents: return []
    embedder = get_embedder([item["text"] for item in documents])
    query_vector = np.array(embedder.encode([query])[0], dtype=float)
    scored = []
    for document, vector in zip(documents, embedder.encode([item["text"] for item in documents])):
        vector = np.array(vector, dtype=float)
        denominator = np.linalg.norm(query_vector) * np.linalg.norm(vector)
        score = float(np.dot(query_vector, vector) / denominator) if denominator else 0
        scored.append((score, document))
    return [dict(document, score=score) for score, document in sorted(scored, reverse=True, key=lambda item: item[0])[:top_k] if score > 0]
