from rag.vector_store import search

def retrieve_regulatory_evidence(question, top_k=4):
    results = search(question, top_k)
    return [{key: item[key] for key in ("document_name", "page_number", "section", "chunk_id", "text")} | {"score": item["score"]} for item in results]
