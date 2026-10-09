from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.vaultapi.api.v1.endpoints import auth, documents

from src.vaultapi.db.session import engine
from src.vaultapi.models.base import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs when the server starts up
    async with engine.begin() as conn:
        # run_sync is required because create_all is a synchronous SQLAlchemy method
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
