"""
AxonBridge — Agent Service
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Playwright browser engine
    print("Initializing Agent Service...")
    yield
    # Shutdown: Cleanup resources
    print("Shutting down Agent Service...")

app = FastAPI(
    title="AxonBridge Agent Service",
    description="Clinical UI Perception & Automation Layer",
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
    return {"status": "ok", "service": "agent-service"}
