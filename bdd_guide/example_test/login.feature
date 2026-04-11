Feature: Application Login
  As a registered user
  I want to log into my account
  So that I can see my dashboard

  Scenario: Successful login with correct credentials
    Given the user opens the login page
    When the user enters a valid username and password
    And clicks the login button
    Then the user should be redirected to the dashboard
    And a welcome message should be displayed

  Scenario: Failed login with a bad password
    Given the user opens the login page
    When the user enters a valid username but an incorrect password
    And clicks the login button
    Then an "Invalid credentials" error message should appear
    And the user should remain on the login page
