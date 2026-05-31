"""
NLP Service Main Entrypoint
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing NLP Service... Loading models (Stubbed)")
    yield
    print("Shutting down NLP Service...")

app = FastAPI(
    title="AxonBridge NLP Service",
    description="Multilingual Voice & Language Engine",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "nlp-service", "models_loaded": "stubbed"}
