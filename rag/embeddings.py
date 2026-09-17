import re
from collections import Counter

class LocalEmbedder:
    """Deterministic TF-IDF-like vectors keep demo mode offline and testable."""
    def __init__(self, documents=None):
        terms = set()
        for document in documents or []: terms.update(re.findall(r"[a-z0-9]+", document.lower()))
        self.terms = sorted(terms) or ["regulation"]
    def encode(self, texts):
        return [[Counter(re.findall(r"[a-z0-9]+", text.lower())).get(term, 0) for term in self.terms] for text in texts]

def get_embedder(documents=None):
    return LocalEmbedder(documents)
