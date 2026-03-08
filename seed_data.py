import requests
import time
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000"

def seed_data():
    print("Seeding Lattice with simulated CTI data...")
    
    # Wait for API to be ready
    for i in range(5):
        try:
            requests.get(f"{API_BASE}/")
            break
        except requests.exceptions.ConnectionError:
            print("Waiting for API...")
            time.sleep(2)

    # 1. Create Production Data (The Ground Truth)
    print("Creating Production Stratum...")
    
    adv_apt28 = requests.post(f"{API_BASE}/adversaries/", json={
        "name": "APT28", "aliases": ["Fancy Bear", "Pawn Storm"], "actor_type": "nation_state"
    }).json()
    
    cap_zebrocy = requests.post(f"{API_BASE}/capabilities/", json={
        "name": "Zebrocy", "cap_type": "malware", "version": "v1.2"
    }).json()
    
    infra_ip1 = requests.post(f"{API_BASE}/infrastructure/", json={
        "value": "89.34.111.11", "infra_type": "ip", "provider": "DigitalOcean"
    }).json()
    
    victim_gov = requests.post(f"{API_BASE}/victims/", json={
        "identity": "Ministry of Defense (EU)", "sector": "government", "region": "Europe"
    }).json()

    # Create Production Relationships
    now = datetime.now()
    two_months_ago = now - timedelta(days=60)
    one_month_ago = now - timedelta(days=30)
    
    requests.post(f"{API_BASE}/relationships/", json={
        "source_uid": adv_apt28["uid"], "target_uid": cap_zebrocy["uid"],
        "rel_type": "USES_CAPABILITY", "valid_from": two_months_ago.isoformat(), "confidence": 95
    })
    
    requests.post(f"{API_BASE}/relationships/", json={
        "source_uid": cap_zebrocy["uid"], "target_uid": infra_ip1["uid"],
        "rel_type": "USES_INFRA", "valid_from": two_months_ago.isoformat(), "valid_to": one_month_ago.isoformat(),
        "confidence": 90, "description": "C2 Server"
    })
    
    requests.post(f"{API_BASE}/relationships/", json={
        "source_uid": adv_apt28["uid"], "target_uid": victim_gov["uid"],
        "rel_type": "TARGETS_VICTIM", "valid_from": one_month_ago.isoformat()
    })

    # 2. Create Workspace Data (The Investigation)
    print("Creating Workspace 'war-room-alpha'...")
    headers = {"X-Lattice-Workspace": "war-room-alpha"}
    
    # Shadow Merge: Update the IP provider in the workspace
    requests.post(f"{API_BASE}/infrastructure/", json={
        "value": "89.34.111.11", "infra_type": "ip", "provider": "Bulletproof Hosting Inc."
    }, headers=headers)
    
    # New discovery: A new IP linked to Zebrocy currently active
    infra_ip2 = requests.post(f"{API_BASE}/infrastructure/", json={
        "value": "104.23.44.12", "infra_type": "ip", "provider": "AWS"
    }, headers=headers).json()
    
    requests.post(f"{API_BASE}/relationships/", json={
        "source_uid": cap_zebrocy["uid"], "target_uid": infra_ip2["uid"],
        "rel_type": "USES_INFRA", "valid_from": one_month_ago.isoformat(),
        "confidence": 80, "description": "New active C2"
    }, headers=headers)

    # Add Tagging
    requests.post(f"{API_BASE}/tags/{adv_apt28['uid']}?tag_path=actor.russia.apt28")

    print("Seed complete! Open http://localhost:5173 to explore.")

if __name__ == "__main__":
    seed_data()
