Feature: Adzuna Service Helper Functions
  As a developer
  I want the Adzuna service to correctly process raw API data
  So that job information is accurately stored in the database

  Scenario: Extract a recognised Irish county from a location string
    When I extract the county from "Dublin City Centre"
    Then the county result is "Dublin"

  Scenario: Extract county using partial match
    When I extract the county from "Cork, Ireland"
    Then the county result is "Cork"

  Scenario: Return None when no county matches
    When I extract the county from "London, UK"
    Then no county result is returned

  Scenario: Return None for empty location input
    When I extract the county from None
    Then no county result is returned

  Scenario: Parse a valid ISO 8601 date string
    When I parse the posted date "2026-01-15T10:30:00Z"
    Then I get a valid datetime object
    And the datetime has no timezone info

  Scenario: Return None for an unparseable date string
    When I parse the posted date "not-a-date"
    Then no parsed date is returned

  Scenario: Return None when date input is None
    When I parse the posted date None
    Then no parsed date is returned

  Scenario: Normalize a complete raw Adzuna job response
    Given a complete raw Adzuna job dictionary
    When I normalize the raw job
    Then the result contains an adzuna_id
    And the result contains a title
    And the result contains a company

  Scenario: Normalize a minimal raw Adzuna job response
    Given a minimal raw Adzuna job dictionary
    When I normalize the raw job
    Then the result is a valid dictionary with no missing keys
