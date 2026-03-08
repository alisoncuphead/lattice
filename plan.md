Goal: Step-by-step implementation guide for the Agent.

Phase 1: Environment & Core Models
Dockerize: Memgraph, Redis, and FastAPI.

Schema Init: Implement the models.py using GQLAlchemy (Nodes, Relationships, and Tags).

UID Utility: Create a hashing utility to ensure entity deduplication.

Phase 2: Workspace & Query Resolver
FastAPI Middleware: Intercept requests to inject workspace_context.

The Resolver: Write the "Priority Query" logic—if a node exists in both Production and Workspace, the Workspace properties "shadow" the Production ones.

Temporal Filter: Implement the global at_timestamp filter for all Cypher queries.

Phase 3: Tagging & Search
Tag Manager: Build logic to split tag paths (e.g., a.b.c) and create/link hierarchical nodes.

Recursive Search: Implement Cypher RECURSIVE or *1.. logic to find all nodes under a parent tag.

Phase 4: The Merge (Push to Production)
Conflict Detector: Compare Workspace vs. Production. Flag property mismatches in Redis.

Atomic Promotion: A single transaction to:

Remove :Workspace labels.

Add :Production labels.

Nullify workspace_id for promoted data.

# Practices to follow
🛠 1. Clean Code & Architecture Practices
The "Service-Repository" Pattern
Do not put Cypher queries inside your FastAPI routes. The Agent must separate concerns:

Models: Pydantic/GQLAlchemy definitions (the "Schema").

Repositories: Pure database interactions (CRUD for Nodes/Edges).

Services: Business logic (e.g., "Merging a workspace," "Calculating a Diamond conflict").

Routes: HTTP handling and input validation.

Type Safety & Validation
Strict Pydantic: Use Pydantic v2 for all Request/Response models.

Type Hinting: Every function signature must include type hints: def get_node(uid: str) -> Optional[Adversary]:.

Enum-Driven Ontology: Use Python Enum for fixed values like infra_type (IP, Domain, CIDR) to prevent "data rot" from typos.

Deterministic ID Generation
Since analysts work in different workspaces, the Agent must ensure the same entity (e.g., IP 8.8.8.8) always has the same UID.

Good Practice: Use a namespace-based UUID or a SHA256 hash of the normalized value.

Normalization: Always strip() and lower() strings before hashing to ensure Google.com and google.com map to the same node.

🕸 2. Graph-Specific Best Practices (Memgraph/Cypher)
Query Parametrization
Never use f-strings to build Cypher queries. This prevents Cypher injection and allows Memgraph to cache query plans.

Bad: client.execute(f"MATCH (n {id: '{user_id}'}) ...")

Good: client.execute("MATCH (n {id: $id}) ...", parameters={"id": user_id})

Index Management
The Agent must ensure that "Lookups" and "Temporal Slices" are indexed immediately.

Required Indexes: Node(uid), Node(workspace_id), Relationship(valid_from), Relationship(valid_to).

Atomic Transactions
When "Promoting" a workspace to production, use a single transaction. If the relationship move fails, the labels should not be stripped. Memgraph supports ACID transactions—use them.

⏱ 3. Temporal & Collaborative Logic
The "Null" Infinity Rule
In the temporal model, valid_to: null represents an ongoing or permanent relationship.

Code Logic: The filtering logic must explicitly check for OR r.valid_to IS NULL whenever a timestamp is provided.

Defensive Locking (Redis)
To prevent two analysts from editing the same Diamond node simultaneously:

Practice: Implement a "Soft Lock" in Redis with a TTL (Time-To-Live). If a user opens an "Edit" dialog, set lock:node:{uid}. If they close it or the browser crashes, the lock expires automatically in 5–10 minutes.

🧪 4. Testing & Documentation
Integration over Unit Testing
Because Lattice is a graph-heavy tool, simple unit tests (mocking the DB) are less useful than Integration Tests.

Agent Task: Create a conftest.py that spins up a temporary Memgraph Docker container for testing real Cypher traversals and workspace overlays.

Self-Documenting API
Use FastAPI Summary and Description tags for every endpoint.

Ensure the /docs (Swagger) page clearly explains how to use the ?at= temporal filter.

📄 Updated plan.md for the Agent
Instruction to Agent: > "Follow the Service-Repository pattern. Ensure all Cypher queries are parameterized. Implement the DiamondNode base class to automatically handle uid generation via SHA256 hashing of primary values. Use Redis for 'Active Session' tracking and node-level soft-locking."
