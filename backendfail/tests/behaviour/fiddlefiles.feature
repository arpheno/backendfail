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
    When I try to access edit the file
    Then The fiddle should be copied
    And I should be redirected to the file

  Scenario: Viewing edit mode files with login
    Given I'm logged in as peter
    And There is a file
    And I own the file
    When I try to access edit the file
    Then I should be able to view it

  Scenario: Editing files with login
    Given I'm logged in as peter
    And There is a file
    And I own the file
    When I try to edit the file
    Then It should be edited

  Scenario: Viewing editing files of others
    Given I'm logged in as peter
    And There is a file
    And I don't own the file
    When I try to access edit the file
    Then The fiddle should be copied
    And I should own the copy
    And I should be redirected to the file

  Scenario: Editing files of others
    Given I'm logged in as peter
    And There is a file
    And I don't own the file
    When I try to edit the file
    Then Permission should be denied

  Scenario: Creating fiddles without login
    Given I'm logged in as no one
    When I try to create a fiddle
    Then A fiddle should be created

  Scenario: Creating fiddles with login
    Given I'm logged in as peter
    When I try to create a fiddle
    Then A fiddle should be created

  Scenario: Creating files with login
    Given I'm logged in as peter
    And There is a fiddle
    And I own the fiddle
    When I try to create a fiddlefile
    Then A file should be created

  Scenario: Renaming files with login
    Given I'm logged in as michaeljackson
    And There is a file
    And I own the file
    When I try to rename the file
    Then The file should be renamed

  Scenario: Deleting files with login
    Given I'm logged in as michaeljackson
    And There is a file
    And I own the file
    When I try to delete the file
    Then The file should be deleted

  Scenario: Claiming anonymous fiddles
    Given I'm logged in as peter
    And There is a file
    And The file is not owned by anyone
    When I try to access edit the file
    Then I should own the copy

