class DocumentIngester:
    """
    Mock ingester. Since we removed the heavy vector database and embedding models to save storage,
    this class is now a no-op placeholder.
    """
    def __init__(self, db_url: str):
        pass
        
    async def initialize_sample_data(self):
        print("Lightweight mode: Skipped embedding-based document ingestion.")
