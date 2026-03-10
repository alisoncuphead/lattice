from typing import Any, Dict, Optional
from app.database import db

class AnalysisService:
    @staticmethod
    def propose_change(
        uid: str, label: str, properties: Dict[str, Any], workspace_id: str
    ) -> Dict[str, Any]:
        """
        Clones a production node into a workspace with new properties, 
        effectively "proposing" a change for later promotion.
        """
        # 1. Fetch the production node properties
        get_query = f"MATCH (n:{label} {{uid: $uid}}) WHERE n.workspace_id IS NULL RETURN n"
        prod_results = db.execute_and_fetch(get_query, parameters={"uid": uid})
        prod_res = list(prod_results)
        
        if not prod_res:
            raise ValueError(f"Production node {uid} not found")
        
        prod_node = prod_res[0]["n"]
        prod_props = prod_node if isinstance(prod_node, dict) else prod_node._properties
        
        # 2. Merge with the new proposed properties
        final_props = {**prod_props, **properties}
        # Ensure we don't overwrite crucial metadata
        final_props["uid"] = uid
        final_props["workspace_id"] = workspace_id
        final_props["is_deleted"] = False
        
        # 3. Create the workspace shadow node
        merge_query = f"""
        MERGE (n:{label} {{uid: $uid, workspace_id: $workspace_id}})
        SET n:DiamondNode, n += $props
        RETURN n
        """
        results = db.execute_and_fetch(
            merge_query,
            parameters={
                "uid": uid,
                "workspace_id": workspace_id,
                "props": final_props
            }
        )
        
        res = list(results)[0]["n"]
        return res if isinstance(res, dict) else res._properties
