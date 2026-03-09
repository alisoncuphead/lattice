import pytest
from app.models.nodes import Infrastructure, Adversary, Capability, Victim, Tag
from app.models.enums import InfrastructureType, ActorType, CapabilityType


def test_infrastructure_crud(client):
    """
    Ensures that infrastructure nodes can be created, retrieved,
    and maintain deterministic UIDs.
    """
    infra_data = {
        "value": "8.8.8.8",
        "infra_type": InfrastructureType.IP,
        "provider": "Google",
    }

    # 1. Create In Production
    response = client.post("/infrastructure/", json=infra_data)
    assert response.status_code == 200
    res_json = response.json()
    uid = res_json["uid"]
    assert res_json["value"] == "8.8.8.8"
    assert res_json["workspace_id"] is None

    # 2. Re-create same IP (idempotency check)
    response2 = client.post("/infrastructure/", json=infra_data)
    assert response2.status_code == 200
    assert response2.json()["uid"] == uid

    # 3. Get by UID
    response3 = client.get(f"/infrastructure/{uid}")
    assert response3.status_code == 200
    assert response3.json()["value"] == "8.8.8.8"


def test_adversary_crud(client):
    """
    Test adversary creation and UID generation.
    """
    adv_data = {"name": "APT28", "aliases": ["Fancy Bear", "Pawn Storm"]}

    response = client.post("/adversaries/", json=adv_data)
    assert response.status_code == 200
    uid = response.json()["uid"]
    assert response.json()["name"] == "APT28"

    # Get by UID
    response2 = client.get(f"/adversaries/{uid}")
    assert response2.status_code == 200
    assert "Fancy Bear" in response2.json()["aliases"]


def test_capability_crud(client):
    """
    Test capability creation and UID generation.
    """
    cap_data = {
        "name": "Zebrocy",
        "cap_type": CapabilityType.MALWARE,
        "version": "v1.2",
        "hash": "abcdef123456"
    }

    response = client.post("/capabilities/", json=cap_data)
    assert response.status_code == 200
    res = response.json()
    uid = res["uid"]
    assert res["name"] == "Zebrocy"
    assert res["version"] == "v1.2"

    # Get by UID
    response2 = client.get(f"/capabilities/{uid}")
    assert response2.status_code == 200
    assert response2.json()["hash"] == "abcdef123456"


def test_victim_crud(client):
    """
    Test victim creation and UID generation.
    """
    victim_data = {
        "identity": "Ministry of Defense (EU)",
        "sector": "government",
        "region": "Europe"
    }

    response = client.post("/victims/", json=victim_data)
    assert response.status_code == 200
    res = response.json()
    uid = res["uid"]
    assert res["identity"] == "Ministry of Defense (EU)"

    # Get by UID
    response2 = client.get(f"/victims/{uid}")
    assert response2.status_code == 200
    assert response2.json()["sector"] == "government"


def test_tagging_and_hierarchical_search(client):
    """
    Test tag creation, assignment, and recursive search.
    """
    # 1. Create an Adversary
    adv = client.post("/adversaries/", json={"name": "Test Actor"}).json()
    adv_uid = adv["uid"]

    # 2. Tag with a nested path
    # Endpoint is /tags/{uid}?tag_path=...
    tag_response = client.post(f"/tags/{adv_uid}?tag_path=actor.russia.test")
    assert tag_response.status_code == 200

    # 3. Search for the top-level tag
    search_response = client.get("/tags/search?tag_name=actor")
    assert search_response.status_code == 200
    results = search_response.json()
    # It should find our "Test Actor" because actor.russia.test is under actor
    uids = [r["uid"] for r in results]
    assert adv_uid in uids

    # 4. Search for the mid-level tag
    search_response2 = client.get("/tags/search?tag_name=actor.russia")
    assert search_response2.status_code == 200
    uids2 = [r["uid"] for r in results]
    assert adv_uid in uids2

    # 5. Search for a sibling tag (should NOT find the actor)
    search_response3 = client.get("/tags/search?tag_name=actor.china")
    assert search_response3.status_code == 200
    uids3 = [r["uid"] for r in search_response3.json()]
    assert adv_uid not in uids3
