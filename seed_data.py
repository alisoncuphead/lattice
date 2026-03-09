import requests
import time
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000"

def seed_data():
    print("🚀 Seeding Lattice with advanced Diamond Model data...")
    
    # Wait for API to be ready
    for i in range(10):
        try:
            requests.get(f"{API_BASE}/")
            break
        except requests.exceptions.ConnectionError:
            print(f"Waiting for API (attempt {i+1}/10)...")
            time.sleep(2)
    else:
        print("❌ API not reachable. Seeding failed.")
        return

    now = datetime.now()
    three_months_ago = now - timedelta(days=90)
    two_months_ago = now - timedelta(days=60)
    one_month_ago = now - timedelta(days=30)
    two_weeks_ago = now - timedelta(days=14)

    # Helper for adding relationships
    def add_rel(source, target, rel_type, start, end=None, conf=90, desc="", headers=None):
        payload = {
            "source_uid": source,
            "target_uid": target,
            "rel_type": rel_type,
            "valid_from": start.isoformat() if hasattr(start, 'isoformat') else start,
            "confidence": conf,
            "description": desc
        }
        if end:
            payload["valid_to"] = end.isoformat() if hasattr(end, 'isoformat') else end
        requests.post(f"{API_BASE}/relationships/", json=payload, headers=headers)

    # 1. Production Stratum: The Baseline
    print("📍 Populating Production Stratum...")
    
    # Adversaries
    apt28 = requests.post(f"{API_BASE}/adversaries/", json={"name": "APT28", "actor_type": "nation_state"}).json()
    apt29 = requests.post(f"{API_BASE}/adversaries/", json={"name": "APT29", "actor_type": "nation_state"}).json()
    lazarus = requests.post(f"{API_BASE}/adversaries/", json={"name": "Lazarus Group", "actor_type": "nation_state"}).json()
    
    # Capabilities
    zebrocy = requests.post(f"{API_BASE}/capabilities/", json={"name": "Zebrocy", "cap_type": "malware", "version": "v1.2"}).json()
    cobalt_strike = requests.post(f"{API_BASE}/capabilities/", json={"name": "Cobalt Strike", "cap_type": "toolkit", "version": "4.9"}).json()
    mimikatz = requests.post(f"{API_BASE}/capabilities/", json={"name": "Mimikatz", "cap_type": "toolkit"}).json()
    wellmess = requests.post(f"{API_BASE}/capabilities/", json={"name": "WellMess", "cap_type": "malware"}).json()
    
    # Infrastructure
    ip_c2_1 = requests.post(f"{API_BASE}/infrastructure/", json={"value": "89.34.111.11", "infra_type": "ip", "provider": "DigitalOcean"}).json()
    ip_c2_2 = requests.post(f"{API_BASE}/infrastructure/", json={"value": "104.23.44.12", "infra_type": "ip", "provider": "AWS"}).json()
    ip_shared = requests.post(f"{API_BASE}/infrastructure/", json={"value": "185.123.10.5", "infra_type": "ip", "provider": "Hetzner"}).json()
    domain_update = requests.post(f"{API_BASE}/infrastructure/", json={"value": "windows-update-service.com", "infra_type": "domain"}).json()
    
    # Victims
    vic_mod = requests.post(f"{API_BASE}/victims/", json={"identity": "Ministry of Defense (EU)", "sector": "government", "region": "Europe"}).json()
    vic_bank = requests.post(f"{API_BASE}/victims/", json={"identity": "Global Bank Corp", "sector": "finance", "region": "Global"}).json()
    vic_health = requests.post(f"{API_BASE}/victims/", json={"identity": "City Hospital", "sector": "healthcare", "region": "North America"}).json()

    # Production Links - APT28
    add_rel(apt28["uid"], zebrocy["uid"], "USES_CAPABILITY", three_months_ago)
    add_rel(zebrocy["uid"], ip_c2_1["uid"], "USES_INFRA", three_months_ago, two_months_ago, desc="Historical C2")
    add_rel(zebrocy["uid"], domain_update["uid"], "USES_INFRA", two_months_ago)
    add_rel(domain_update["uid"], ip_shared["uid"], "USES_INFRA", two_months_ago)
    add_rel(apt28["uid"], vic_mod["uid"], "TARGETS_VICTIM", two_months_ago)
    
    # Production Links - APT29
    add_rel(apt29["uid"], wellmess["uid"], "USES_CAPABILITY", three_months_ago)
    add_rel(wellmess["uid"], ip_c2_2["uid"], "USES_INFRA", three_months_ago)
    add_rel(apt29["uid"], vic_mod["uid"], "TARGETS_VICTIM", one_month_ago)
    
    # Production Links - Lazarus
    add_rel(lazarus["uid"], mimikatz["uid"], "USES_CAPABILITY", six_months_ago := (now - timedelta(days=180)))
    add_rel(lazarus["uid"], vic_bank["uid"], "TARGETS_VICTIM", three_months_ago)

    # Common tags in Production
    requests.post(f"{API_BASE}/tags/{apt28['uid']}?tag_path=actor.russia.apt28")
    requests.post(f"{API_BASE}/tags/{apt29['uid']}?tag_path=actor.russia.apt29")
    requests.post(f"{API_BASE}/tags/{lazarus['uid']}?tag_path=actor.north_korea.lazarus")
    requests.post(f"{API_BASE}/tags/{zebrocy['uid']}?tag_path=malware.stealer.zebrocy")

    # 2. Workspace Stratum: 'war-room-alpha' (The Deep Investigation)
    print("🧪 Creating Workspace 'war-room-alpha'...")
    ws_headers = {"X-Lattice-Workspace": "war-room-alpha"}

    # New Discovery: Overlap between APT28 and APT29 via shared infra
    # In this workspace, we found that APT28 also used the 'Shared IP' recently
    add_rel(zebrocy["uid"], ip_shared["uid"], "USES_INFRA", one_month_ago, conf=75, desc="Possible infrastructure reuse", headers=ws_headers)
    
    # New Discovery: APT29 targeting Healthcare
    add_rel(apt29["uid"], vic_health["uid"], "TARGETS_VICTIM", two_weeks_ago, conf=85, desc="Spearphishing observed", headers=ws_headers)
    
    # Workspace-only node: A new malware variant
    zebrocy_v2 = requests.post(f"{API_BASE}/capabilities/", json={"name": "Zebrocy-Go", "cap_type": "malware", "version": "v2.0"}, headers=ws_headers).json()
    add_rel(apt28["uid"], zebrocy_v2["uid"], "USES_CAPABILITY", two_weeks_ago, headers=ws_headers)
    
    # Shadowing: High confidence override for Lazarus
    requests.post(f"{API_BASE}/adversaries/", json={"name": "Lazarus Group", "actor_type": "nation_state", "aliases": ["Hidden Cobra", "Zink"]}, headers=ws_headers)

    # 3. Workspace Stratum: 'war-room-beta' (Financial Focus)
    print("💰 Creating Workspace 'war-room-beta'...")
    ws_beta_headers = {"X-Lattice-Workspace": "war-room-beta"}
    
    # Lazarus using new infra for banking
    ip_bank_c2 = requests.post(f"{API_BASE}/infrastructure/", json={"value": "45.11.22.33", "infra_type": "ip", "provider": "FastFlux"}, headers=ws_beta_headers).json()
    add_rel(mimikatz["uid"], ip_bank_c2["uid"], "USES_INFRA", one_month_ago, headers=ws_beta_headers)
    add_rel(lazarus["uid"], vic_bank["uid"], "TARGETS_VICTIM", one_month_ago, conf=99, desc="Active campaign detected", headers=ws_beta_headers)

    print("\n✅ Seed complete!")
    print("Explore Production at: http://localhost:5173")
    print("Explore War Room Alpha with Header: X-Lattice-Workspace: war-room-alpha")
    print("Explore War Room Beta with Header: X-Lattice-Workspace: war-room-beta")

if __name__ == "__main__":
    seed_data()
