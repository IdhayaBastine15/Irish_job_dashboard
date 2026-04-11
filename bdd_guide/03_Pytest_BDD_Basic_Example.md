# Connecting English to Python with Pytest-BDD

Now that we know how to write `.feature` files in Gherkin, how do we make the computer actually *test* the application using them?

This is where **`pytest-bdd`** comes in. It connects your plain English sentences to small snippets of Python code.

## The Two Halves of a Test

Every BDD test in our project is made of two files that live side-by-side:
1. **The Feature File (`login.feature`)**: The English description.
2. **The Step Definitions File (`test_login.py`)**: The Python code that maps to the English.

## How the Magic Works

In our Python file, we use "decorators" (special tags above functions) to link Python code to our English sentences.

Let's say we have this step in our `.feature` file:
> `Given the user opens the login page`

In our Python file (`test_login.py`), we create a function and tell pytest to run it *whenever it sees that exact sentence*:

```python
from pytest_bdd import given

@given("the user opens the login page")
def go_to_login_page():
    # Python code goes here to instruct the browser to go to /login
    browser.navigate("http://localhost:3000/login")
```

When you run your tests, pytest reads the feature file. Whenever it reads `Given the user opens the login page`, it knows to jump into `test_login.py` and run the `go_to_login_page()` function.

## Complete Example Workflow

1. You write a complete `.feature` file with a `Scenario`.
2. You create Python functions for every unique `Given`, `When`, and `Then` sentence in your feature file.
3. In the Python function for a `Then` step, you use simple `assert` statements to check if the app did what it was supposed to do.

```python
from pytest_bdd import then

@then("the user should be redirected to the dashboard")
def check_dashboard_redirection():
    # Verify the current URL matches the dashboard URL
    assert browser.current_url == "http://localhost:3000/dashboard"
```

## Summary

That's the entire testing flow! 
1. Write the human-readable **behavior** in `features/`.
2. Write the **Python automation scripts** in `tests/` that match the English steps.
3. Run `pytest` to automate the browser and verify the app works as described!

*Check out the `example_test` directory to see a complete working file setup.*
