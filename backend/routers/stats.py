from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from datetime import datetime, timedelta
from database import get_db
from models import Job, SyncLog
from schemas import StatsOverview, CategoryCount, CountyCount, SkillCount, SalaryBucket

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/overview", response_model=StatsOverview)
async def overview(db: AsyncSession = Depends(get_db)):
    total = (await db.execute(
        select(func.count(Job.id)).where(Job.is_active == True)
    )).scalar()

    week_ago = datetime.utcnow() - timedelta(days=7)
    new_week = (await db.execute(
        select(func.count(Job.id)).where(
            Job.is_active == True,
            Job.synced_at >= week_ago
        )
    )).scalar()

    avg_salary = (await db.execute(
        select(func.avg(Job.salary_min)).where(
            Job.is_active == True,
            Job.salary_min != None,
            Job.salary_predicted == False,
        )
    )).scalar()

    top_county_row = (await db.execute(
        select(Job.county, func.count(Job.id).label("cnt"))
        .where(Job.is_active == True, Job.county != None)
        .group_by(Job.county)
        .order_by(text("cnt DESC"))
        .limit(1)
    )).first()

    cat_count = (await db.execute(
        select(func.count(func.distinct(Job.category)))
        .where(Job.is_active == True, Job.category != None)
    )).scalar()

    return {
        "total_jobs": total,
        "new_this_week": new_week,
        "avg_salary": round(avg_salary) if avg_salary else None,
        "top_county": top_county_row[0] if top_county_row else None,
        "categories": cat_count,
    }


@router.get("/by-category", response_model=list[CategoryCount])
async def by_category(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(
        select(Job.category, func.count(Job.id).label("count"))
        .where(Job.is_active == True, Job.category != None)
        .group_by(Job.category)
        .order_by(text("count DESC"))
        .limit(15)
    )).all()
    return [{"category": r[0], "count": r[1]} for r in rows]


@router.get("/by-county", response_model=list[CountyCount])
async def by_county(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(
        select(Job.county, func.count(Job.id).label("count"))
        .where(Job.is_active == True, Job.county != None)
        .group_by(Job.county)
        .order_by(text("count DESC"))
    )).all()
    return [{"county": r[0], "count": r[1]} for r in rows]


@router.get("/top-skills", response_model=list[SkillCount])
async def top_skills(limit: int = 20, db: AsyncSession = Depends(get_db)):
    # unnest the skills array and count
    rows = (await db.execute(
        text("""
            SELECT skill, COUNT(*) as cnt
            FROM jobs, unnest(skills) AS skill
            WHERE is_active = true
            GROUP BY skill
            ORDER BY cnt DESC
            LIMIT :limit
        """),
        {"limit": limit}
    )).all()
    return [{"skill": r[0], "count": r[1]} for r in rows]


@router.get("/salary-distribution", response_model=list[SalaryBucket])
async def salary_distribution(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(
        text("""
            SELECT
                CASE
                    WHEN salary_min < 30000 THEN 'Under €30k'
                    WHEN salary_min < 40000 THEN '€30k - €40k'
                    WHEN salary_min < 50000 THEN '€40k - €50k'
                    WHEN salary_min < 60000 THEN '€50k - €60k'
                    WHEN salary_min < 80000 THEN '€60k - €80k'
                    WHEN salary_min < 100000 THEN '€80k - €100k'
                    ELSE 'Over €100k'
                END as range,
                COUNT(*) as count
            FROM jobs
            WHERE is_active = true
              AND salary_min IS NOT NULL
              AND salary_predicted = false
            GROUP BY range
            ORDER BY MIN(salary_min)
        """)
    )).all()
    return [{"range": r[0], "count": r[1]} for r in rows]


@router.get("/sync-logs")
async def sync_logs(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(
        select(SyncLog).order_by(SyncLog.started_at.desc()).limit(20)
    )).scalars().all()
    return [{
        "id": r.id,
        "started_at": r.started_at.isoformat(),
        "finished_at": r.finished_at.isoformat() if r.finished_at else None,
        "jobs_fetched": r.jobs_fetched,
        "jobs_added": r.jobs_added,
        "jobs_updated": r.jobs_updated,
        "status": r.status,
        "error": r.error,
    } for r in rows]
