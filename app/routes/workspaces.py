from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.services.merger import MergerService
from app.middleware.workspace import get_active_workspace

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.get("/{workspace_id}/conflicts")
async def get_conflicts(workspace_id: str):
    return MergerService.detect_conflicts(workspace_id)


@router.post("/{workspace_id}/promote")
async def promote_workspace(workspace_id: str):
    MergerService.promote_to_production(workspace_id)
    return {"message": f"Workspace {workspace_id} promoted to Production"}
