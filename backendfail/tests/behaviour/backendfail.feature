Feature: backendfail
  main ui testing

  Scenario: Viewing the main page
    Given I have a web browser
    When I open the main page
    Then the title should be backend.fail

  Scenario: Redirection to facebook
    Given I have a web browser
    When I try to login via facebook
    Then I should be redirected to facebook

  Scenario: Redirection to backendfail
    Given I have a web browser
    When I try to login via facebook
    And I succeed at logging in via facebook
    Then I should be redirected to _
#  Scenario: Creating a new fail
#    Given I have a web browser
#    When I try to login via facebook
#    And I succeed at logging in via facebook
#    And I try to create a new djangofail
#    Then I should be redirected to a new fail
#    And The preview should contain success

