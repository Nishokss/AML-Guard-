from rag.vector_store import save_documents, search

def test_rag_retrieves_evidence(tmp_path, monkeypatch):
    import rag.vector_store as store
    monkeypatch.setattr(store, "STORE", tmp_path / "index.json")
    save_documents([{"document_name":"demo.pdf","page_number":1,"section":"banking","chunk_id":"1","text":"Correspondent banking requires risk assessment and enhanced controls."}])
    assert search("correspondent banking", 1)[0]["document_name"] == "demo.pdf"
