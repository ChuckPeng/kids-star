from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth import router as auth_router
from app.api.v1.families import router as families_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.challenges import router as challenges_router
from app.api.v1.rewards import router as rewards_router
from app.api.v1.applications import router as applications_router
from app.api.v1.statistics import router as statistics_router
from app.core.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(families_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(challenges_router, prefix="/api/v1")
app.include_router(rewards_router, prefix="/api/v1")
app.include_router(applications_router, prefix="/api/v1")
app.include_router(statistics_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
