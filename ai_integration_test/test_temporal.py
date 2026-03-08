import pytest
import time


def test_temporal_filtering(client):
    """
    Ensures that at_timestamp correctly filters relationships.
    Scenario:
    1. Create Adversary 'APT1'
    2. Create Infrastructure '9.9.9.9'
    3. Link 'APT1' -> '9.9.9.9' from T1 to T2.
    4. Link 'APT1' -> '9.9.9.9' from T3 onwards.
    5. Query at T1.5 (Expect link)
    6. Query at T2.5 (Expect NO link)
    7. Query at T4 (Expect link)
    """
    # 1. Setup Nodes
    resp_adv = client.post("/adversaries/", json={"name": "APT1"})
    adv_uid = resp_adv.json()["uid"]
    resp_infra = client.post(
        "/infrastructure/", json={"value": "9.9.9.9", "infra_type": "ip"}
    )
    infra_uid = resp_infra.json()["uid"]

    T1, T2, T3 = 1000.0, 2000.0, 3000.0

    # 2. Link T1 -> T2
    client.post(
        "/relationships/",
        json={
            "source_uid": adv_uid,
            "target_uid": infra_uid,
            "rel_type": "USES_INFRA",
            "valid_from": T1,
            "valid_to": T2,
        },
    )

    # 3. Link T3 onwards
    client.post(
        "/relationships/",
        json={
            "source_uid": adv_uid,
            "target_uid": infra_uid,
            "rel_type": "USES_INFRA",
            "valid_from": T3,
        },
    )

    # 4. Check at T1.5 (1500)
    resp1 = client.get(f"/adversaries/{adv_uid}/relationships?at=1500")
    assert len(resp1.json()) == 1

    # 5. Check at T2.5 (2500)
    resp2 = client.get(f"/adversaries/{adv_uid}/relationships?at=2500")
    assert len(resp2.json()) == 0

    # 6. Check at T4 (4000)
    resp3 = client.get(f"/adversaries/{adv_uid}/relationships?at=4000")
    assert len(resp3.json()) == 1
