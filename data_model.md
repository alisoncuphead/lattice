Goal: Define the Diamond Model ontology and hierarchical tagging.

1. Node Vertices (The Diamond)
All nodes have a uid (deterministic hash of their primary value).

Adversary: name (PK), aliases, actor_type.

Infrastructure: value (PK), infra_type (IP, Domain, etc.), provider.

Capability: name (PK), cap_type, version, hash.

Victim: identity (PK), sector, region.

2. Temporal Relationships (The Assertions)
Every edge between vertices must include:

valid_from: Start of observation.

valid_to: End of observation (Null = Indefinite).

confidence: 0-100.

workspace_id: Scoping the assertion.

3. Hierarchical Tagging (Synapse Style)
Tag Nodes: Represent taxonomy (e.g., #actor.apt28.cnc).

Path Inheritance: Searching for #actor recursively returns #actor.apt28.

Edge: (:Entity)-[:HAS_TAG {valid_from, valid_to}]->(:Tag).
