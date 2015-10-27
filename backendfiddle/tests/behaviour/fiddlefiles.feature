Feature: FiddleFiles
    Viewing, forking and editing functionality for source files

Scenario: Viewing files without login
    Given I'm logged in as no one
    And There is a file
    When I look at the file
    Then I should not be able to edit it

Scenario: Editing files without login
    Given I'm logged in as no one
    And There is a file
    When I try to edit the file
    Then I should be redirected to the login

  Scenario: Editing files with login
    Given I'm logged in as peter
    And There is a file
    And I own the file
    When I try to edit the file
    Then It should be edited

Scenario: Creating fiddles without login
    Given I'm logged in as no one
    When I try to create a fiddle
    Then I should be redirected to the login
Scenario: Creating fiddles with login
    Given I'm logged in as peter
    When I try to create a fiddle
    Then A fiddle should be created
