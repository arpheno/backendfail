Feature: FiddleFiles
    Viewing, forking and editing functionality for source files

Scenario: Viewing files without login
    Given I'm not logged in
    And There is a file
    When I look at the file
    Then I should not be able to edit it
