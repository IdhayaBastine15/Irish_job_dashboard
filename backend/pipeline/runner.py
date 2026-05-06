"""
Pipeline runner — orchestrates Extract → Transform → Load stages.
Writes a SyncLog entry to the database for every run.
"""
from __future__ import annotations
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from pipeline.context import PipelineContext
from pipeline.extract import run_extract
from pipeline.transform import run_transform
from pipeline.load import run_load
from models import SyncLog


async def run_pipeline(db: AsyncSession) -> PipelineContext:
    ctx = PipelineContext()

    # create a SyncLog row so the run is visible immediately
    log = SyncLog(started_at=ctx.started_at)
    db.add(log)
    await db.commit()
    await db.refresh(log)
    ctx.run_id = log.id

    print(f"[pipeline] run_id={ctx.run_id} started")

    try:
        ctx = await run_extract(ctx)

        # abort if extract failed
        if ctx.stages[-1].status == "failed":
            raise RuntimeError(ctx.stages[-1].error)

        ctx = await run_transform(ctx)

        if ctx.stages[-1].status == "failed":
            raise RuntimeError(ctx.stages[-1].error)

        ctx = await run_load(ctx, db)

        log.status = ctx.status

    except Exception as e:
        log.status = "failed"
        log.error = str(e)
        print(f"[pipeline] run_id={ctx.run_id} failed: {e}")

    finally:
        ctx.finished_at = datetime.utcnow()
        log.finished_at = ctx.finished_at
        log.jobs_fetched = len(ctx.raw_jobs)
        log.jobs_added = ctx.jobs_added
        log.jobs_updated = ctx.jobs_updated
        await db.commit()

    print(
        f"[pipeline] run_id={ctx.run_id} status={log.status} "
        f"fetched={log.jobs_fetched} added={log.jobs_added} updated={log.jobs_updated}"
    )
    return ctx
