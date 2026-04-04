"""
BDD step definitions for adzuna_service.feature
Pure unit tests – no database or HTTP client required.
"""
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from services.adzuna import extract_county, parse_posted_date, normalize_job

scenarios("../features/adzuna_service.feature")


# ---------------------------------------------------------------------------
# When – call the service functions
# ---------------------------------------------------------------------------

@when(parsers.parse('I extract the county from "{location}"'), target_fixture="county_result")
def call_extract_county(location):
    return extract_county(location)


@when("I extract the county from None", target_fixture="county_result")
def call_extract_county_none():
    return extract_county(None)


@when(parsers.parse('I parse the posted date "{date_str}"'), target_fixture="parsed_date")
def call_parse_date(date_str):
    return parse_posted_date(date_str)


@when("I parse the posted date None", target_fixture="parsed_date")
def call_parse_date_none():
    return parse_posted_date(None)


@when("I normalize the raw job", target_fixture="normalized_job")
def call_normalize_job(raw_job_dict):
    return normalize_job(raw_job_dict)


# ---------------------------------------------------------------------------
# Given – provide raw job dictionaries
# ---------------------------------------------------------------------------

@given("a complete raw Adzuna job dictionary", target_fixture="raw_job_dict")
def complete_raw_job():
    return {
        "id": "abc123",
        "title": "Senior Python Developer",
        "company": {"display_name": "Tech Ireland Ltd"},
        "location": {"display_name": "Dublin, Ireland"},
        "category": {"label": "IT Jobs", "tag": "it-jobs"},
        "contract_type": "permanent",
        "contract_time": "full_time",
        "salary_min": 65000,
        "salary_max": 85000,
        "salary_is_predicted": "0",
        "description": "We are looking for a senior Python developer.",
        "redirect_url": "https://www.adzuna.co.uk/jobs/ad/abc123",
        "created": "2026-01-15T10:30:00Z",
    }


@given("a minimal raw Adzuna job dictionary", target_fixture="raw_job_dict")
def minimal_raw_job():
    return {
        "id": "min001",
        "title": "Developer",
    }


# ---------------------------------------------------------------------------
# Then – assert results
# ---------------------------------------------------------------------------

@then(parsers.parse('the county result is "{expected}"'))
def check_county(county_result, expected):
    assert county_result == expected


@then("no county result is returned")
def check_no_county(county_result):
    assert county_result is None


@then("I get a valid datetime object")
def check_datetime(parsed_date):
    from datetime import datetime
    assert parsed_date is not None
    assert isinstance(parsed_date, datetime)


@then("the datetime has no timezone info")
def check_no_timezone(parsed_date):
    assert parsed_date.tzinfo is None


@then("no parsed date is returned")
def check_no_date(parsed_date):
    assert parsed_date is None


@then("the result contains an adzuna_id")
def check_adzuna_id(normalized_job):
    assert "adzuna_id" in normalized_job
    assert normalized_job["adzuna_id"] != ""


@then("the result contains a title")
def check_title(normalized_job):
    assert "title" in normalized_job


@then("the result contains a company")
def check_company(normalized_job):
    assert "company" in normalized_job


@then("the result is a valid dictionary with no missing keys")
def check_minimal_normalized(normalized_job):
    required_keys = {
        "adzuna_id", "title", "company", "location", "county",
        "category", "category_tag", "contract_type", "contract_time",
        "salary_min", "salary_max", "salary_predicted",
        "description", "redirect_url", "posted_date", "raw_data",
    }
    assert required_keys.issubset(normalized_job.keys())
