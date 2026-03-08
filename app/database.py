from gqlalchemy import Memgraph
from redis import Redis
from app.config import settings

# Global Memgraph instance
db = Memgraph(
    host=settings.MEMGRAPH_HOST,
    port=settings.MEMGRAPH_PORT,
    username=settings.MEMGRAPH_USER,
    password=settings.MEMGRAPH_PASSWORD,
)

# Global Redis instance
redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True,
)


def init_db():
    """Initializes database indexes using raw Cypher."""
    # Ensure indexes for DiamondNodes
    db.execute("CREATE INDEX ON :DiamondNode(uid);")
    db.execute("CREATE INDEX ON :DiamondNode(workspace_id);")

    # Specific indexes for types
    db.execute("CREATE INDEX ON :Adversary(name);")
    db.execute("CREATE INDEX ON :Infrastructure(value);")
    db.execute("CREATE INDEX ON :Capability(name);")
    db.execute("CREATE INDEX ON :Victim(identity);")
    db.execute("CREATE INDEX ON :Tag(name);")

    # Relationship indexes
    db.execute("CREATE INDEX ON :USES_INFRA(valid_from);")
    db.execute("CREATE INDEX ON :USES_INFRA(valid_to);")
    db.execute("CREATE INDEX ON :USES_CAPABILITY(valid_from);")
    db.execute("CREATE INDEX ON :USES_CAPABILITY(valid_to);")
    db.execute("CREATE INDEX ON :TARGETS_VICTIM(valid_from);")
    db.execute("CREATE INDEX ON :TARGETS_VICTIM(valid_to);")
    db.execute("CREATE INDEX ON :HAS_TAG(valid_from);")
    db.execute("CREATE INDEX ON :HAS_TAG(valid_to);")
