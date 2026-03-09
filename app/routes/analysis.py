from fastapi import APIRouter, Depends
from typing import Optional, List, Dict, Any
from app.services.resolver import ShadowResolver
from app.middleware.workspace import get_active_workspace

router = APIRouter(prefix="/analysis", tags=["Analysis"])

@router.get("/path")
async def find_path(
    source_uid: str,
    target_uid: str,
    workspace_id: Optional[str] = Depends(get_active_workspace),
    at: Optional[float] = None
):
    """
    Finds the shortest path between two nodes in the current stratum.
    """
    return ShadowResolver.find_path(
        start_uid=source_uid,
        end_uid=target_uid,
        workspace_id=workspace_id,
        at_timestamp=at
    )
