from typing import Optional, List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from database import get_db
from models import Job, UserResume
from schemas import ResumeOut, JobMatchOut, JobOut
from services.resume_parser import parse_resume

router = APIRouter(prefix="/api/resume", tags=["resume"])


@router.post("/upload", response_model=ResumeOut)
async def upload_resume(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    allowed = {".pdf", ".docx", ".txt"}
    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in allowed:
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, or TXT files are supported")

    content = await file.read()
    raw_text, skills = parse_resume(file.filename, content)

    # keep only the latest resume
    await db.execute(delete(UserResume))
    resume = UserResume(
        filename=file.filename,
        extracted_skills=skills,
        raw_text=raw_text[:50000],
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)
    return resume


@router.get("/", response_model=Optional[ResumeOut])
async def get_resume(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserResume).order_by(UserResume.uploaded_at.desc()).limit(1))
    return result.scalar_one_or_none()


@router.get("/matches", response_model=List[JobMatchOut])
async def get_matches(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserResume).order_by(UserResume.uploaded_at.desc()).limit(1))
    resume = result.scalar_one_or_none()
    if not resume or not resume.extracted_skills:
        raise HTTPException(status_code=404, detail="No resume uploaded yet")

    resume_skills = set(s.lower() for s in resume.extracted_skills)

    jobs_result = await db.execute(select(Job).where(Job.skills.isnot(None)).limit(500))
    jobs = jobs_result.scalars().all()

    matches = []
    for job in jobs:
        job_skills = set(s.lower() for s in (job.skills or []))
        matched = resume_skills & job_skills
        if not job_skills:
            continue
        score = len(matched) / max(len(resume_skills), 1)
        fit = "strong" if score >= 0.35 else ("good" if score >= 0.15 else "less")
        matches.append({
            "job": JobOut.from_orm(job),
            "score": round(score, 3),
            "matched_skills": sorted(matched),
            "fit": fit,
        })

    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches
