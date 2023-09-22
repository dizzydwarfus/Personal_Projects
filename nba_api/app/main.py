from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from .database.sql_connector import DB
from .database.db import get_db

from .api.endpoints import players, shots_taken, tables, positions

from .utils import utils

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root(db: DB = Depends(get_db)):
    connection_status = "Connected" if db.test_connection(
    ) else "Failed to connect to the database."

    endpoints = {
        route.path: route.name for route in app.routes
    }

    usage_examples = {
        "/v1/api/players": "/v1/api/players?player_id=5",
        "/v1/api/shots": "/v1/api/shots?player_id=5",
        "/v1/api/tables": "/v1/api/tables",
        "/v1/api/positions": "/v1/api/positions",
        # ... Add usage examples for other endpoints here
    }

    return {
        "message": "Welcome to the NBA Data API!",
        "description": "This API provides information about NBA players, shots, positions, and more.",
        "database_status": connection_status,
        "available_endpoints": endpoints,
        "usage_examples": usage_examples,
        "note": "Visit each endpoint or refer to the documentation at /docs for more details."
    }


app.include_router(players.router, prefix="/v1/api/players", tags=['players'])
app.include_router(shots_taken.router, prefix="/v1/api/shots", tags=['shots'])
app.include_router(tables.router, prefix="/v1/api/tables", tags=['tables'])
app.include_router(
    positions.router, prefix="/v1/api/positions", tags=['positions'])
app.include_router(utils.router, prefix="/v1/api/utils", tags=['utilities'])


# in root directory, run with: uvicorn app.main:app --reload
