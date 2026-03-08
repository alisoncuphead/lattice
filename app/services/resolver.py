from typing import Any, List, Optional, Dict
from app.database import db


class ShadowResolver:
    @staticmethod
    def resolve_nodes(
        label: str, workspace_id: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        query = f"""
        MATCH (n:{label})
        WHERE n.workspace_id = $workspace_id OR n.workspace_id IS NULL
        WITH n.uid AS uid, n
        ORDER BY n.workspace_id DESC
        WITH uid, head(collect(n)) AS resolved_node
        RETURN resolved_node
        LIMIT $limit
        """
        results = db.execute_and_fetch(
            query, parameters={"workspace_id": workspace_id, "limit": limit}
        )
        output = []
        for res in results:
            node = res["resolved_node"]
            output.append(node if isinstance(node, dict) else node._properties)
        return output

    @staticmethod
    def resolve_relationships(
        start_uid: str,
        workspace_id: Optional[str] = None,
        at_timestamp: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        temporal_clause = ""
        params: Dict[str, Any] = {"start_uid": start_uid, "workspace_id": workspace_id}

        if at_timestamp:
            temporal_clause = """
            AND r.valid_from <= $at_timestamp 
            AND (r.valid_to >= $at_timestamp OR r.valid_to IS NULL)
            """
            params["at_timestamp"] = at_timestamp

        query = f"""
        MATCH (n {{uid: $start_uid}})-[r]->(m)
        WHERE (r.workspace_id = $workspace_id OR r.workspace_id IS NULL)
        {temporal_clause}
        WITH type(r) AS rel_type, m.uid AS target_uid, r, m
        ORDER BY r.workspace_id DESC
        WITH rel_type, target_uid, head(collect(r)) AS resolved_rel, head(collect(m)) AS target_node
        RETURN resolved_rel, target_node, rel_type
        """
        results = db.execute_and_fetch(query, parameters=params)

        output = []
        for res in results:
            rel = res["resolved_rel"]
            target = res["target_node"]
            output.append(
                {
                    "relationship": rel if isinstance(rel, dict) else rel._properties,
                    "target": (
                        target if isinstance(target, dict) else target._properties
                    ),
                    "type": res["rel_type"],
                }
            )
        return output
