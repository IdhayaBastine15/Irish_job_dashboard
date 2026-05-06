"""
Extract stage — fetch raw jobs from Adzuna with retry logic.
"""
from __future__ import annotations
import asyncio
import httpx
from pipeline.context import PipelineContext
from services.adzuna import fetch_jobs
from config import get_settings

settings = get_settings()

MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


async def _fetch_page_with_retry(page: int) -> list[dict]:
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            data = await fetch_jobs(page=page)
            return data.get("results", [])
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            last_err = e
            if attempt < MAX_RETRIES:
                await asyncio.sleep(RETRY_DELAY * attempt)
    raise RuntimeError(f"Extract failed after {MAX_RETRIES} attempts: {last_err}")


async def run_extract(ctx: PipelineContext) -> PipelineContext:
    stage = ctx.add_stage("extract")
    raw: list[dict] = []

    try:
        for page in range(1, settings.adzuna_max_pages + 1):
            results = await _fetch_page_with_retry(page)
            if not results:
                break
            raw.extend(results)
            print(f"[extract] page={page} fetched={len(results)} total={len(raw)}")

        ctx.raw_jobs = raw
        stage.finish(records_out=len(raw))
    except Exception as e:
        stage.finish(error=str(e))

    return ctx
