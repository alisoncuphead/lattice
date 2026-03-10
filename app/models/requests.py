from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
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
    # Metadata for Diamond Model logic
    valid_from: datetime = Field(default_factory=datetime.now)
    valid_to: Optional[datetime] = None
    confidence: float = 100.0
    
    # Metadata for UI (Carbon)
    relationship_type: Optional[str] = None
    source_vendor: Optional[str] = None
    description: Optional[str] = None
    context: Dict[str, Any] = {}


class BulkInfrastructureRequest(BaseModel):
    """
    Request model for bulk infrastructure lookup.
    """

    values: List[str] = Field(..., description="List of infrastructure values (IPs, domains, etc.)")


class ProposeChangeRequest(BaseModel):
    """
    Request model for proposing a change to an existing node.
    """

    uid: str = Field(..., description="The UID of the node to change")
    label: str = Field(..., description="The label/type of the node (e.g. 'Adversary')")
    properties: Dict[str, Any] = Field(..., description="The new properties to apply")
