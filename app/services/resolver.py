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
        WHERE resolved_node.is_deleted IS NULL OR resolved_node.is_deleted = false
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
        ORDER BY CASE WHEN r.workspace_id IS NULL THEN 1 ELSE 0 END ASC
        WITH rel_type, target_uid, head(collect(r)) AS resolved_rel, head(collect(m)) AS target_node
        WHERE resolved_rel.is_deleted IS NULL OR resolved_rel.is_deleted = false
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

    @staticmethod
    def find_path(
        start_uid: str,
        end_uid: str,
        workspace_id: Optional[str] = None,
        at_timestamp: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Finds the shortest path between two nodes using Memgraph's pathfinding.
        """
        temporal_clause = ""
        params = {
            "start_uid": start_uid,
            "end_uid": end_uid,
            "workspace_id": workspace_id,
            "at_timestamp": at_timestamp
        }
        
        if at_timestamp:
            temporal_clause = """
            AND ALL(r IN relationships(p) WHERE 
                r.valid_from <= $at_timestamp 
                AND (r.valid_to >= $at_timestamp OR r.valid_to IS NULL)
            )
            """

        query = f"""
        MATCH (start {{uid: $start_uid}}), (end {{uid: $end_uid}})
        MATCH p = shortestPath((start)-[*..10]->(end))
        WHERE ALL(n IN nodes(p) WHERE (n.workspace_id = $workspace_id OR n.workspace_id IS NULL) AND (n.is_deleted IS NULL OR n.is_deleted = false))
          AND ALL(r IN relationships(p) WHERE (r.workspace_id = $workspace_id OR r.workspace_id IS NULL) AND (r.is_deleted IS NULL OR r.is_deleted = false))
          {temporal_clause}
        RETURN p
        """
        
        results = db.execute_and_fetch(query, parameters=params)
        res_list = list(results)
        if not res_list:
            return []
            
        path = res_list[0]["p"]
        output = []
        for i, node in enumerate(path.nodes):
            node_props = node if isinstance(node, dict) else node._properties
            output.append({
                "type": "node", 
                "data": node_props, 
                "labels": list(node.labels) if hasattr(node, "labels") else ["Node"]
            })
            
            if i < len(path.relationships):
                rel = path.relationships[i]
                rel_props = rel if isinstance(rel, dict) else rel._properties
                output.append({
                    "type": "relationship", 
                    "data": rel_props, 
                    "rel_type": type(rel).__name__
                })
                
        return output
