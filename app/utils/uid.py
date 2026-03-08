import hashlib
import json
from typing import Any, Dict


def generate_deterministic_uid(data: Dict[str, Any]) -> str:
    """
    Generates a deterministic SHA256 hash for a given dictionary of data.
    The data is normalized (keys sorted, strings stripped and lowercased)
    to ensure the same input always produces the same UID.
    """
    # Normalize data: strip and lowercase strings, sort keys
    normalized_data = {}
    for key, value in data.items():
        if isinstance(value, str):
            normalized_data[key] = value.strip().lower()
        else:
            normalized_data[key] = value

    # Sort keys to ensure deterministic JSON string
    sorted_json = json.dumps(normalized_data, sort_keys=True)
    return hashlib.sha256(sorted_json.encode()).hexdigest()
