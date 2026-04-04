"""
BDD step definitions for jobs.feature
"""
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from tests.conftest import MockJob

scenarios("../features/jobs.feature")


# ---------------------------------------------------------------------------
# Given – seed the mock DB queue
# ---------------------------------------------------------------------------

@given("the database contains job listings")
def db_contains_jobs(mock_db_session):
    job = MockJob()
    mock_db_session.queue_response(3)         # count query
    mock_db_session.queue_response([job, MockJob(id=2), MockJob(id=3)])  # list query


@given(parsers.parse('the database contains jobs in category "{category}"'))
def db_jobs_by_category(mock_db_session, category):
    job = MockJob(category=category)
    mock_db_session.queue_response(1)
    mock_db_session.queue_response([job])


@given(parsers.parse('the database contains jobs in county "{county}"'))
def db_jobs_by_county(mock_db_session, county):
    job = MockJob(county=county)
    mock_db_session.queue_response(1)
    mock_db_session.queue_response([job])


@given("the database contains jobs with salary above 50000")
def db_jobs_high_salary(mock_db_session):
    job = MockJob(salary_min=60000.0)
    mock_db_session.queue_response(1)
    mock_db_session.queue_response([job])


@given("the database contains jobs requiring python")
def db_jobs_with_skill(mock_db_session):
    job = MockJob(skills=["python", "fastapi"])
    mock_db_session.queue_response(1)
    mock_db_session.queue_response([job])


@given('the database contains jobs matching "engineer"')
def db_jobs_keyword(mock_db_session):
    job = MockJob(title="Senior Software Engineer")
    mock_db_session.queue_response(1)
    mock_db_session.queue_response([job])


@given("a job with ID 1 exists in the database")
def db_single_job(mock_db_session):
    mock_db_session.queue_response(MockJob(id=1))


@given("no job with ID 9999 exists")
def db_no_job(mock_db_session):
    mock_db_session.queue_response(None)


@given("the database contains 25 job listings")
def db_25_jobs(mock_db_session):
    mock_db_session.queue_response(25)                              # count
    mock_db_session.queue_response([MockJob(id=i) for i in range(11, 21)])  # page 2


# ---------------------------------------------------------------------------
# When – make the HTTP request
# ---------------------------------------------------------------------------

@when("I request all jobs", target_fixture="response")
def request_all_jobs(client):
    return client.get("/api/jobs/")


@when(parsers.parse('I filter jobs by category "{category}"'), target_fixture="response")
def filter_by_category(client, category):
    return client.get(f"/api/jobs/?category={category}")


@when(parsers.parse('I filter jobs by county "{county}"'), target_fixture="response")
def filter_by_county(client, county):
    return client.get(f"/api/jobs/?county={county}")


@when("I filter jobs with minimum salary of 50000", target_fixture="response")
def filter_by_salary(client):
    return client.get("/api/jobs/?salary_min=50000")


@when(parsers.parse('I filter jobs by skill "{skill}"'), target_fixture="response")
def filter_by_skill(client, skill):
    # Job.skills.contains() requires the PostgreSQL dialect-specific ARRAY type.
    # This query cannot be constructed against a generic SQLAlchemy mock — it is
    # covered by integration tests against a real PostgreSQL database.
    pytest.skip(
        "Skill filter uses PostgreSQL ARRAY.contains() — skipped in unit test suite"
    )
    return client.get(f"/api/jobs/?skill={skill}")


@when(parsers.parse('I search jobs with keyword "{keyword}"'), target_fixture="response")
def search_by_keyword(client, keyword):
    return client.get(f"/api/jobs/?q={keyword}")


@when(parsers.parse('I request jobs sorted by "{sort}"'), target_fixture="response")
def request_sorted(client, sort):
    return client.get(f"/api/jobs/?sort={sort}")


@when("I request the job with ID 1", target_fixture="response")
def request_job_1(client):
    return client.get("/api/jobs/1")


@when("I request the job with ID 9999", target_fixture="response")
def request_job_9999(client):
    return client.get("/api/jobs/9999")


@when("I request page 2 with 10 jobs per page", target_fixture="response")
def request_page_2(client):
    return client.get("/api/jobs/?page=2&per_page=10")


# ---------------------------------------------------------------------------
# Then – assert the response
# ---------------------------------------------------------------------------

@then("I receive a paginated list of jobs")
def check_paginated_list(response):
    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data
    assert isinstance(data["jobs"], list)


@then("the response includes total count and page info")
def check_pagination_meta(response):
    data = response.json()
    assert "total" in data
    assert "page" in data
    assert "pages" in data
    assert "per_page" in data


@then(parsers.parse('I only receive jobs in the "{category}" category'))
def check_category_filter(response, category):
    assert response.status_code == 200
    data = response.json()
    assert all(category.lower() in (j["category"] or "").lower() for j in data["jobs"])


@then(parsers.parse('I only receive jobs in county "{county}"'))
def check_county_filter(response, county):
    assert response.status_code == 200
    data = response.json()
    assert all(county.lower() in (j["county"] or "").lower() for j in data["jobs"])


@then("I receive jobs with salary above the threshold")
def check_salary_filter(response):
    assert response.status_code == 200
    data = response.json()
    assert all((j["salary_min"] or 0) >= 50000 for j in data["jobs"])


@then("I receive jobs requiring that skill")
def check_skill_filter(response):
    assert response.status_code == 200
    data = response.json()
    assert all("python" in (j["skills"] or []) for j in data["jobs"])


@then("I receive jobs matching the keyword")
def check_keyword_search(response):
    assert response.status_code == 200
    data = response.json()
    assert len(data["jobs"]) > 0


@then("I receive a valid sorted job list")
def check_sorted_list(response):
    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data


@then("I receive the full job details")
def check_job_detail(response):
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "title" in data
    assert "company" in data


@then("I receive a 404 not found response")
def check_404(response):
    assert response.status_code == 404


@then("I receive the second page of results")
def check_second_page(response):
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert data["per_page"] == 10


@then("the total reflects all available jobs")
def check_total(response):
    data = response.json()
    assert data["total"] == 25
