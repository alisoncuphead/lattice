from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
from app.models.requests import RelationshipCreate
from app.repositories.rel_repo import RelationshipRepository
from app.middleware.workspace import get_active_workspace

router = APIRouter(prefix="/relationships", tags=["Relationships"])
repo = RelationshipRepository()

@router.get("/")
async def list_relationships(
    workspace_id: Optional[str] = Depends(get_active_workspace),
    at: Optional[float] = None
):
    return repo.list_relationships(workspace_id=workspace_id, at_timestamp=at)

@router.post("/")
async def create_relationship(
    data: RelationshipCreate,
    workspace_id: Optional[str] = Depends(get_active_workspace)
):
    try:
        repo.create_relationship(data, workspace_id=workspace_id)
        return {"message": f"Relationship {data.rel_type} created from {data.source_uid} to {data.target_uid}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/")
async def delete_relationship(
    source_uid: str,
    target_uid: str,
    rel_type: str,
    workspace_id: Optional[str] = Depends(get_active_workspace)
):
    repo.delete_relationship(source_uid, target_uid, rel_type, workspace_id=workspace_id)
    return {"message": "Relationship deleted successfully"}
