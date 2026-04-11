import pytest
from pytest_bdd import scenarios, given, when, then, parsers

scenarios("../features/applications.feature")

@pytest.fixture
def test_data():
    return {}

@given(parsers.parse('the user has application details for "{job_title}" at "{company}"'))
def application_details(test_data, job_title, company):
    test_data["payload"] = {
        "job_title": job_title,
        "company": company,
        "status": "applied"
    }

@when("the user submits a new application")
def submit_application(client, mock_db_session, test_data):
    response = client.post("/api/applications/", json=test_data["payload"])
    test_data["response"] = response

@then(parsers.parse('the application should be saved successfully with status "{status}"'))
def application_saved(test_data, mock_db_session, status):
    resp = test_data["response"]
    assert resp.status_code == 200
    assert resp.json()["status"] == status
    assert len(mock_db_session.added) == 1
    assert mock_db_session.committed

@then("the application id should be returned")
def app_id_returned(test_data):
    resp = test_data["response"]
    assert "id" in resp.json()

@given("the user has several tracked applications")
def several_tracked_applications(mock_db_session):
    from models import Application
    from datetime import datetime
    apps = [
        Application(id=1, job_title="Engineer", company="Google", status="applied", created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
        Application(id=2, job_title="Dev", company="Meta", status="interview", created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    ]
    mock_db_session.queue_response(apps)

@when("the user requests all applications")
def request_all_applications(client, test_data):
    test_data["response"] = client.get("/api/applications/")

@then("the system should return a list of applications")
def verify_list_of_applications(test_data):
    resp = test_data["response"]
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 2

@given("the user has an existing application")
def existing_application(mock_db_session):
    from models import Application
    from datetime import datetime
    app = Application(id=1, job_title="Engineer", company="Google", status="applied", created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    mock_db_session.queue_response([app])
    mock_db_session.queue_response([app]) # Sometimes routers fetch again or delete needs a query

@when(parsers.parse('the user updates the status to "{status}"'))
def update_status(client, test_data, mock_db_session, status):
    # Need to refill the db fixture
    from models import Application
    from datetime import datetime
    app = Application(id=1, job_title="Engineer", company="Google", status="applied", created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    # Clear the queue and enqueue
    mock_db_session._queue.clear()
    mock_db_session.queue_response([app])
    test_data["response"] = client.patch("/api/applications/1", json={"status": status})

@then(parsers.parse('the application status should be saved as "{status}"'))
def verify_status_saved(test_data, mock_db_session, status):
    resp = test_data["response"]
    assert resp.status_code == 200
    assert resp.json()["status"] == status
    assert mock_db_session.committed

@when("the user deletes the application")
def delete_application(client, test_data, mock_db_session):
    from models import Application
    from datetime import datetime
    app = Application(id=1, job_title="Engineer", company="Google", status="applied", created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    mock_db_session._queue.clear()
    mock_db_session.queue_response([app])
    mock_db_session.queue_response([]) # for the delete
    test_data["response"] = client.delete("/api/applications/1")

@then("the application should be removed successfully")
def verify_deleted(test_data, mock_db_session):
    resp = test_data["response"]
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
    assert mock_db_session.committed
