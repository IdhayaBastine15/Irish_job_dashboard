Feature: Job Listings API
  As a job seeker
  I want to browse and search job listings
  So that I can find relevant job opportunities

  Scenario: List all active jobs
    Given the database contains job listings
    When I request all jobs
    Then I receive a paginated list of jobs
    And the response includes total count and page info

  Scenario: Filter jobs by category
    Given the database contains jobs in category "IT Jobs"
    When I filter jobs by category "IT Jobs"
    Then I only receive jobs in the "IT Jobs" category

  Scenario: Filter jobs by county
    Given the database contains jobs in county "Dublin"
    When I filter jobs by county "Dublin"
    Then I only receive jobs in county "Dublin"

  Scenario: Filter jobs by minimum salary
    Given the database contains jobs with salary above 50000
    When I filter jobs with minimum salary of 50000
    Then I receive jobs with salary above the threshold

  Scenario: Filter jobs by skill
    Given the database contains jobs requiring python
    When I filter jobs by skill "python"
    Then I receive jobs requiring that skill

  Scenario: Search jobs by keyword
    Given the database contains jobs matching "engineer"
    When I search jobs with keyword "engineer"
    Then I receive jobs matching the keyword

  Scenario: Sort jobs by newest first
    Given the database contains job listings
    When I request jobs sorted by "newest"
    Then I receive a valid sorted job list

  Scenario: Sort jobs by highest salary
    Given the database contains job listings
    When I request jobs sorted by "salary_high"
    Then I receive a valid sorted job list

  Scenario: Get a specific job by ID
    Given a job with ID 1 exists in the database
    When I request the job with ID 1
    Then I receive the full job details

  Scenario: Get a non-existent job returns 404
    Given no job with ID 9999 exists
    When I request the job with ID 9999
    Then I receive a 404 not found response

  Scenario: Paginate job results
    Given the database contains 25 job listings
    When I request page 2 with 10 jobs per page
    Then I receive the second page of results
    And the total reflects all available jobs
