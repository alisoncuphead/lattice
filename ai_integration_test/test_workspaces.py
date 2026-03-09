import pytest
from app.models.enums import InfrastructureType


def test_shadow_merge_logic(client):
    """
    Tests that workspace versions of nodes 'shadow' production versions.
    Scenario:
    1. Create '8.8.8.8' in Production (Provider: Unknown)
    2. Create '8.8.8.8' in Workspace-A (Provider: Google)
    3. Verify that querying Workspace-A returns 'Google'
    4. Verify that querying Production returns 'Unknown'
    """
    infra_data_prod = {
        "value": "8.8.8.8",
        "infra_type": InfrastructureType.IP,
        "provider": "Unknown",
    }
    infra_data_ws = {
        "value": "8.8.8.8",
        "infra_type": InfrastructureType.IP,
        "provider": "Google",
    }
    workspace_id = "war-room-A"

    # Create in Production
    resp_prod = client.post("/infrastructure/", json=infra_data_prod)
    uid = resp_prod.json()["uid"]

    # Create in Workspace (using X-Lattice-Workspace header)
    resp_ws = client.post(
        "/infrastructure/",
        json=infra_data_ws,
        headers={"X-Lattice-Workspace": workspace_id},
    )
    assert resp_ws.json()["uid"] == uid  # UID must be same
    assert resp_ws.json()["workspace_id"] == workspace_id

    # Retrieve in Workspace
    get_ws = client.get(
        f"/infrastructure/{uid}", headers={"X-Lattice-Workspace": workspace_id}
    )
    assert get_ws.json()["provider"] == "Google"

    # Retrieve in Production
    get_prod = client.get(f"/infrastructure/{uid}")
    assert get_prod.json()["provider"] == "Unknown"


def test_workspace_listing_shadow(client):
    """
    Test that listing nodes in a workspace handles the shadow merge correctly.
    """
    workspace_id = "war-room-B"
    # Create 1 Production and 1 Workspace node (same entity)
    client.post(
        "/infrastructure/",
        json={"value": "1.1.1.1", "infra_type": "ip", "provider": "p1"},
    )
    client.post(
        "/infrastructure/",
        json={"value": "1.1.1.1", "infra_type": "ip", "provider": "p2"},
        headers={"X-Lattice-Workspace": workspace_id},
    )

    # List in Production
    list_prod = client.get("/infrastructure/")
    assert any(x["provider"] == "p1" for x in list_prod.json())

    # List in Workspace
    list_ws = client.get(
        "/infrastructure/", headers={"X-Lattice-Workspace": workspace_id}
    )
    # Should only see 'p2', not 'p1' for the same IP
    assert any(x["provider"] == "p2" for x in list_ws.json())
    assert not any(x["provider"] == "p1" for x in list_ws.json())


def test_tombstone_deletion(client):
    """
    Test that deleting a production node in a workspace creates a tombstone
    that hides the node, and promoting it deletes the production node.
    """
    # 1. Create in Production
    infra = client.post(
        "/infrastructure/", json={"value": "10.10.10.10", "infra_type": "ip"}
    ).json()
    uid = infra["uid"]

    # 2. Delete in Workspace A
    ws_headers = {"X-Lattice-Workspace": "ws-tombstone"}
    del_res = client.delete(f"/infrastructure/{uid}", headers=ws_headers)
    assert del_res.status_code == 200

    # 3. Verify it's GONE in Workspace A
    get_ws = client.get(f"/infrastructure/{uid}", headers=ws_headers)
    assert get_ws.status_code == 404

    # 4. Verify it's still THERE in Production
    get_prod = client.get(f"/infrastructure/{uid}")
    assert get_prod.status_code == 200

    # 5. Promote Workspace A
    promote_res = client.post("/workspaces/ws-tombstone/promote")
    assert promote_res.status_code == 200

    # 6. Now it should be GONE in Production too
    get_prod_after = client.get(f"/infrastructure/{uid}")
    assert get_prod_after.status_code == 404
