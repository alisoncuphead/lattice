from fastapi import APIRouter, Depends, HTTPException
from app.services.lock_manager import LockManager
from app.middleware.workspace import get_current_user

router = APIRouter(prefix="/locks", tags=["Locks"])


@router.post("/{uid}/acquire")
async def acquire_lock(uid: str, user_id: str = Depends(get_current_user)):
    success = LockManager.acquire_lock(uid, user_id)
    if not success:
        locked_by = LockManager.check_lock(uid)
        raise HTTPException(
            status_code=409, detail=f"Node {uid} is already locked by {locked_by}"
        )
    return {"message": "Lock acquired", "uid": uid, "user_id": user_id}


@router.post("/{uid}/release")
async def release_lock(uid: str, user_id: str = Depends(get_current_user)):
    LockManager.release_lock(uid, user_id)
    return {"message": "Lock released", "uid": uid}


@router.get("/{uid}")
async def check_lock(uid: str):
    locked_by = LockManager.check_lock(uid)
    return {"uid": uid, "locked_by": locked_by, "is_locked": locked_by is not None}
