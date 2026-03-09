from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.enums import InfrastructureType, ActorType, CapabilityType
from app.utils.uid import generate_deterministic_uid


class DiamondNode(BaseModel):
    """
    Base model for all Diamond Model nodes in Lattice.
    """

    uid: Optional[str] = None  # Optional in request, generated in repo/route
    workspace_id: Optional[str] = None
    is_deleted: bool = False

    @classmethod
    def create_uid(cls, primary_data: dict) -> str:
        data_to_hash = {"_type": cls.__name__, **primary_data}
        return generate_deterministic_uid(data_to_hash)


class Adversary(DiamondNode):
    name: str
    aliases: List[str] = []
    actor_type: ActorType = ActorType.UNKNOWN


class Infrastructure(DiamondNode):
    value: str
    infra_type: InfrastructureType
    provider: Optional[str] = None


class Capability(DiamondNode):
    name: str
    cap_type: CapabilityType
    version: Optional[str] = None
    hash: Optional[str] = None


class Victim(DiamondNode):
    identity: str
    sector: Optional[str] = None
    region: Optional[str] = None


class Tag(DiamondNode):
    name: str
    description: Optional[str] = None
