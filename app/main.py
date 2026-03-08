from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import (
    infrastructure,
    workspaces,
    tags,
    adversary,
    capability,
    victim,
    relationships,
)
from app.database import init_db

app = FastAPI(
    title="Lattice API",
    description="Collaborative Temporal Graph for CTI",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Lattice-Workspace"],
)


@app.on_event("startup")
async def startup_event():
    # In a real app, we'd wait for the DB to be ready
    init_db()


app.include_router(infrastructure.router)
app.include_router(adversary.router)
app.include_router(capability.router)
app.include_router(victim.router)
app.include_router(relationships.router)
app.include_router(workspaces.router)
app.include_router(tags.router)


@app.get("/")
async def root():
    return {"message": "Welcome to Lattice CTI Platform"}
