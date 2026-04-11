Feature: Job Applications Tracker
  As a job seeker
  I want to track my job applications
  So that I can remember what jobs I have applied to and what stage they are at

  Scenario: Creating a new job application
    Given the user has application details for "Software Engineer" at "TechCorp"
    When the user submits a new application
    Then the application should be saved successfully with status "applied"
    And the application id should be returned

  Scenario: Fetching list of all job applications
    Given the user has several tracked applications
    When the user requests all applications
    Then the system should return a list of applications

  Scenario: Updating an application status
    Given the user has an existing application
    When the user updates the status to "interview"
    Then the application status should be saved as "interview"

  Scenario: Deleting an application
    Given the user has an existing application
    When the user deletes the application
    Then the application should be removed successfully
