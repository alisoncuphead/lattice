from typing import List, Optional, Dict, Any
from app.database import db
from app.models.nodes import Tag


class TagManager:
    @staticmethod
    def ensure_tag(tag_path: str, workspace_id: Optional[str] = None) -> Tag:
        parts = tag_path.strip("#").split(".")
        current_path = ""
        last_tag_uid = None

        for part in parts:
            if current_path:
                current_path += f".{part}"
            else:
                current_path = part

            uid = Tag.create_uid({"name": current_path})

            query = """
            MERGE (t:Tag {uid: $uid})
            SET t.name = $name, t.workspace_id = $workspace_id
            RETURN t
            """
            db.execute(
                query,
                parameters={
                    "uid": uid,
                    "name": current_path,
                    "workspace_id": workspace_id,
                },
            )

            if last_tag_uid:
                link_query = """
                MATCH (p:Tag {uid: $p_uid}), (c:Tag {uid: $c_uid})
                MERGE (c)-[:SUBTAG_OF]->(p)
                """
                db.execute(link_query, parameters={"p_uid": last_tag_uid, "c_uid": uid})

            last_tag_uid = uid

        return Tag(uid=last_tag_uid, name=current_path, workspace_id=workspace_id)

    @staticmethod
    def get_tags_for_entity(
        entity_uid: str, workspace_id: Optional[str] = None
    ) -> List[Tag]:
        query = """
        MATCH (n {uid: $entity_uid})-[r:HAS_TAG]->(t:Tag)
        WHERE r.workspace_id = $workspace_id OR r.workspace_id IS NULL
        RETURN t
        """
        results = db.execute_and_fetch(
            query, parameters={"entity_uid": entity_uid, "workspace_id": workspace_id}
        )
        output = []
        for res in results:
            node = res["t"]
            props = node if isinstance(node, dict) else node._properties
            output.append(Tag(**props))
        return output

    @staticmethod
    def tag_entity(
        entity_uid: str,
        tag_path: str,
        workspace_id: Optional[str] = None,
        valid_from: Optional[float] = None,
        valid_to: Optional[float] = None,
    ):
        import time

        if not valid_from:
            valid_from = time.time()

        tag = TagManager.ensure_tag(tag_path, workspace_id)

        query = """
        MATCH (e {uid: $entity_uid}), (t:Tag {uid: $tag_uid})
        MERGE (e)-[r:HAS_TAG]->(t)
        SET r.workspace_id = $workspace_id,
            r.valid_from = $valid_from,
            r.valid_to = $valid_to
        """
        db.execute(
            query,
            parameters={
                "entity_uid": entity_uid,
                "tag_uid": tag.uid,
                "workspace_id": workspace_id,
                "valid_from": valid_from,
                "valid_to": valid_to,
            },
        )

    @staticmethod
    def find_entities_by_tag(
        tag_name: str, workspace_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query = """
        MATCH (t:Tag {name: $tag_name})<-[:SUBTAG_OF*0..]-(child_tag:Tag)
        MATCH (child_tag)<-[:HAS_TAG]-(entity)
        WHERE entity.workspace_id = $workspace_id OR entity.workspace_id IS NULL
        RETURN DISTINCT entity
        """
        results = db.execute_and_fetch(
            query, parameters={"tag_name": tag_name, "workspace_id": workspace_id}
        )
        output = []
        for res in results:
            node = res["entity"]
            output.append(node if isinstance(node, dict) else node._properties)
        return output
