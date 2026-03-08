import pytest
from app.models.nodes import Infrastructure, Adversary
from app.models.enums import InfrastructureType


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
