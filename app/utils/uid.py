import hashlib
import json
from typing import Any, Dict


def generate_deterministic_uid(data: Dict[str, Any]) -> str:
    """
    Generates a deterministic SHA256 hash for a given dictionary of data.
    The data is normalized (keys sorted, strings normalized via registry)
    to ensure the same input always produces the same UID.
    """
    from app.utils.normalization import registry
    
    # Normalize data: use registry for specific types, default to refang + lower
    normalized_data = {}
    
    # If we have a _type, we can use it to find specific normalizers for fields
    node_type = data.get("_type", "").lower()
    
    for key, value in data.items():
        if key == "_type":
            normalized_data[key] = value
            continue
            
        if isinstance(value, str):
            # Try to find a normalizer for this field name OR node_type_field
            normalized_data[key] = registry.normalize(key, value)
        else:
            normalized_data[key] = value

    # Sort keys to ensure deterministic JSON string
    sorted_json = json.dumps(normalized_data, sort_keys=True)
    return hashlib.sha256(sorted_json.encode()).hexdigest()
