class ClinicalEmbedder:
    """
    Mock embedder. Removed sentence-transformers to save 500MB+ of storage.
    """
    def __init__(self):
        pass
        
    def embed_text(self, text: str) -> list[float]:
        return []
