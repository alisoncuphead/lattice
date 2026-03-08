from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.models.nodes import Victim
from app.repositories.nodes import VictimRepository
from app.middleware.workspace import get_active_workspace
from app.services.resolver import ShadowResolver

router = APIRouter(prefix="/victims", tags=["Victims"])
repo = VictimRepository()


@router.get("/", response_model=List[Victim])
async def list_victims(
    workspace_id: Optional[str] = Depends(get_active_workspace), limit: int = 100
):
    return repo.list(workspace_id=workspace_id, limit=limit)


@router.post("/", response_model=Victim)
async def create_victim(
    victim: Victim, workspace_id: Optional[str] = Depends(get_active_workspace)
):
    victim.workspace_id = workspace_id
    if not victim.uid:
        victim.uid = Victim.create_uid({"identity": victim.identity})
    return repo.create(victim)


@router.get("/{uid}", response_model=Victim)
async def get_victim(
    uid: str, workspace_id: Optional[str] = Depends(get_active_workspace)
):
    victim = repo.get_by_uid(uid, workspace_id=workspace_id)
    if not victim:
        raise HTTPException(status_code=404, detail="Victim not found")
    return victim


@router.get("/{uid}/relationships")
async def get_victim_relationships(
    uid: str,
    workspace_id: Optional[str] = Depends(get_active_workspace),
    at: Optional[float] = None,
):
    return ShadowResolver.resolve_relationships(
        start_uid=uid, workspace_id=workspace_id, at_timestamp=at
    )
