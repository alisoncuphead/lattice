from typing import Optional, List, Dict, Any
from app.database import db
from app.models.requests import RelationshipCreate

class RelationshipRepository:
    @staticmethod
    def create_relationship(data: RelationshipCreate, workspace_id: Optional[str] = None):
        allowed_types = ["USES_INFRA", "USES_CAPABILITY", "TARGETS_VICTIM", "HAS_TAG"]
        if data.rel_type not in allowed_types:
            raise ValueError(f"Invalid relationship type: {data.rel_type}")

        # Convert datetimes to timestamps (float) for easier Cypher handling
        valid_from = data.valid_from.timestamp()
        valid_to = data.valid_to.timestamp() if data.valid_to else None

        query = f"""
        MATCH (s {{uid: $source_uid}}), (t {{uid: $target_uid}})
        MERGE (s)-[r:{data.rel_type} {{workspace_id: $workspace_id}}]->(t)
        SET r.valid_from = $valid_from,
            r.valid_to = $valid_to,
            r.confidence = $confidence,
            r.description = $description,
            r.is_deleted = false
        RETURN r
        """
        params = {
            "source_uid": data.source_uid,
            "target_uid": data.target_uid,
            "workspace_id": workspace_id,
            "valid_from": valid_from,
            "valid_to": valid_to,
            "confidence": data.confidence,
            "description": data.description
        }
        db.execute(query, parameters=params)

    @staticmethod
    def list_relationships(
        workspace_id: Optional[str] = None, 
        at_timestamp: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Lists all relationships in the stratum with shadow merge and temporal filtering.
        """
        temporal_clause = ""
        params: Dict[str, Any] = {"workspace_id": workspace_id}
        
        if at_timestamp:
            temporal_clause = """
            AND r.valid_from <= $at_timestamp 
            AND (r.valid_to >= $at_timestamp OR r.valid_to IS NULL)
            """
            params["at_timestamp"] = at_timestamp

        query = f"""
        MATCH (s)-[r]->(t)
        WHERE (r.workspace_id = $workspace_id OR r.workspace_id IS NULL)
        {temporal_clause}
        // Shadow merge: For same source, target, and type, pick workspace over production
        WITH s.uid AS source_uid, t.uid AS target_uid, type(r) AS rel_type, r, s, t
        ORDER BY r.workspace_id DESC
        WITH source_uid, target_uid, rel_type, head(collect(r)) AS resolved_rel, head(collect(s)) AS source_node, head(collect(t)) AS target_node
        WHERE resolved_rel.is_deleted IS NULL OR resolved_rel.is_deleted = false
        RETURN resolved_rel, source_node, target_node, rel_type
        """
        results = db.execute_and_fetch(query, parameters=params)
        
        output = []
        for res in results:
            rel = res["resolved_rel"]
            source = res["source_node"]
            target = res["target_node"]
            output.append({
                "relationship": rel if isinstance(rel, dict) else rel._properties,
                "source": source if isinstance(source, dict) else source._properties,
                "target": target if isinstance(target, dict) else target._properties,
                "type": res["rel_type"]
            })
        return output

    @staticmethod
    def delete_relationship(source_uid: str, target_uid: str, rel_type: str, workspace_id: Optional[str] = None):
        if workspace_id is None:
            # Production Hard Delete
            query = f"""
            MATCH (s {{uid: $source_uid}})-[r:{rel_type}]->(t {{uid: $target_uid}})
            WHERE r.workspace_id IS NULL
            DELETE r
            """
            db.execute(query, parameters={
                "source_uid": source_uid,
                "target_uid": target_uid
            })
        else:
            # Workspace Tombstone
            query = f"""
            MATCH (s {{uid: $source_uid}}), (t {{uid: $target_uid}})
            MERGE (s)-[r:{rel_type} {{workspace_id: $workspace_id}}]->(t)
            SET r.is_deleted = true
            """
            db.execute(query, parameters={
                "source_uid": source_uid,
                "target_uid": target_uid,
                "workspace_id": workspace_id
            })
