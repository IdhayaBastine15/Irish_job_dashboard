"""
BDD step definitions for skill_extractor.feature
Pure unit tests – no database or HTTP client required.
"""
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from services.skill_extractor import extract_skills

scenarios("../features/skill_extractor.feature")


# ---------------------------------------------------------------------------
# Given – build the text input
# ---------------------------------------------------------------------------

@given('a job description containing "python" and "docker"', target_fixture="job_text")
def text_python_docker():
    return "We require python experience and proficiency with docker containers."


@given('a job description containing "excel" and "bloomberg"', target_fixture="job_text")
def text_excel_bloomberg():
    return "Candidates must be proficient in excel and have bloomberg terminal experience."


@given('a job description containing "nursing" and "icu"', target_fixture="job_text")
def text_nursing_icu():
    return "We are recruiting experienced nursing staff with icu background."


@given('a job description containing "PYTHON" in uppercase', target_fixture="job_text")
def text_python_uppercase():
    return "Strong PYTHON skills required along with SQL knowledge."


@given("an empty job description", target_fixture="job_text")
def text_empty():
    return ""


@given("a job description with no recognised skill keywords", target_fixture="job_text")
def text_no_skills():
    return "The candidate should be enthusiastic and willing to learn new things."


@given("a job description with both tech and finance keywords", target_fixture="job_text")
def text_mixed_skills():
    return "Looking for a python developer with excel and bloomberg experience for fintech role."


# ---------------------------------------------------------------------------
# When – run the extractor
# ---------------------------------------------------------------------------

@when("I extract skills from the text", target_fixture="extracted_skills")
def run_extraction(job_text):
    return extract_skills(job_text)


# ---------------------------------------------------------------------------
# Then – assert the results
# ---------------------------------------------------------------------------

@then(parsers.parse('"{skill}" is in the extracted skills'))
def check_skill_present(extracted_skills, skill):
    assert skill in extracted_skills, f"Expected '{skill}' in {extracted_skills}"


@then("the extracted skills list is empty")
def check_empty_skills(extracted_skills):
    assert extracted_skills == []


@then("skills from multiple categories are present")
def check_multiple_categories(extracted_skills):
    tech = {"python", "javascript", "docker", "react", "sql"}
    finance = {"excel", "bloomberg", "sap", "vba"}
    has_tech = bool(tech & set(extracted_skills))
    has_finance = bool(finance & set(extracted_skills))
    assert has_tech and has_finance, (
        f"Expected skills from both tech and finance categories, got: {extracted_skills}"
    )
