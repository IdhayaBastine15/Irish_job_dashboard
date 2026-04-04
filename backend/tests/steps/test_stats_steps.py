"""
BDD step definitions for stats.feature
"""
import pytest
from pytest_bdd import scenarios, given, when, then
from tests.conftest import MockJob, MockSyncLog

scenarios("../features/stats.feature")


# ---------------------------------------------------------------------------
# Given – seed the mock DB queue
# ---------------------------------------------------------------------------

@given("there are jobs in the database")
def db_has_jobs(mock_db_session):
    # overview: 5 sequential queries
    mock_db_session.queue_response(247)                   # total_jobs
    mock_db_session.queue_response(15)                    # new_this_week
    mock_db_session.queue_response(58500.0)               # avg_salary
    mock_db_session.queue_response([("Dublin", 85)])      # top_county → .first()
    mock_db_session.queue_response(8)                     # categories count


@given("there are jobs across multiple categories")
def db_jobs_categories(mock_db_session):
    mock_db_session.queue_response([
        ("IT Jobs", 85),
        ("Engineering Jobs", 42),
        ("Finance Jobs", 30),
    ])


@given("there are jobs across multiple counties")
def db_jobs_counties(mock_db_session):
    mock_db_session.queue_response([
        ("Dublin", 110),
        ("Cork", 45),
        ("Galway", 22),
    ])


@given("there are jobs with skills in the database")
def db_jobs_skills(mock_db_session):
    mock_db_session.queue_response([
        ("python", 60),
        ("javascript", 55),
        ("docker", 40),
        ("react", 35),
        ("sql", 30),
    ])


@given("there are jobs with salary data")
def db_jobs_salary(mock_db_session):
    mock_db_session.queue_response([
        ("€40k - €50k", 35),
        ("€50k - €60k", 60),
        ("€60k - €80k", 45),
        ("Over €100k", 10),
    ])


@given("sync operations have been recorded")
def db_sync_logs(mock_db_session):
    log = MockSyncLog()
    mock_db_session.queue_response([log])


# ---------------------------------------------------------------------------
# When – make the HTTP request
# ---------------------------------------------------------------------------

@when("I request the market overview", target_fixture="response")
def request_overview(client):
    return client.get("/api/stats/overview")


@when("I request jobs by category", target_fixture="response")
def request_by_category(client):
    return client.get("/api/stats/by-category")


@when("I request jobs by county", target_fixture="response")
def request_by_county(client):
    return client.get("/api/stats/by-county")


@when("I request the top skills", target_fixture="response")
def request_top_skills(client):
    return client.get("/api/stats/top-skills")


@when("I request the top 5 skills", target_fixture="response")
def request_top_5_skills(client):
    return client.get("/api/stats/top-skills?limit=5")


@when("I request the salary distribution", target_fixture="response")
def request_salary_dist(client):
    return client.get("/api/stats/salary-distribution")


@when("I request the sync logs", target_fixture="response")
def request_sync_logs(client):
    return client.get("/api/stats/sync-logs")


# ---------------------------------------------------------------------------
# Then – assert the response
# ---------------------------------------------------------------------------

@then("I receive the total jobs count")
def check_total_jobs(response):
    assert response.status_code == 200
    data = response.json()
    assert "total_jobs" in data
    assert isinstance(data["total_jobs"], int)


@then("I receive the new jobs this week count")
def check_new_this_week(response):
    data = response.json()
    assert "new_this_week" in data
    assert isinstance(data["new_this_week"], int)


@then("I receive the average salary")
def check_avg_salary(response):
    data = response.json()
    assert "avg_salary" in data


@then("I receive the top county")
def check_top_county(response):
    data = response.json()
    assert "top_county" in data
    assert data["top_county"] == "Dublin"


@then("I receive a list of categories with counts")
def check_categories(response):
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "category" in data[0]
    assert "count" in data[0]


@then("categories are ordered by job count")
def check_categories_ordered(response):
    data = response.json()
    counts = [item["count"] for item in data]
    assert counts == sorted(counts, reverse=True)


@then("I receive a list of counties with counts")
def check_counties(response):
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert "county" in data[0]
    assert "count" in data[0]


@then("I receive a ranked list of skills with counts")
def check_skills(response):
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert "skill" in data[0]
    assert "count" in data[0]


@then("I receive no more than 5 skills")
def check_skill_limit(response):
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 5


@then("I receive salary buckets with counts")
def check_salary_buckets(response):
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert "range" in data[0]
    assert "count" in data[0]


@then("I receive a list of sync log entries")
def check_sync_logs(response):
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@then("each entry has a status field")
def check_sync_log_status(response):
    data = response.json()
    assert all("status" in entry for entry in data)
