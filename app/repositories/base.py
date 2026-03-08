from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
from app.database import db
from app.models.nodes import DiamondNode

T = TypeVar("T", bound=DiamondNode)


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model
        self.label = model.__name__

    def get_by_uid(self, uid: str, workspace_id: Optional[str] = None) -> Optional[T]:
        # Filter for workspace OR production
        # Sort such that non-null workspace_id comes first
        query = f"""
        MATCH (n:{self.label} {{uid: $uid}})
        WHERE n.workspace_id = $workspace_id OR n.workspace_id IS NULL
        RETURN n
        ORDER BY CASE WHEN n.workspace_id IS NULL THEN 1 ELSE 0 END ASC
        LIMIT 1
        """
        results = db.execute_and_fetch(
            query, parameters={"uid": uid, "workspace_id": workspace_id}
        )
        res = list(results)
        if not res:
            return None
        node_data = res[0]["n"]
        props = node_data if isinstance(node_data, dict) else node_data._properties
        if "workspace_id" not in props:
            props["workspace_id"] = None
        return self.model(**props)

    def create(self, node: T) -> T:
        query = f"""
        MERGE (n:{self.label} {{uid: $uid, workspace_id: $workspace_id}})
        SET n += $props
        RETURN n
        """
        props = node.model_dump(exclude={"uid", "workspace_id"})
        results = db.execute_and_fetch(
            query,
            parameters={
                "uid": node.uid,
                "workspace_id": node.workspace_id,
                "props": props,
            },
        )
        res = list(results)
        node_data = res[0]["n"]
        props = node_data if isinstance(node_data, dict) else node_data._properties
        if "workspace_id" not in props:
            props["workspace_id"] = None
        return self.model(**props)

    def list(self, workspace_id: Optional[str] = None, limit: int = 100) -> List[T]:
        query = f"""
        MATCH (n:{self.label})
        WHERE n.workspace_id = $workspace_id OR n.workspace_id IS NULL
        WITH n.uid AS uid, n
        ORDER BY CASE WHEN n.workspace_id IS NULL THEN 1 ELSE 0 END ASC
        WITH uid, head(collect(n)) AS final_node
        RETURN final_node
        LIMIT $limit
        """
        results = db.execute_and_fetch(
            query, parameters={"workspace_id": workspace_id, "limit": limit}
        )
        output = []
        for res in results:
            node_data = res["final_node"]
            props = node_data if isinstance(node_data, dict) else node_data._properties
            if "workspace_id" not in props:
                props["workspace_id"] = None
            output.append(self.model(**props))
        return output
