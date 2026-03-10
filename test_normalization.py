from app.models.nodes import Infrastructure, Capability
from app.models.enums import InfrastructureType, CapabilityType

def test_ipv4_normalization():
    # Test cases: (input_value, expected_normalized_in_logic)
    # We care that they produce the same UID
    ip1 = "1.2.3.4"
    ip2 = "001.002.003.004"
    ip3 = " 1.2.3.4 "
    
    uid1 = Infrastructure.create_uid({"value": ip1, "infra_type": InfrastructureType.IP})
    uid2 = Infrastructure.create_uid({"value": ip2, "infra_type": InfrastructureType.IP})
    uid3 = Infrastructure.create_uid({"value": ip3, "infra_type": InfrastructureType.IP})
    
    print(f"IP Normalization: {uid1} == {uid2} == {uid3}")
    assert uid1 == uid2 == uid3
    print("✓ IPv4 Normalization passed")

def test_fqdn_normalization():
    dom1 = "EXAMPLE.COM"
    dom2 = "example.com."
    dom3 = " example.com "
    
    uid1 = Infrastructure.create_uid({"value": dom1, "infra_type": InfrastructureType.DOMAIN})
    uid2 = Infrastructure.create_uid({"value": dom2, "infra_type": InfrastructureType.DOMAIN})
    uid3 = Infrastructure.create_uid({"value": dom3, "infra_type": InfrastructureType.DOMAIN})
    
    print(f"FQDN Normalization: {uid1} == {uid2} == {uid3}")
    assert uid1 == uid2 == uid3
    print("✓ FQDN Normalization passed")

def test_hash_normalization():
    h1 = "ABCDEF1234567890"
    h2 = "abcdef1234567890"
    
    uid1 = Capability.create_uid({"name": "test", "hash": h1})
    uid2 = Capability.create_uid({"name": "test", "hash": h2})
    
    print(f"Hash Normalization: {uid1} == {uid2}")
    assert uid1 == uid2
    print("✓ Hash Normalization passed")

if __name__ == "__main__":
    try:
        test_ipv4_normalization()
        test_fqdn_normalization()
        test_hash_normalization()
        print("\nALL NORMALIZATION TESTS PASSED")
    except AssertionError as e:
        print(f"\nTEST FAILED")
        exit(1)
