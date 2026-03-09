from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.models.nodes import Capability
from app.repositories.nodes import CapabilityRepository
from app.middleware.workspace import get_active_workspace, get_current_user
from app.services.resolver import ShadowResolver
from app.services.lock_manager import LockManager

router = APIRouter(prefix="/capabilities", tags=["Capabilities"])
repo = CapabilityRepository()


@router.get("/", response_model=List[Capability])
async def list_capabilities(
    workspace_id: Optional[str] = Depends(get_active_workspace), limit: int = 100
):
    return repo.list(workspace_id=workspace_id, limit=limit)


@router.post("/", response_model=Capability)
async def create_capability(
    capability: Capability,
    workspace_id: Optional[str] = Depends(get_active_workspace),
    user_id: str = Depends(get_current_user),
):
    capability.workspace_id = workspace_id
    if not capability.uid:
        capability.uid = Capability.create_uid(
            {"name": capability.name, "version": capability.version}
        )

    # COLLISION CHECK: If node exists, check if it's locked by someone else
    existing = repo.get_by_uid(capability.uid, workspace_id=workspace_id)
    if existing:
        locked_by = LockManager.check_lock(capability.uid)
        if locked_by and locked_by != user_id:
            raise HTTPException(
                status_code=423,
                detail=f"Node {capability.uid} is currently locked by {locked_by}",
            )

    return repo.create(capability)


@router.get("/{uid}", response_model=Capability)
async def get_capability(
    uid: str, workspace_id: Optional[str] = Depends(get_active_workspace)
):
    capability = repo.get_by_uid(uid, workspace_id=workspace_id)
    if not capability:
        raise HTTPException(status_code=404, detail="Capability not found")
    return capability


@router.get("/{uid}/relationships")
async def get_capability_relationships(
    uid: str,
    workspace_id: Optional[str] = Depends(get_active_workspace),
    at: Optional[float] = None,
):
    return ShadowResolver.resolve_relationships(
        start_uid=uid, workspace_id=workspace_id, at_timestamp=at
    )
