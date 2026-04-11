"""
Shared fixtures for BDD tests.
Provides a mock database session and a TestClient wired to a minimal
FastAPI app (no lifespan / no real PostgreSQL required).
"""
from __future__ import annotations

import pytest
from collections import deque
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from database import get_db
from routers import jobs, stats, insights, applications, resume


# ---------------------------------------------------------------------------
# Mock SQLAlchemy result / session
# ---------------------------------------------------------------------------

class MockResult:
    """Mimics the subset of AsyncResult used across all routers."""

    def __init__(self, data=None):
        self._data = data  # raw value OR list

    # scalar()  – used by count/avg queries
    def scalar(self):
        if isinstance(self._data, list):
            return self._data[0] if self._data else None
        return self._data

    # scalar_one_or_none() – used by get-by-id queries
    def scalar_one_or_none(self):
        if isinstance(self._data, list):
            return self._data[0] if self._data else None
        return self._data

    # first() – used by top-county query
    def first(self):
        if isinstance(self._data, list):
            return self._data[0] if self._data else None
        return self._data

    # scalars().all() – used by list queries
    def scalars(self):
        return self

    def all(self):
        if isinstance(self._data, list):
            return self._data
        return [self._data] if self._data is not None else []

    # fetchall() – alias
    def fetchall(self):
        return self.all()


class MockAsyncSession:
    """
    Queue-based async session.
    Call queue_response(data) before each db.execute() that the handler
    will make, in the order they will be called.
    """

    def __init__(self):
        self._queue: deque[MockResult] = deque()
        self.committed = False
        self.added: list = []

    def queue_response(self, data):
        self._queue.append(MockResult(data))

    async def execute(self, *args, **kwargs):
        if self._queue:
            return self._queue.popleft()
        return MockResult([])

    async def commit(self):
        self.committed = True

    async def refresh(self, obj):
        if hasattr(obj, "id") and obj.id is None:
            obj.id = 1
        if hasattr(obj, "uploaded_at") and obj.uploaded_at is None:
            from datetime import datetime
            obj.uploaded_at = datetime.utcnow()

    def add(self, obj):
        self.added.append(obj)

    def delete(self, obj):
        pass

    # Support `async with AsyncSessionLocal() as db:`
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


# ---------------------------------------------------------------------------
# Mock domain objects
# ---------------------------------------------------------------------------

class MockJob:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", 1)
        self.adzuna_id = kwargs.get("adzuna_id", "adzuna_test_001")
        self.title = kwargs.get("title", "Software Engineer")
        self.company = kwargs.get("company", "Test Corp")
        self.location = kwargs.get("location", "Dublin City")
        self.county = kwargs.get("county", "Dublin")
        self.category = kwargs.get("category", "IT Jobs")
        self.category_tag = kwargs.get("category_tag", "it-jobs")
        self.contract_type = kwargs.get("contract_type", "permanent")
        self.contract_time = kwargs.get("contract_time", "full_time")
        self.salary_min = kwargs.get("salary_min", 55000.0)
        self.salary_max = kwargs.get("salary_max", 75000.0)
        self.salary_predicted = kwargs.get("salary_predicted", False)
        self.description = kwargs.get("description", "A great software engineering role")
        self.redirect_url = kwargs.get("redirect_url", "https://example.com/job/1")
        self.skills = kwargs.get("skills", ["python", "fastapi", "docker"])
        self.posted_date = kwargs.get("posted_date", datetime(2026, 1, 15))
        self.synced_at = kwargs.get("synced_at", datetime(2026, 1, 15))
        self.is_active = kwargs.get("is_active", True)


class MockSyncLog:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", 1)
        self.started_at = kwargs.get("started_at", datetime(2026, 1, 15, 10, 0, 0))
        self.finished_at = kwargs.get("finished_at", datetime(2026, 1, 15, 10, 5, 0))
        self.jobs_fetched = kwargs.get("jobs_fetched", 250)
        self.jobs_added = kwargs.get("jobs_added", 247)
        self.jobs_updated = kwargs.get("jobs_updated", 3)
        self.status = kwargs.get("status", "success")
        self.error = kwargs.get("error", None)


# ---------------------------------------------------------------------------
# Minimal test FastAPI app (no lifespan – no real DB on startup)
# ---------------------------------------------------------------------------

def _build_test_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(jobs.router)
    app.include_router(stats.router)
    app.include_router(insights.router)
    app.include_router(applications.router)
    app.include_router(resume.router)
    return app


_test_app = _build_test_app()


# ---------------------------------------------------------------------------
# Pytest fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_db_session():
    return MockAsyncSession()


@pytest.fixture
def client(mock_db_session):
    async def _override_get_db():
        yield mock_db_session

    _test_app.dependency_overrides[get_db] = _override_get_db
    with TestClient(_test_app) as c:
        yield c
    _test_app.dependency_overrides.clear()
