from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.services.tag_manager import TagManager
from app.middleware.workspace import get_active_workspace

router = APIRouter(prefix="/tags", tags=["Tagging"])


@router.get("/search")
async def find_by_tag(
    tag_name: str = Query(..., description="Full path of the tag, e.g., 'actor.apt28'"),
    workspace_id: Optional[str] = Depends(get_active_workspace),
):
    return TagManager.find_entities_by_tag(tag_name, workspace_id)


@router.post("/{entity_uid}")
async def tag_entity(
    entity_uid: str,
    tag_path: str = Query(...),
    valid_from: Optional[float] = None,
    valid_to: Optional[float] = None,
    workspace_id: Optional[str] = Depends(get_active_workspace),
):
    TagManager.tag_entity(entity_uid, tag_path, workspace_id, valid_from, valid_to)
    return {"message": f"Entity {entity_uid} tagged with {tag_path}"}
