Goal: Define the multi-user, workspace-aware environment.

1. The Stack
Graph Store: Memgraph (In-Memory Property Graph).

API Layer: FastAPI (Python 3.11+) with GQLAlchemy.

Coordination Layer: Redis (Session state, Real-time node locking, Tag autocomplete).

Interface: CLI (Click/Typer) + Graph Visualization (D3.js or Cytoscape).

2. Workspace & Collaboration Logic
The Overlay Pattern: Production data is the "Base Layer." Workspaces are "Delta Layers."

State Management:

Production: Nodes/Edges labeled :Production.

Workspace: Nodes/Edges labeled :Workspace + workspace_id.

Sessioning: FastAPI uses a Redis-backed session to track the user’s active_workspace_id. All queries are automatically rewritten to: WHERE n.workspace_id = $ws OR :Production IN labels(n).
