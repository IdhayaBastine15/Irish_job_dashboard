"""
BDD step definitions for insights.feature
"""
import pytest
from unittest.mock import AsyncMock, patch
from pytest_bdd import scenarios, given, when, then
from tests.conftest import MockJob

scenarios("../features/insights.feature")

# Shared mock insight responses
_MARKET_INSIGHT = {
    "summary": "The IT sector has strong demand.",
    "top_skills": ["python", "docker", "react"],
    "skill_gaps": ["kubernetes", "rust"],
    "market_note": "Remote roles are increasing.",
}

_JOB_INSIGHT = {
    "key_requirements": ["Python", "FastAPI", "PostgreSQL"],
    "nice_to_have": ["Docker", "AWS"],
    "seniority": "mid",
    "remote_friendly": True,
    "summary": "A mid-level backend engineering role.",
}


# ---------------------------------------------------------------------------
# Given – configure API key and DB
# ---------------------------------------------------------------------------

@given("the Claude API key is configured")
def api_key_set(mocker):
    mocker.patch("routers.insights.settings.anthropic_api_key", "sk-ant-test-key")


@given("the Claude API key is not set")
def api_key_missing(mocker):
    mocker.patch("routers.insights.settings.anthropic_api_key", "")


@given("there are IT jobs in the database")
def db_it_jobs(mock_db_session, mocker):
    # 4 queries: job_count, avg_salary, county_rows, skill_rows
    mock_db_session.queue_response(50)                            # job_count
    mock_db_session.queue_response(62000.0)                       # avg_salary
    mock_db_session.queue_response([("Dublin", 30), ("Cork", 10)])  # county breakdown
    mock_db_session.queue_response([("python", 25), ("docker", 20)])  # skills
    mocker.patch(
        "routers.insights.generate_market_insight",
        new=AsyncMock(return_value=_MARKET_INSIGHT),
    )


@given("a job with ID 1 exists")
def db_job_1(mock_db_session, mocker):
    mock_db_session.queue_response(MockJob(id=1))
    mocker.patch(
        "routers.insights.analyze_job_description",
        new=AsyncMock(return_value=_JOB_INSIGHT),
    )


@given("no job with ID 9999 exists")
def db_no_job_9999(mock_db_session):
    mock_db_session.queue_response(None)


# ---------------------------------------------------------------------------
# When – make the HTTP request
# ---------------------------------------------------------------------------

@when('I request market insights for "IT Jobs"', target_fixture="response")
def request_market_insight(client):
    return client.get("/api/insights/market/IT%20Jobs")


@when("I request the insight for job ID 1", target_fixture="response")
def request_job_insight_1(client):
    return client.get("/api/insights/job/1")


@when("I request the insight for job ID 9999", target_fixture="response")
def request_job_insight_9999(client):
    return client.get("/api/insights/job/9999")


# ---------------------------------------------------------------------------
# Then – assert the response
# ---------------------------------------------------------------------------

@then("I receive a market insight response")
def check_market_insight(response):
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


@then("the insight includes a summary field")
def check_summary(response):
    assert "summary" in response.json()


@then("the insight includes a top_skills field")
def check_top_skills(response):
    assert "top_skills" in response.json()


@then("the insight includes a skill_gaps field")
def check_skill_gaps(response):
    assert "skill_gaps" in response.json()


@then("I receive a 503 service unavailable response")
def check_503(response):
    assert response.status_code == 503


@then("I receive a job analysis response")
def check_job_analysis(response):
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


@then("the analysis includes a key_requirements field")
def check_key_requirements(response):
    assert "key_requirements" in response.json()


@then("the analysis includes a seniority field")
def check_seniority(response):
    assert "seniority" in response.json()


@then("I receive a 404 not found response")
def check_404(response):
    assert response.status_code == 404
