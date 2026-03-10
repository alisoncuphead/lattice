from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class DiamondRelationship(BaseModel):
    valid_from: datetime = Field(default_factory=datetime.now)
    valid_to: Optional[datetime] = None
    confidence: float = 100.0
    workspace_id: Optional[str] = None
    is_deleted: bool = False
    
    # Enriched Metadata for Carbon
    relationship_type: Optional[str] = Field(None, description="Semantic type (e.g. RESOLVED_TO, DROPPED_BY)")
    source_vendor: Optional[str] = Field(None, description="The tool that provided this link (e.g. VirusTotal)")
    description: Optional[str] = None
    context: Dict[str, Any] = {}


class UsesInfrastructure(DiamondRelationship):
    pass


class UsesCapability(DiamondRelationship):
    pass


class TargetsVictim(DiamondRelationship):
    pass


class HasTag(DiamondRelationship):
    pass


class SubtagOf(BaseModel):
    pass
