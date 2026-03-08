from app.repositories.base import BaseRepository
from app.models.nodes import Adversary, Infrastructure, Capability, Victim, Tag


class AdversaryRepository(BaseRepository[Adversary]):
    def __init__(self):
        super().__init__(Adversary)


class InfrastructureRepository(BaseRepository[Infrastructure]):
    def __init__(self):
        super().__init__(Infrastructure)


class CapabilityRepository(BaseRepository[Capability]):
    def __init__(self):
        super().__init__(Capability)


class VictimRepository(BaseRepository[Victim]):
    def __init__(self):
        super().__init__(Victim)


class TagRepository(BaseRepository[Tag]):
    def __init__(self):
        super().__init__(Tag)
