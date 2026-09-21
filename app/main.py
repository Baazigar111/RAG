from fastapi import FastAPI, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.db import SessionLocal
from app.pipelines.trace_scrubber import TraceScrubber
from app.parsers.postmortem_parser import PostMortemParser
from app.pipelines.search import HybridSearchEngine
from app.pipelines.synthesizer import RemediationSynthesizer
from app.database.models import LogEmbeddingModel

app = FastAPI(title="LogIntel RAG Backend")

# Enable CORS for Next.js frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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