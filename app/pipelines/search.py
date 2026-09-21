from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.models import LogEmbeddingModel

class HybridSearchEngine:
    """
    Combines dense vector similarity search with keyword and metadata filtering.
    """
    def __init__(self, db: Session):
        self.db = db

    def search_similar(self, query_embedding: list, query_text: str = None, service_name: str = None, limit: int = 5):
        query = self.db.query(LogEmbeddingModel)
        
        if service_name:
            query = query.filter(LogEmbeddingModel.service_name == service_name)
            
        # Order by vector cosine distance operator (<=>)
        results = query.order_by(LogEmbeddingModel.embedding.op('<=>')(query_embedding)).limit(limit).all()
        return results
