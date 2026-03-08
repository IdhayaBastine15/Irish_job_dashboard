from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional
from database import get_db
from models import Job
from schemas import JobListOut, JobOut

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("/", response_model=JobListOut)
async def list_jobs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    q: Optional[str] = None,
    category: Optional[str] = None,
    county: Optional[str] = None,
    contract_type: Optional[str] = None,
    contract_time: Optional[str] = None,
    salary_min: Optional[float] = None,
    skill: Optional[str] = None,
    sort: str = Query("newest", regex="^(newest|oldest|salary_high|salary_low)$"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Job).where(Job.is_active == True)

    if q:
        stmt = stmt.where(or_(
            Job.title.ilike(f"%{q}%"),
            Job.company.ilike(f"%{q}%"),
            Job.description.ilike(f"%{q}%"),
        ))
    if category:
        stmt = stmt.where(Job.category.ilike(f"%{category}%"))
    if county:
        stmt = stmt.where(Job.county.ilike(f"%{county}%"))
    if contract_type:
        stmt = stmt.where(Job.contract_type == contract_type)
    if contract_time:
        stmt = stmt.where(Job.contract_time == contract_time)
    if salary_min:
        stmt = stmt.where(Job.salary_min >= salary_min)
    if skill:
        stmt = stmt.where(Job.skills.contains([skill.lower()]))

    # count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar()

    # sort
    if sort == "newest":
        stmt = stmt.order_by(Job.posted_date.desc().nullslast())
    elif sort == "oldest":
        stmt = stmt.order_by(Job.posted_date.asc().nullslast())
    elif sort == "salary_high":
        stmt = stmt.order_by(Job.salary_max.desc().nullslast())
    elif sort == "salary_low":
        stmt = stmt.order_by(Job.salary_min.asc().nullslast())

    stmt = stmt.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(stmt)
    jobs = result.scalars().all()

    return {
        "jobs": jobs,
        "total": total,
        "page": page,
        "pages": -(-total // per_page),  # ceiling div
        "per_page": per_page,
    }


@router.get("/{job_id}", response_model=JobOut)
async def get_job(job_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Job not found")
    return job
