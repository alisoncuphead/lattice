from typing import Optional, Dict, Any


def get_temporal_clause(at_timestamp: Optional[float], rel_alias: str = "r") -> str:
    """
    Returns a Cypher WHERE clause fragment for temporal filtering.
    """
    if at_timestamp is None:
        return ""

    return f"""
    AND {rel_alias}.valid_from <= $at_timestamp 
    AND ({rel_alias}.valid_to >= $at_timestamp OR {rel_alias}.valid_to IS NULL)
    """
