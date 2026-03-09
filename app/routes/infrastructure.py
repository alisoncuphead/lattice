from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.models.nodes import Infrastructure
from app.repositories.nodes import InfrastructureRepository
from app.middleware.workspace import get_active_workspace, get_current_user
from app.services.resolver import ShadowResolver
from app.services.lock_manager import LockManager

router = APIRouter(prefix="/infrastructure", tags=["Infrastructure"])
repo = InfrastructureRepository()


@router.get("/", response_model=List[Infrastructure])
async def list_infrastructure(
    workspace_id: Optional[str] = Depends(get_active_workspace), limit: int = 100
):
    return repo.list(workspace_id=workspace_id, limit=limit)


@router.post("/", response_model=Infrastructure)
async def create_infrastructure(
    infra: Infrastructure,
    workspace_id: Optional[str] = Depends(get_active_workspace),
    user_id: str = Depends(get_current_user),
):
    # Ensure workspace_id is set
    infra.workspace_id = workspace_id
    # Generate UID if not provided
    if not infra.uid:
        infra.uid = Infrastructure.create_uid({"value": infra.value})

    # COLLISION CHECK: If node exists, check if it's locked by someone else
    existing = repo.get_by_uid(infra.uid, workspace_id=workspace_id)
    if existing:
        locked_by = LockManager.check_lock(infra.uid)
        if locked_by and locked_by != user_id:
            raise HTTPException(
                status_code=423,
                detail=f"Node {infra.uid} is currently locked by {locked_by}",
            )

    return repo.create(infra)


@router.get("/{uid}", response_model=Infrastructure)
async def get_infrastructure(
    uid: str, workspace_id: Optional[str] = Depends(get_active_workspace)
):
    infra = repo.get_by_uid(uid, workspace_id=workspace_id)
    if not infra:
        raise HTTPException(status_code=404, detail="Infrastructure not found")
    return infra


@router.delete("/{uid}")
async def delete_infrastructure(
    uid: str, workspace_id: Optional[str] = Depends(get_active_workspace)
):
    repo.delete(uid, workspace_id=workspace_id)
    return {"message": "Infrastructure deleted"}


@router.get("/{uid}/relationships")
async def get_infra_relationships(
    uid: str,
    workspace_id: Optional[str] = Depends(get_active_workspace),
    at: Optional[float] = None,
):
    return ShadowResolver.resolve_relationships(
        start_uid=uid, workspace_id=workspace_id, at_timestamp=at
    )
