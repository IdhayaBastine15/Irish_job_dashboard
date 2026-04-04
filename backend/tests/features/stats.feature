Feature: Job Market Statistics API
  As a user
  I want to view job market statistics
  So that I can understand employment trends in Ireland

  Scenario: Get market overview statistics
    Given there are jobs in the database
    When I request the market overview
    Then I receive the total jobs count
    And I receive the new jobs this week count
    And I receive the average salary
    And I receive the top county

  Scenario: Get jobs grouped by category
    Given there are jobs across multiple categories
    When I request jobs by category
    Then I receive a list of categories with counts
    And categories are ordered by job count

  Scenario: Get jobs grouped by county
    Given there are jobs across multiple counties
    When I request jobs by county
    Then I receive a list of counties with counts

  Scenario: Get top skills in demand
    Given there are jobs with skills in the database
    When I request the top skills
    Then I receive a ranked list of skills with counts

  Scenario: Get top skills with a custom limit
    Given there are jobs with skills in the database
    When I request the top 5 skills
    Then I receive no more than 5 skills

  Scenario: Get salary distribution
    Given there are jobs with salary data
    When I request the salary distribution
    Then I receive salary buckets with counts

  Scenario: Get recent sync logs
    Given sync operations have been recorded
    When I request the sync logs
    Then I receive a list of sync log entries
    And each entry has a status field
