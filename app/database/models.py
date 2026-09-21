from sqlalchemy import Column, Integer, String, Text
from pgvector.sqlalchemy import Vector
from app.database.db import Base

class LogEmbeddingModel(Base):
    __tablename__ = "log_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String(100), nullable=False)
    error_code = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    chunk_type = Column(String(50), nullable=False)
    embedding = Column(Vector(1536), nullable=True)
