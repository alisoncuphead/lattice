from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.models.nodes import Adversary
from app.repositories.nodes import AdversaryRepository
from app.middleware.workspace import get_active_workspace
from app.services.resolver import ShadowResolver

router = APIRouter(prefix="/adversaries", tags=["Adversaries"])
repo = AdversaryRepository()


@router.get("/", response_model=List[Adversary])
async def list_adversaries(
    workspace_id: Optional[str] = Depends(get_active_workspace), limit: int = 100
):
    return repo.list(workspace_id=workspace_id, limit=limit)


@router.post("/", response_model=Adversary)
async def create_adversary(
    adversary: Adversary, workspace_id: Optional[str] = Depends(get_active_workspace)
):
    adversary.workspace_id = workspace_id
    if not adversary.uid:
        adversary.uid = Adversary.create_uid({"name": adversary.name})
    return repo.create(adversary)


@router.get("/{uid}", response_model=Adversary)
async def get_adversary(
    uid: str, workspace_id: Optional[str] = Depends(get_active_workspace)
):
    adversary = repo.get_by_uid(uid, workspace_id=workspace_id)
    if not adversary:
        raise HTTPException(status_code=404, detail="Adversary not found")
    return adversary


@router.get("/{uid}/relationships")
async def get_adversary_relationships(
    uid: str,
    workspace_id: Optional[str] = Depends(get_active_workspace),
    at: Optional[float] = None,
):
    return ShadowResolver.resolve_relationships(
        start_uid=uid, workspace_id=workspace_id, at_timestamp=at
    )
