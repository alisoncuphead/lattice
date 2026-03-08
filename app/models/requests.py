from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RelationshipCreate(BaseModel):
    """
    Request model for creating a relationship between two nodes.
    """

    source_uid: str
    target_uid: str
    rel_type: str = Field(
        ..., description="The Cypher relationship type, e.g., 'USES_INFRA'"
    )
    valid_from: datetime = Field(default_factory=datetime.now)
    valid_to: Optional[datetime] = None
    confidence: float = 100.0
    description: Optional[str] = None
