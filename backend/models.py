from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, Boolean, Float, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from database import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    adzuna_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    company: Mapped[str] = mapped_column(String(200))
    location: Mapped[str] = mapped_column(String(150))
    county: Mapped[str | None] = mapped_column(String(60))
    category: Mapped[str | None] = mapped_column(String(100))
    category_tag: Mapped[str | None] = mapped_column(String(100))  # adzuna raw tag
    contract_type: Mapped[str | None] = mapped_column(String(50))  # permanent, contract
    contract_time: Mapped[str | None] = mapped_column(String(50))  # full_time, part_time
    salary_min: Mapped[float | None] = mapped_column(Float)
    salary_max: Mapped[float | None] = mapped_column(Float)
    salary_predicted: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str | None] = mapped_column(Text)
    redirect_url: Mapped[str | None] = mapped_column(String(1000))
    skills: Mapped[list | None] = mapped_column(ARRAY(String))  # extracted by spacy
    raw_data: Mapped[dict | None] = mapped_column(JSONB)  # full adzuna response
    posted_date: Mapped[datetime | None] = mapped_column(DateTime)
    synced_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "adzuna_id": self.adzuna_id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "county": self.county,
            "category": self.category,
            "contract_type": self.contract_type,
            "contract_time": self.contract_time,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "salary_predicted": self.salary_predicted,
            "description": self.description,
            "redirect_url": self.redirect_url,
            "skills": self.skills or [],
            "posted_date": self.posted_date.isoformat() if self.posted_date else None,
            "synced_at": self.synced_at.isoformat() if self.synced_at else None,
        }


class SyncLog(Base):
    __tablename__ = "sync_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    jobs_fetched: Mapped[int] = mapped_column(Integer, default=0)
    jobs_added: Mapped[int] = mapped_column(Integer, default=0)
    jobs_updated: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="running")
    error: Mapped[str | None] = mapped_column(Text)
