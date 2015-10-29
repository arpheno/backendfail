Feature: backendfail
  main ui testing

  Scenario: Viewing the main page
    Given I have a web browser
    When I open the main page
    Then the title should be backend.fail

