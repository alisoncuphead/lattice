from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DiamondRelationship(BaseModel):
    valid_from: datetime
    valid_to: Optional[datetime] = None
    confidence: float = 100.0
    workspace_id: Optional[str] = None


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
