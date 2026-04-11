# Getting to Know Gherkin

**Gherkin** is the language we use to write BDD tests. It is designed to be readable by humans while being structured enough that a computer can understand it and run automated tests.

Gherkin uses simple keywords to define the state, action, and expected outcome of a test.

## Key Gherkin Keywords

The most important keywords in Gherkin are **Feature**, **Scenario**, **Given**, **When**, and **Then**. 

*   **`Feature`**: A high-level description of a software feature.
*   **`Scenario`**: A specific situation or test case within that feature.
*   **`Given`**: Sets up the initial state or context. (What is true before the action happens?)
*   **`When`**: Describes the action the user takes.
*   **`Then`**: Describes the expected outcome. (What happens as a result of the action?)
*   **`And` / `But`**: Used to chain multiple Given, When, or Then steps together smoothly.

---

## Example: Logging In

Let's look at an example. We save Gherkin tests in files ending with **`.feature`**. 

```gherkin
Feature: User Login
  As a registered user
  I want to log into my account
  So that I can see my dashboard

  Scenario: Successful login with correct credentials
    Given the user opens the login page
    When the user enters a valid username and password
    And clicks the login button
    Then the user should be redirected to the dashboard
    And a welcome message should be displayed

  Scenario: Failed login with wrong password
    Given the user opens the login page
    When the user enters a valid username but an incorrect password
    And clicks the login button
    Then an "Invalid credentials" error message should appear
    And the user should remain on the login page
```

## Why it works

Notice how the `Feature` block describes *why* we are building this (for context).

Then, each `Scenario` is a very specific test case. 
- The **Given** block puts the system in a known state (on the login page).
- The **When** block performs the action we are testing (entering details and clicking).
- The **Then** block asserts what should have happened (redirection, error messages).

It reads exactly like a checklist from a QA tester.

[Next up: How do we actually run this using Python and Pytest?](03_Pytest_BDD_Basic_Example.md)
