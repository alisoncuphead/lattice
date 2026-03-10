import re
from typing import Callable, Dict, Any, Optional


def refang(value: str) -> str:
    """
    Refangs common defanged IOC patterns.
    Example: 
      - hxxp://google[.]com -> http://google.com
      - 8.8.8[.]8 -> 8.8.8.8
      - example(.)com -> example.com
    """
    if not isinstance(value, str):
        return value
    
    # Replace [.] and (.) with .
    val = value.replace("[.]", ".").replace("(.)", ".").replace("[t]", "t").replace("(t)", "t")
    # Replace hxxp with http
    val = re.sub(r"^hxxp", "http", val, flags=re.IGNORECASE)
    # Replace [@] or (@) with @
    val = val.replace("[@]", "@").replace("(@)", "@")
    
    return val


class NormalizerRegistry:
    def __init__(self):
        self._normalizers: Dict[str, Callable[[Any], Any]] = {}

    def register(self, name: str):
        def decorator(func: Callable[[Any], Any]):
            self._normalizers[name.lower()] = func
            return func
        return decorator

    def normalize(self, name: str, value: Any) -> Any:
        normalizer = self._normalizers.get(name.lower())
        if normalizer:
            return normalizer(value)
        # Default: strip and lowercase strings
        if isinstance(value, str):
            return refang(value).strip().lower()
        return value


registry = NormalizerRegistry()


@registry.register("ipv4")
def normalize_ipv4(value: str) -> str:
    """
    Normalizes an IPv4 address by removing leading zeros from octets.
    Example: 001.002.003.004 -> 1.2.3.4
    """
    if not isinstance(value, str):
        return value
    val = refang(value).strip()
    parts = val.split(".")
    if len(parts) == 4:
        try:
            return ".".join(str(int(p)) for p in parts)
        except ValueError:
            pass
    return val.lower()


@registry.register("fqdn")
def normalize_fqdn(value: str) -> str:
    """
    Normalizes a Fully Qualified Domain Name.
    Example: EXAMPLE[.]COM. -> example.com
    """
    if not isinstance(value, str):
        return value
    # Remove trailing dot and lowercase
    val = refang(value).strip().rstrip(".").lower()
    return val


@registry.register("email")
def normalize_email(value: str) -> str:
    """
    Normalizes an email address.
    Example: Admin@Example.com -> admin@example.com
    """
    if not isinstance(value, str):
        return value
    return value.strip().lower()


@registry.register("hash")
@registry.register("md5")
@registry.register("sha1")
@registry.register("sha256")
def normalize_hash(value: str) -> str:
    """
    Normalizes cryptographic hashes.
    Example: ABC123DEF -> abc123def
    """
    if not isinstance(value, str):
        return value
    return value.strip().lower()


@registry.register("ja3")
@registry.register("ssl_serial")
def normalize_fingerprint(value: str) -> str:
    """
    Normalizes common fingerprints.
    """
    if not isinstance(value, str):
        return value
    return value.strip().lower()
