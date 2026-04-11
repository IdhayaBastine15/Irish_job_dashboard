Feature: Resume Parsing and Matching
  As a candidate
  I want to upload my resume and match it against jobs
  So that I can see my fit for open positions

  Scenario: Uploading a new resume
    Given the user has a resume file named "resume.txt"
    When the user uploads the resume
    Then the system should parse the resume
    And save the resume info successfully

  Scenario: Getting resume matches against jobs
    Given the user has an uploaded resume with extracted skills
    And the system has jobs containing various skills
    When the user requests job matches
    Then the system should return a list of matched jobs
    And the jobs should include a score and fit label
