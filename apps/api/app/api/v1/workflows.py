"""
AxonBridge — Workflow Routes
"""

import uuid
from typing import List

from fastapi import APIRouter, Depends, Query, HTTPException

from app.api.deps import (
    get_current_tenant_id,
    get_current_user,
    require_permission,
)
from app.models.user import User
from app.schemas.common import PaginatedResponse, IDResponse, DeleteResponse
from app.services.workflow_orchestrator import workflow_orchestrator
from pydantic import BaseModel

router = APIRouter(prefix="/workflows", tags=["Workflows"])

class WorkflowAnalyzeRequest(BaseModel):
    workflow_type: str
    text: str


# Mock storage for Phase 2
_mock_workflows = []

@router.get("", response_model=PaginatedResponse[dict])
async def list_workflows(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    _: User = Depends(require_permission("workflow", "read")),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
):
    """List workflow templates for the current tenant."""
    return PaginatedResponse.create(items=_mock_workflows, total=len(_mock_workflows), page=page, per_page=per_page)

@router.post("", response_model=IDResponse, status_code=201)
async def create_workflow(
    data: dict,
    current_user: User = Depends(require_permission("workflow", "create")),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
):
    """Create a new workflow template."""
    new_id = str(uuid.uuid4())
    workflow = {"id": new_id, **data}
    _mock_workflows.append(workflow)
    return IDResponse(id=uuid.UUID(new_id), message="Workflow created successfully")

@router.post("/{workflow_id}/execute", response_model=dict)
async def execute_workflow(
    workflow_id: uuid.UUID,
    data: dict,
    current_user: User = Depends(require_permission("workflow", "execute")),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
):
    """Execute a workflow (kicks off Temporal worker)."""
    # Trigger temporal workflow execution here
    execution_id = str(uuid.uuid4())
    return {"execution_id": execution_id, "status": "started", "message": "Workflow execution started"}

@router.post("/analyze")
async def analyze_workflow(request: WorkflowAnalyzeRequest):
    """Dynamically process unstructured text via LLM based on workflow type."""
    try:
        result = await workflow_orchestrator.process_workflow(request.workflow_type, request.text)
        return {"status": "success", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM processing failed: {str(e)}")
