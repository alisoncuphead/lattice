from typing import List, Dict, Any, Optional
from app.database import db, redis_client


class MergerService:
    @staticmethod
    def detect_conflicts(workspace_id: str) -> List[Dict[str, Any]]:
        query = """
        MATCH (ws {workspace_id: $workspace_id})
        MATCH (prod {uid: ws.uid})
        WHERE prod.workspace_id IS NULL
        RETURN ws.uid AS uid, ws, prod, labels(ws)[0] AS label
        """
        results = db.execute_and_fetch(query, parameters={"workspace_id": workspace_id})

        conflicts = []
        for res in results:
            ws_node = res["ws"]
            prod_node = res["prod"]
            ws_props = ws_node if isinstance(ws_node, dict) else ws_node._properties
            prod_props = (
                prod_node if isinstance(prod_node, dict) else prod_node._properties
            )
            uid = res["uid"]
            label = res["label"]

            differences = {}
            for key, ws_val in ws_props.items():
                if key in ["workspace_id"]:
                    continue
                prod_val = prod_props.get(key)
                if ws_val != prod_val:
                    differences[key] = {"production": prod_val, "workspace": ws_val}

            if differences:
                conflict = {"uid": uid, "label": label, "differences": differences}
                conflicts.append(conflict)
                redis_client.set(f"conflict:{workspace_id}:{uid}", "true")

        return conflicts

    @staticmethod
    def promote_to_production(workspace_id: str):
        node_query = """
        MATCH (ws {workspace_id: $workspace_id})
        OPTIONAL MATCH (prod {uid: ws.uid})
        WHERE prod.workspace_id IS NULL
        DETACH DELETE prod
        WITH ws
        SET ws.workspace_id = NULL,
            ws:Production
        REMOVE ws:Workspace
        """
        db.execute(node_query, parameters={"workspace_id": workspace_id})

        rel_query = """
        MATCH ()-[r {workspace_id: $workspace_id}]->()
        SET r.workspace_id = NULL
        """
        db.execute(rel_query, parameters={"workspace_id": workspace_id})

        keys = redis_client.keys(f"conflict:{workspace_id}:*")
        if keys:
            redis_client.delete(*keys)
