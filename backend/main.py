import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import init_db
from routers import jobs, stats, insights
from routers.pipeline import router as pipeline_router
from config import get_settings
from models import SyncLog
from database import AsyncSessionLocal
from pipeline.runner import run_pipeline

settings = get_settings()
scheduler = AsyncIOScheduler()


async def sync_adzuna_jobs():
    async with AsyncSessionLocal() as db:
        await run_pipeline(db)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    try:
        await ensure_index()
    except Exception:
        pass  # ES may not be available in all environments

    # run initial sync on startup
    asyncio.create_task(sync_adzuna_jobs())

    # schedule periodic syncs
    scheduler.add_job(
        sync_adzuna_jobs,
        "interval",
        hours=settings.sync_interval_hours,
        id="adzuna_sync",
    )
    scheduler.start()

    yield

    scheduler.shutdown()


app = FastAPI(
    title="Irish Job Dashboard API",
    description="Aggregates Irish job market data from Adzuna with skill extraction and Claude-powered insights",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://irish-job-dashboard.netlify.app",
        "https://*.netlify.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router)
app.include_router(stats.router)
app.include_router(insights.router)
app.include_router(pipeline_router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
