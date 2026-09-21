import os
import logging
from dotenv import load_dotenv

load_dotenv()
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.db import SessionLocal, init_db
from app.pipelines.trace_scrubber import TraceScrubber
from app.parsers.postmortem_parser import PostMortemParser
from app.pipelines.search import HybridSearchEngine
from app.pipelines.synthesizer import RemediationSynthesizer
from app.database.models import LogEmbeddingModel

logger = logging.getLogger("uvicorn")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-initialize database tables and pgvector extension on startup
    try:
        init_db()
        logger.info("Database tables and pgvector extension initialized successfully.")
    except Exception as e:
        logger.warning(f"Database initialization deferred or encountered error: {e}")
    yield

app = FastAPI(title="LogIntel RAG Backend", lifespan=lifespan)

# Enable dynamic CORS for frontend integration
raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
allowed_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]
if "*" in allowed_origins:
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "logintel-rag-backend"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class LogPayload(BaseModel):
    service_name: str
    error_code: str
    severity: str
    raw_log: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the LogIntel RAG API"}

@app.post("/api/v1/triage")
def triage_error(payload: LogPayload, db: Session = Depends(get_db)):
    # 1. Sanitize raw log
    scrubber = TraceScrubber()
    clean_log = scrubber.scrub(payload.raw_log)
    
    # 2. Search for similar historical chunks using vector similarity
    search_engine = HybridSearchEngine(db)
    dummy_vector = [0.0] * 1536
    results = search_engine.search_similar(
        query_embedding=dummy_vector, 
        query_text=payload.error_code, 
        service_name=payload.service_name
    )
    
    retrieved_contents = [r.content for r in results]
    
    # 3. Synthesize Remediation
    synthesizer = RemediationSynthesizer()
    diagnosis = synthesizer.synthesize(clean_log, retrieved_contents)
    
    return {
        "service_name": payload.service_name,
        "error_code": payload.error_code,
        "sanitized_log": clean_log,
        "diagnosis": diagnosis
    }

@app.post("/api/v1/ingest")
async def ingest_postmortem(
    service_name: str, 
    error_code: str, 
    severity: str, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    content = await file.read()
    text_content = content.decode("utf-8")
    
    # 1. Parse markdown into semantic segments
    parser = PostMortemParser()
    chunks = parser.parse(text_content)
    
    # 2. Save each segment into PostgreSQL using correct dot notation
    for chunk in chunks:
        dummy_embedding = [0.1] * 1536 
        
        db_record = LogEmbeddingModel(
            service_name=service_name,
            error_code=error_code,
            severity=severity,
            content=chunk.content,
            chunk_type=getattr(chunk, 'type', 'general'),
            embedding=dummy_embedding
        )
        db.add(db_record)
    
    db.commit()
    return {"status": "success", "chunks_ingested": len(chunks)}