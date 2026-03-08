import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import init_db
from routers import jobs, stats, insights
from config import get_settings
from services.adzuna import fetch_jobs, normalize_job
from services.skill_extractor import extract_skills
from models import Job, SyncLog
from database import AsyncSessionLocal
from sqlalchemy import select
from datetime import datetime

settings = get_settings()
scheduler = AsyncIOScheduler()


async def sync_adzuna_jobs():
    async with AsyncSessionLocal() as db:
        log = SyncLog(started_at=datetime.utcnow())
        db.add(log)
        await db.commit()
        await db.refresh(log)

        fetched = 0
        added = 0
        updated = 0

        try:
            for page in range(1, settings.adzuna_max_pages + 1):
                data = await fetch_jobs(page=page)
                results = data.get("results", [])
                if not results:
                    break

                for raw in results:
                    fetched += 1
                    normalized = normalize_job(raw)
                    normalized["skills"] = extract_skills(
                        f"{normalized['title']} {normalized.get('description', '')}"
                    )

                    existing = (await db.execute(
                        select(Job).where(Job.adzuna_id == normalized["adzuna_id"])
                    )).scalar_one_or_none()

                    if existing:
                        for k, v in normalized.items():
                            setattr(existing, k, v)
                        existing.synced_at = datetime.utcnow()
                        updated += 1
                    else:
                        job = Job(**normalized, synced_at=datetime.utcnow())
                        db.add(job)
                        added += 1

                await db.commit()

            log.status = "success"
        except Exception as e:
            log.status = "failed"
            log.error = str(e)
        finally:
            log.jobs_fetched = fetched
            log.jobs_added = added
            log.jobs_updated = updated
            log.finished_at = datetime.utcnow()
            await db.commit()

        print(f"[sync] done — fetched={fetched} added={added} updated={updated}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

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
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router)
app.include_router(stats.router)
app.include_router(insights.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
