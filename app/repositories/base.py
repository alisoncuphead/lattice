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
        
        # Check for tombstone
        if props.get("is_deleted"):
            return None

        if "workspace_id" not in props:
            props["workspace_id"] = None
        return self.model(**props)

    def get_bulk_by_uids(self, uids: List[str], workspace_id: Optional[str] = None) -> List[T]:
        """
        Retrieves multiple nodes by their UIDs in a single query.
        """
        query = f"""
        MATCH (n:{self.label})
        WHERE n.uid IN $uids AND (n.workspace_id = $workspace_id OR n.workspace_id IS NULL)
        WITH n.uid AS uid, n
        ORDER BY CASE WHEN n.workspace_id IS NULL THEN 1 ELSE 0 END ASC
        WITH uid, head(collect(n)) AS final_node
        WHERE final_node.is_deleted IS NULL OR final_node.is_deleted = false
        RETURN final_node
        """
        results = db.execute_and_fetch(
            query, parameters={"uids": uids, "workspace_id": workspace_id}
        )
        output = []
        for res in results:
            node_data = res["final_node"]
            props = node_data if isinstance(node_data, dict) else node_data._properties
            if "workspace_id" not in props:
                props["workspace_id"] = None
            output.append(self.model(**props))
        return output

    def create(self, node: T) -> T:
        query = f"""
        MERGE (n:{self.label} {{uid: $uid, workspace_id: $workspace_id}})
        SET n:DiamondNode, n.is_deleted = false, n += $props
        RETURN n
        """
        props = node.model_dump(exclude={"uid", "workspace_id", "is_deleted"})
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

    def delete(self, uid: str, workspace_id: Optional[str] = None):
        """
        Hard delete if in Production (workspace_id=None).
        Create a Tombstone if in a Workspace.
        """
        if workspace_id is None:
            # Production Hard Delete
            query = f"MATCH (n:{self.label} {{uid: $uid}}) WHERE n.workspace_id IS NULL DETACH DELETE n"
            db.execute(query, parameters={"uid": uid})
        else:
            # Workspace Tombstone
            query = f"""
            MERGE (n:{self.label} {{uid: $uid, workspace_id: $workspace_id}})
            SET n:DiamondNode, n.is_deleted = true
            """
            db.execute(query, parameters={"uid": uid, "workspace_id": workspace_id})

    def list(self, workspace_id: Optional[str] = None, limit: int = 100) -> List[T]:
        return self.search(workspace_id=workspace_id, limit=limit)

    def search(
        self,
        workspace_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        query: Optional[str] = None,
        limit: int = 100
    ) -> List[T]:
        """
        Advanced search with property filters, tag matching, and keyword search.
        """
        where_clauses = ["(n.workspace_id = $workspace_id OR n.workspace_id IS NULL)"]
        params = {"workspace_id": workspace_id, "limit": limit}

        if filters:
            for key, value in filters.items():
                where_clauses.append(f"n.{key} = $filter_{key}")
                params[f"filter_{key}"] = value

        if query:
            # Basic keyword search across common fields
            where_clauses.append("(n.name CONTAINS $query OR n.value CONTAINS $query OR n.identity CONTAINS $query)")
            params["query"] = query

        tag_match = ""
        if tags:
            tag_match = "MATCH (n)-[:HAS_TAG]->(t:Tag) WHERE t.name IN $tags"
            params["tags"] = tags

        cypher_where = " AND ".join(where_clauses)
        
        full_query = f"""
        MATCH (n:{self.label})
        {tag_match}
        WHERE {cypher_where}
        WITH n.uid AS uid, n
        ORDER BY CASE WHEN n.workspace_id IS NULL THEN 1 ELSE 0 END ASC
        WITH uid, head(collect(n)) AS final_node
        WHERE final_node.is_deleted IS NULL OR final_node.is_deleted = false
        RETURN final_node
        LIMIT $limit
        """
        
        results = db.execute_and_fetch(full_query, parameters=params)
        output = []
        for res in results:
            node_data = res["final_node"]
            props = node_data if isinstance(node_data, dict) else node_data._properties
            if "workspace_id" not in props:
                props["workspace_id"] = None
            output.append(self.model(**props))
        return output
