# GEMINI.md - Lattice Project Context

## Project Overview
Lattice is a high-performance, workspace-aware threat intelligence platform built on the Diamond Model of Intrusion Analysis. It treats intelligence as a dynamic, layered graph, allowing analysts to collaborate in isolated "War Rooms" (Workspaces) before merging findings into a shared "Production" ground truth.

### Key Technologies
- **Python 3.11+**: Primary programming language.
- **FastAPI**: Web framework for the API.
- **Memgraph**: In-memory, C++ Graph Store (using Bolt protocol).
- **GQLAlchemy**: Object-graph mapper (OGM) for Memgraph.
- **Redis**: Session state, node-locking, and autocomplete coordinator.
- **Docker & Docker Compose**: Environment orchestration.

### Architecture
- **Production Stratum**: Verified, peer-reviewed source of truth.
- **Workspace Stratum**: Private/shared investigative layers.
- **Temporal Dimension**: Time-bound relationships (`valid_from`, `valid_to`).
- **Diamond Ontology**: Adversary, Infrastructure, Capability, Victim.

## Development Standards

### 1. Service-Repository Pattern
- **Models**: `models.py` using Pydantic v2 and GQLAlchemy.
- **Repositories**: `repositories/` for pure database interactions (Cypher queries).
- **Services**: `services/` for business logic (merging, conflict resolution).
- **Routes**: `routes/` for HTTP handling and validation.

### 2. Type Safety & Validation
- Strict use of Pydantic v2.
- Comprehensive type hinting for all function signatures.
- Enum-driven ontology for fixed values.

### 3. Graph Best Practices
- **Deterministic UIDs**: SHA256 hash of normalized primary values (e.g., lowercase, stripped strings).
- **Parameterized Queries**: Never use f-strings for Cypher queries.
- **Index Management**: Ensure `uid`, `workspace_id`, `valid_from`, and `valid_to` are indexed.
- **Atomic Transactions**: Use ACID transactions for promotions/merges.

### 4. Temporal Logic
- `valid_to: null` represents infinity/ongoing.
- Always include temporal filters in queries when a timestamp is provided.

### 5. Node Locking
- Implement soft-locking in Redis for concurrent edits.

## Building and Running
```bash
docker-compose up -d
```

## Testing
- Prioritize integration tests using a real Memgraph instance.
- Use `pytest` and `conftest.py` for setup.
