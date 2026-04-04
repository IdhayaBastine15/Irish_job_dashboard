Feature: Skill Extraction Service
  As a developer
  I want to extract recognised skills from job description text
  So that jobs can be matched to candidate profiles

  Scenario: Extract technology skills from a job description
    Given a job description containing "python" and "docker"
    When I extract skills from the text
    Then "python" is in the extracted skills
    And "docker" is in the extracted skills

  Scenario: Extract finance skills from a job description
    Given a job description containing "excel" and "bloomberg"
    When I extract skills from the text
    Then "excel" is in the extracted skills
    And "bloomberg" is in the extracted skills

  Scenario: Extract healthcare skills from a job description
    Given a job description containing "nursing" and "icu"
    When I extract skills from the text
    Then "nursing" is in the extracted skills
    And "icu" is in the extracted skills

  Scenario: Skill extraction is case-insensitive
    Given a job description containing "PYTHON" in uppercase
    When I extract skills from the text
    Then "python" is in the extracted skills

  Scenario: Empty text returns no skills
    Given an empty job description
    When I extract skills from the text
    Then the extracted skills list is empty

  Scenario: Unrecognised text returns no skills
    Given a job description with no recognised skill keywords
    When I extract skills from the text
    Then the extracted skills list is empty

  Scenario: Extract skills from multiple categories
    Given a job description with both tech and finance keywords
    When I extract skills from the text
    Then skills from multiple categories are present
