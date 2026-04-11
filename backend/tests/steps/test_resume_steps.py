import pytest
from pytest_bdd import scenarios, given, when, then, parsers
import io

scenarios("../features/resume.feature")

@pytest.fixture
def test_data():
    return {}

@given(parsers.parse('the user has a resume file named "{filename}"'))
def user_has_resume(test_data, filename):
    test_data["filename"] = filename
    test_data["content"] = b"dummy content"

@when("the user uploads the resume")
def upload_resume(client, mock_db_session, test_data, mocker):
    mocker.patch(
        "routers.resume.parse_resume", 
        return_value=("dummy text", ["python", "fastapi"])
    )
    files = {"file": (test_data["filename"], io.BytesIO(test_data["content"]), "application/pdf")}
    response = client.post("/api/resume/upload", files=files)
    test_data["response"] = response

@then("the system should parse the resume")
def system_parses(test_data):
    assert test_data["response"].status_code == 200

@then("save the resume info successfully")
def save_resume_info(test_data, mock_db_session):
    resp = test_data["response"]
    assert resp.json()["filename"] == test_data["filename"]
    assert "python" in resp.json()["extracted_skills"]
    assert len(mock_db_session.added) == 1
    assert mock_db_session.committed

@given("the user has an uploaded resume with extracted skills")
def uploaded_resume(mock_db_session):
    from models import UserResume
    from datetime import datetime
    resume = UserResume(id=1, filename="test.pdf", extracted_skills=["python", "sql", "fastapi"], uploaded_at=datetime.utcnow(), raw_text="dum")
    mock_db_session.queue_response([resume])

@given("the system has jobs containing various skills")
def system_jobs(mock_db_session):
    from tests.conftest import MockJob
    jobs = [
        MockJob(id=1, title="Backend Dev", skills=["python", "fastapi", "docker"]),
        MockJob(id=2, title="Data Analyst", skills=["sql", "excel"])
    ]
    mock_db_session.queue_response(jobs)

@when("the user requests job matches")
def request_job_matches(client, test_data):
    test_data["response"] = client.get("/api/resume/matches")

@then("the system should return a list of matched jobs")
def system_returns_matched_jobs(test_data):
    resp = test_data["response"]
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

@then("the jobs should include a score and fit label")
def jobs_include_score_and_fit(test_data):
    for match in test_data["response"].json():
        assert "score" in match
        assert "fit" in match
