from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List, Dict, Any
from app.services.resolver import ShadowResolver
from app.services.analysis import AnalysisService
from app.models.requests import ProposeChangeRequest
from app.middleware.workspace import get_active_workspace

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.post("/propose")
async def propose_change(
    request: ProposeChangeRequest,
    workspace_id: Optional[str] = Depends(get_active_workspace),
):
    """
    Suggests a change to a production node by creating a shadow copy in the workspace.
    """
    if not workspace_id:
        raise HTTPException(
            status_code=400, detail="Must be in a workspace to propose changes."
        )

    try:
        return AnalysisService.propose_change(
            uid=request.uid,
            label=request.label,
            properties=request.properties,
            workspace_id=workspace_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

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
