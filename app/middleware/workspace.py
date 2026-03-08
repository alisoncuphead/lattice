from fastapi import Request, Header, HTTPException
from typing import Optional
from app.database import redis_client

WORKSPACE_HEADER = "X-Lattice-Workspace"


async def get_active_workspace(
    request: Request,
    x_lattice_workspace: Optional[str] = Header(None, alias=WORKSPACE_HEADER),
) -> Optional[str]:
    """
    Dependency to retrieve the active workspace ID.
    Prioritizes:
    1. Header 'X-Lattice-Workspace'
    2. Session-based workspace from Redis (if a session exists)
    """
    # 1. Check Header
    if x_lattice_workspace:
        return x_lattice_workspace

    # 2. Check Session (simplified session logic)
    # In a real app, we'd look up a session cookie in Redis
    session_id = request.cookies.get("session_id")
    if session_id:
        workspace_id = redis_client.get(f"session:{session_id}:workspace")
        if workspace_id:
            return workspace_id

    # If no workspace is provided, it defaults to None (Production base)
    return None
