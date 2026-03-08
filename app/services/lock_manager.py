from typing import Optional
from app.database import redis_client


class LockManager:
    """
    Implements soft-locking for nodes using Redis.
    """

    @staticmethod
    def acquire_lock(uid: str, user_id: str, ttl: int = 300) -> bool:
        """
        Tries to acquire a lock for a node.
        Returns True if successful, False if already locked by another user.
        ttl defaults to 5 minutes (300 seconds).
        """
        lock_key = f"lock:node:{uid}"
        current_lock = redis_client.get(lock_key)

        if current_lock and current_lock != user_id:
            return False

        redis_client.setex(lock_key, ttl, user_id)
        return True

    @staticmethod
    def release_lock(uid: str, user_id: str):
        """
        Releases a lock if held by the user.
        """
        lock_key = f"lock:node:{uid}"
        current_lock = redis_client.get(lock_key)

        if current_lock == user_id:
            redis_client.delete(lock_key)

    @staticmethod
    def check_lock(uid: str) -> Optional[str]:
        """
        Returns the user_id holding the lock, or None.
        """
        return redis_client.get(f"lock:node:{uid}")
