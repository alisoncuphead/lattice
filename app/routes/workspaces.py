from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.services.merger import MergerService
from app.middleware.workspace import get_active_workspace
from app.database import db

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.get("/", response_model=List[str])
async def list_workspaces():
    """Returns a list of all unique workspace IDs currently in the graph."""
    query = """
    MATCH (n)
    WHERE n.workspace_id IS NOT NULL
    RETURN DISTINCT n.workspace_id AS ws_id
    UNION
    MATCH ()-[r]->()
    WHERE r.workspace_id IS NOT NULL
    RETURN DISTINCT r.workspace_id AS ws_id
    """
    results = db.execute_and_fetch(query)
    # Using a set to ensure unique results across the UNION
    workspaces = {res["ws_id"] for res in results}
    return sorted(list(workspaces))


@router.get("/{workspace_id}/conflicts")
async def get_conflicts(workspace_id: str):
    return MergerService.detect_conflicts(workspace_id)


@router.post("/{workspace_id}/promote")
async def promote_workspace(workspace_id: str):
    MergerService.promote_to_production(workspace_id)
    return {"message": f"Workspace {workspace_id} promoted to Production"}
