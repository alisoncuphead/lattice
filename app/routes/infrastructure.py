from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.models.nodes import Infrastructure
from app.repositories.nodes import InfrastructureRepository
from app.middleware.workspace import get_active_workspace
from app.services.resolver import ShadowResolver

router = APIRouter(prefix="/infrastructure", tags=["Infrastructure"])
repo = InfrastructureRepository()


@router.get("/", response_model=List[Infrastructure])
async def list_infrastructure(
    workspace_id: Optional[str] = Depends(get_active_workspace), limit: int = 100
):
    return repo.list(workspace_id=workspace_id, limit=limit)


@router.post("/", response_model=Infrastructure)
async def create_infrastructure(
    infra: Infrastructure, workspace_id: Optional[str] = Depends(get_active_workspace)
):
    # Ensure workspace_id is set
    infra.workspace_id = workspace_id
    # Generate UID if not provided
    if not infra.uid:
        infra.uid = Infrastructure.create_uid({"value": infra.value})
    return repo.create(infra)


@router.get("/{uid}", response_model=Infrastructure)
async def get_infrastructure(
    uid: str, workspace_id: Optional[str] = Depends(get_active_workspace)
):
    infra = repo.get_by_uid(uid, workspace_id=workspace_id)
    if not infra:
        raise HTTPException(status_code=404, detail="Infrastructure not found")
    return infra


@router.get("/{uid}/relationships")
async def get_infra_relationships(
    uid: str,
    workspace_id: Optional[str] = Depends(get_active_workspace),
    at: Optional[float] = None,
):
    return ShadowResolver.resolve_relationships(
        start_uid=uid, workspace_id=workspace_id, at_timestamp=at
    )
