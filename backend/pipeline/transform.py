"""
Transform stage — normalize raw API data, extract skills, enrich records.
"""
from __future__ import annotations
from pipeline.context import PipelineContext
from services.adzuna import normalize_job
from services.skill_extractor import extract_skills


def _enrich(raw: dict) -> dict:
    job = normalize_job(raw)
    job["skills"] = extract_skills(
        f"{job['title']} {job.get('description', '')}"
    )
    return job


async def run_transform(ctx: PipelineContext) -> PipelineContext:
    stage = ctx.add_stage("transform", records_in=len(ctx.raw_jobs))

    if stage.records_in == 0:
        stage.finish(error="no raw jobs to transform")
        return ctx

    transformed = []
    errors = 0

    for raw in ctx.raw_jobs:
        try:
            transformed.append(_enrich(raw))
        except Exception as e:
            errors += 1
            print(f"[transform] skipped record id={raw.get('id')}: {e}")

    ctx.transformed_jobs = transformed
    print(f"[transform] transformed={len(transformed)} errors={errors}")

    if errors and not transformed:
        stage.finish(error=f"all {errors} records failed to transform")
    else:
        stage.finish(records_out=len(transformed))

    return ctx
