Lattice: Collaborative Temporal Graph for CTI
Lattice is a high-performance, workspace-aware threat intelligence platform built on the Diamond Model of Intrusion Analysis. It treats intelligence as a dynamic, layered graph, allowing analysts to collaborate in isolated "War Rooms" before merging findings into a shared "Production" ground truth.

💎 Core Philosophy
In a typical CTI environment, data is either "in" or "out." Lattice introduces a stratified approach:

The Production Stratum: The verified, peer-reviewed source of truth.

The Workspace Stratum: Private or shared investigative layers where hypotheses are tested, and new nodes are linked.

The Temporal Dimension: Every link in Lattice is time-bound. Infrastructure "exists" in the context of an adversary only for the duration of its observed use.

🛠 Key Features
1. Multi-User Workspaces (War Rooms)
Analysts work in isolated environments. When querying the graph, Lattice performs a Shadow Merge:

It fetches the Production base.

It overlays the Workspace data.

If a node property differs (e.g., a higher confidence score in the Workspace), the Workspace version takes priority.

2. Hierarchical Tagging (Synapse-Style)
Lattice implements a first-class taxonomy system:

Taxonomy Nodes: Tags are not strings; they are nodes in a tree (e.g., #actor.apt28.malware).

Inheritance: A search for #actor recursively finds all entities linked to child tags.

Temporal Tags: Apply tags that only "exist" for a specific window of time.

3. The Diamond Ontology
Strict enforcement of the four Diamond vertices ensures graph hygiene:

Adversary: (Who) Threat actors and aliases.

Infrastructure: (Where) IP, Domain, ASN, CIDR.

Capability: (How) Malware, Toolkits, Exploits.

Victim: (Target) Organizations, Sectors, Regions.

4. Conflict-Aware Merging
Promoting data to Production requires a "Merge Request":

Conflict Detection: Lattice identifies property clashes (e.g., different attributions for the same IP).

Atomic Push: Once resolved, Workspace labels are stripped, and data is promoted to Production in a single ACID transaction.

📦 Stack & Setup
Database: Memgraph (In-memory, C++ Graph Store).

API: FastAPI + GQLAlchemy (Python 3.11+).

Coordinator: Redis (Session state, Node-locking, Autocomplete).

Quick Start
Bash
docker-compose up -d
📄 docker-compose.yml
This file provides the Agent with a ready-to-code environment.

YAML
version: '3.8'

services:
  memgraph:
    image: memgraph/memgraph-platform:latest
    container_name: lattice-db
    ports:
      - "7687:7687" # Bolt protocol
      - "3000:3000" # Memgraph Lab (UI)
    environment:
      - MEMGRAPH_USER=
      - MEMGRAPH_PASSWORD=

  redis:
    image: redis:7-alpine
    container_name: lattice-coordinator
    ports:
      - "6379:6379"

  api:
    build: .
    container_name: lattice-api
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - MEMGRAPH_HOST=memgraph
      - MEMGRAPH_PORT=7687
      - REDIS_HOST=redis
    depends_on:
      - memgraph
      - redis
