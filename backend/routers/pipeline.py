from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from database import get_db
from models import SyncLog
from pipeline.runner import run_pipeline

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])


@router.get("/status")
async def pipeline_status(limit: int = 10, db: AsyncSession = Depends(get_db)):
    """Return recent pipeline run summaries."""
    rows = (await db.execute(
        select(SyncLog).order_by(desc(SyncLog.started_at)).limit(limit)
    )).scalars().all()

    return [
        {
            "run_id": r.id,
            "status": r.status,
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "finished_at": r.finished_at.isoformat() if r.finished_at else None,
            "jobs_fetched": r.jobs_fetched,
            "jobs_added": r.jobs_added,
            "jobs_updated": r.jobs_updated,
            "error": r.error,
        }
        for r in rows
    ]


@router.post("/trigger")
async def trigger_pipeline(background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """Manually trigger a pipeline run."""
    background_tasks.add_task(run_pipeline, db)
    return {"message": "pipeline run triggered"}
