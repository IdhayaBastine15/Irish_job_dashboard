"""
Load stage — upsert jobs into PostgreSQL and index into Elasticsearch.
"""
from __future__ import annotations
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pipeline.context import PipelineContext
from models import Job
from services.search import index_job


async def run_load(ctx: PipelineContext, db: AsyncSession) -> PipelineContext:
    stage = ctx.add_stage("load", records_in=len(ctx.transformed_jobs))

    if stage.records_in == 0:
        stage.finish(error="no transformed jobs to load")
        return ctx

    added = 0
    updated = 0
    es_errors = 0

    try:
        for normalized in ctx.transformed_jobs:
            existing = (await db.execute(
                select(Job).where(Job.adzuna_id == normalized["adzuna_id"])
            )).scalar_one_or_none()

            if existing:
                for k, v in normalized.items():
                    setattr(existing, k, v)
                existing.synced_at = datetime.utcnow()
                updated += 1
            else:
                db.add(Job(**normalized, synced_at=datetime.utcnow()))
                added += 1

            try:
                await index_job(normalized)
            except Exception as e:
                es_errors += 1
                print(f"[load] ES index error for {normalized.get('adzuna_id')}: {e}")

        await db.commit()

        ctx.jobs_added = added
        ctx.jobs_updated = updated
        print(f"[load] added={added} updated={updated} es_errors={es_errors}")
        stage.finish(records_out=added + updated)

    except Exception as e:
        await db.rollback()
        stage.finish(error=str(e))

    return ctx
