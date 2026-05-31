import os
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import axonmd, cds, encounters, agents, nlp, workflows
from app.guidelines.document_ingester import DocumentIngester

app = FastAPI(title="AxonBridge Clinical Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    # Initialize RAG sample data
    db_url = os.getenv("POSTGRES_URL", "postgresql+asyncpg://axonbridge:changeme_secure_password_here@axonbridge-postgres:5432/axonbridge")
    # Clean up sqlalchemy format for asyncpg
    db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    
    ingester = DocumentIngester(db_url)
    asyncio.create_task(ingester.initialize_sample_data())

# Include Routes
app.include_router(axonmd.router, prefix="/api/v1/clinical/axonmd", tags=["AxonMD"])
app.include_router(cds.router, prefix="/api/v1/clinical/cds", tags=["CDS"])
app.include_router(encounters.router, prefix="/api/v1/clinical/encounters", tags=["Encounters"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["Agents"])
app.include_router(nlp.router, prefix="/api/v1/clinical", tags=["NLP"])
app.include_router(workflows.router, prefix="/api/v1/workflows", tags=["Workflows"])

@app.websocket("/api/v1/clinical/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming WS messages if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "clinical-service"}
