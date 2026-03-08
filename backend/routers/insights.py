from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from database import get_db
from models import Job
from schemas import InsightRequest, InsightResponse
from services.claude_insights import generate_market_insight, analyze_job_description
from config import get_settings

router = APIRouter(prefix="/api/insights", tags=["insights"])
settings = get_settings()


@router.get("/market/{category}")
async def market_insight(category: str, db: AsyncSession = Depends(get_db)):
    if not settings.anthropic_api_key:
        raise HTTPException(status_code=503, detail="Claude API key not configured")

    job_count = (await db.execute(
        select(func.count(Job.id)).where(
            Job.is_active == True,
            Job.category.ilike(f"%{category}%")
        )
    )).scalar()

    avg_salary = (await db.execute(
        select(func.avg(Job.salary_min)).where(
            Job.is_active == True,
            Job.category.ilike(f"%{category}%"),
            Job.salary_min != None,
        )
    )).scalar()

    county_rows = (await db.execute(
        select(Job.county, func.count(Job.id).label("count"))
        .where(Job.is_active == True, Job.category.ilike(f"%{category}%"), Job.county != None)
        .group_by(Job.county)
        .order_by(text("count DESC"))
        .limit(5)
    )).all()

    skill_rows = (await db.execute(
        text("""
            SELECT skill, COUNT(*) as cnt
            FROM jobs, unnest(skills) AS skill
            WHERE is_active = true AND category ILIKE :cat
            GROUP BY skill ORDER BY cnt DESC LIMIT 15
        """),
        {"cat": f"%{category}%"}
    )).all()

    county_breakdown = [{"county": r[0], "count": r[1]} for r in county_rows]
    top_skills = [r[0] for r in skill_rows]

    return await generate_market_insight(
        category=category,
        top_skills=top_skills,
        job_count=job_count,
        avg_salary=avg_salary,
        county_breakdown=county_breakdown,
    )


@router.get("/job/{job_id}")
async def job_insight(job_id: int, db: AsyncSession = Depends(get_db)):
    if not settings.anthropic_api_key:
        raise HTTPException(status_code=503, detail="Claude API key not configured")

    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return await analyze_job_description(
        description=job.description or "",
        title=job.title
    )
