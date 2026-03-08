import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import db, redis_client


@pytest.fixture(scope="module")
def client():
    """
    Returns a FastAPI TestClient for integration testing.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def cleanup_db():
    """
    Cleans up the database after each test to ensure isolation.
    WARNING: This will delete all nodes and relationships in the connected Memgraph instance.
    """
    yield
    # We detach delete everything to have a clean slate for the next test
    # In a production-like test env, we'd use a separate test DB
    try:
        db.execute("MATCH (n) DETACH DELETE n")
        # Clear Redis keys used by Lattice
        keys = (
            redis_client.keys("lock:*")
            + redis_client.keys("conflict:*")
            + redis_client.keys("session:*")
        )
        if keys:
            redis_client.delete(*keys)
    except Exception:
        # If DB is not reachable, skip cleanup
        pass


@pytest.fixture
def production_workspace():
    """Helper to represent the production state (workspace_id=None)."""
    return None


@pytest.fixture
def test_workspace():
    """Helper to provide a unique workspace ID for testing."""
    return "test-war-room-123"
