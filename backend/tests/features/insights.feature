Feature: AI Market Insights API
  As a user
  I want AI-powered insights about the job market
  So that I can make informed career decisions

  Scenario: Get market insight for a job category
    Given the Claude API key is configured
    And there are IT jobs in the database
    When I request market insights for "IT Jobs"
    Then I receive a market insight response
    And the insight includes a summary field
    And the insight includes a top_skills field
    And the insight includes a skill_gaps field

  Scenario: Market insight returns 503 when API key is missing
    Given the Claude API key is not set
    When I request market insights for "IT Jobs"
    Then I receive a 503 service unavailable response

  Scenario: Get insight for a specific job posting
    Given the Claude API key is configured
    And a job with ID 1 exists
    When I request the insight for job ID 1
    Then I receive a job analysis response
    And the analysis includes a key_requirements field
    And the analysis includes a seniority field

  Scenario: Job insight returns 404 for missing job
    Given the Claude API key is configured
    And no job with ID 9999 exists
    When I request the insight for job ID 9999
    Then I receive a 404 not found response
