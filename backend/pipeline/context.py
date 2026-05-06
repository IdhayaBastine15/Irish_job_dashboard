"""
Pipeline run context — passed through every stage.
Acts as the shared state bag for the entire pipeline run.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class StageResult:
    name: str
    status: str          # "success" | "failed" | "skipped"
    records_in: int = 0
    records_out: int = 0
    error: str | None = None
    started_at: datetime = field(default_factory=datetime.utcnow)
    finished_at: datetime | None = None

    def finish(self, records_out: int = 0, error: str | None = None):
        self.finished_at = datetime.utcnow()
        self.records_out = records_out
        self.status = "failed" if error else "success"
        self.error = error

    @property
    def duration_seconds(self) -> float | None:
        if self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        return None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "status": self.status,
            "records_in": self.records_in,
            "records_out": self.records_out,
            "error": self.error,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "duration_seconds": self.duration_seconds,
        }


@dataclass
class PipelineContext:
    run_id: int | None = None
    started_at: datetime = field(default_factory=datetime.utcnow)
    finished_at: datetime | None = None
    stages: list[StageResult] = field(default_factory=list)

    # data flowing between stages
    raw_jobs: list[dict] = field(default_factory=list)
    transformed_jobs: list[dict] = field(default_factory=list)

    # load stage counters
    jobs_added: int = 0
    jobs_updated: int = 0

    @property
    def status(self) -> str:
        if any(s.status == "failed" for s in self.stages):
            return "failed"
        if self.finished_at:
            return "success"
        return "running"

    def add_stage(self, name: str, records_in: int = 0) -> StageResult:
        stage = StageResult(name=name, status="running", records_in=records_in)
        self.stages.append(stage)
        return stage

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "status": self.status,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "jobs_added": self.jobs_added,
            "jobs_updated": self.jobs_updated,
            "total_fetched": len(self.raw_jobs),
            "stages": [s.to_dict() for s in self.stages],
        }
