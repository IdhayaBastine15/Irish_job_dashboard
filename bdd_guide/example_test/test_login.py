import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# 1. LINK TO THE FEATURE FILE
# This tells pytest where to find the plain-English Gherkin file.
# Pytest will automatically load all 'Scenarios' in the file as tests.
scenarios('login.feature')


# A fake helper class to pretend we are interacting with a browser or API
class FakeApp:
    def __init__(self):
        self.current_page = None
        self.message = None

    def navigate(self, page):
        self.current_page = page

# Pytest fixture to share our fake app between steps
@pytest.fixture
def app():
    return FakeApp()


# 2. DEFINE THE 'GIVEN' STEPS
@given("the user opens the login page")
def go_to_login_page(app):
    app.navigate("login")
    assert app.current_page == "login"


# 3. DEFINE THE 'WHEN' STEPS
@when("the user enters a valid username and password")
def enter_valid_details():
    # In a real test, you'd type text into browser fields here
    pass

@when("the user enters a valid username but an incorrect password")
def enter_invalid_details():
    pass

@when("clicks the login button")
def click_login(app):
    # Let's pretend our app logic happened here based on valid/invalid passwords
    # For this example, we'll just fake the state for the 'successful' path 
    # to show how 'Then' asserts work.
    pass


# 4. DEFINE THE 'THEN' STEPS
@then("the user should be redirected to the dashboard")
def check_dashboard_redirection(app):
    # Fake the redirect result
    app.current_page = "dashboard" 
    
    # This assertion is the actual core of the test
    assert app.current_page == "dashboard"

@then("a welcome message should be displayed")
def check_welcome_message(app):
    app.message = "Welcome back!"
    assert "Welcome" in app.message

@then(parsers.parse('an "{error_msg}" error message should appear'))
def check_error_message(app, error_msg):
    # Example using a parser to grab the specific string from the feature file
    app.message = "Invalid credentials"
    assert app.message == error_msg

@then("the user should remain on the login page")
def check_remain_on_login(app):
    app.current_page = "login"
    assert app.current_page == "login"
