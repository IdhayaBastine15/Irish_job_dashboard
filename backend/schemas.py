from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class JobOut(BaseModel):
    id: int
    adzuna_id: str
    title: str
    company: Optional[str]
    location: Optional[str]
    county: Optional[str]
    category: Optional[str]
    contract_type: Optional[str]
    contract_time: Optional[str]
    salary_min: Optional[float]
    salary_max: Optional[float]
    salary_predicted: bool
    description: Optional[str]
    redirect_url: Optional[str]
    skills: list[str]
    posted_date: Optional[datetime]
    synced_at: datetime

    class Config:
        from_attributes = True


class JobListOut(BaseModel):
    jobs: list[JobOut]
    total: int
    page: int
    pages: int
    per_page: int


class CategoryCount(BaseModel):
    category: str
    count: int


class CountyCount(BaseModel):
    county: str
    count: int


class SkillCount(BaseModel):
    skill: str
    count: int


class SalaryBucket(BaseModel):
    range: str
    count: int


class StatsOverview(BaseModel):
    total_jobs: int
    new_this_week: int
    avg_salary: Optional[float]
    top_county: Optional[str]
    categories: int


class InsightRequest(BaseModel):
    context: str  # e.g. "software developer in Dublin"


class InsightResponse(BaseModel):
    summary: str
    top_skills: list[str]
    skill_gaps: list[str]
    market_note: str


class ApplicationCreate(BaseModel):
    job_title: str
    company: str
    status: Optional[str] = "applied"

class ApplicationUpdate(BaseModel):
    job_title: Optional[str] = None
    company: Optional[str] = None
    status: Optional[str] = None

class ApplicationOut(ApplicationCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class ResumeOut(BaseModel):
    id: int
    filename: str
    extracted_skills: list[str]
    uploaded_at: datetime
    class Config:
        from_attributes = True

class JobMatchOut(BaseModel):
    job: JobOut
    score: float
    matched_skills: list[str]
    fit: str
