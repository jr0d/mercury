Feature: View Active Computer Information
    As an authorized tenant
    I want to be able to see details of my active mercury_computers

    Background: Test GET /active/computers/<mercury_id>
        Given the account is an authorized tenant
        And the mercury_computers client URL is /active/computers

    @positive @p0 @smoke
    Scenario: Get Active Computer Details
        Given a mercury_computers entity id is located for testing
        When I get the entity using the mercury_computers api
        Then the mercury_computers response status is 200 OK
        And the mercury_computers response contains valid single entity details

    @negative @p1    
    Scenario Outline: Get Active Computer Details With <invalid_mercury_id>
        Given a mercury_computers <invalid_mercury_id> is provided
        When I get the entity using the mercury_computers api
        Then the mercury_computers response status is <status_code> <reason>

        Examples: Invalid Loadbalancer IDs
        | invalid_mercury_id        | status_code          | reason    |
        | invalid_device_id_123     | 404                  | NOT FOUND |
        | 0                         | 404                  | NOT FOUND |
        | 9999999999999999999       | 404                  | NOT FOUND |
        | ""                        | 404                  | NOT FOUND |
        | !@#$%^&*()_               | 404                  | NOT FOUND |
        | None                      | 404                  | NOT FOUND |
        | 123e4567-e89b-12d3-a456-42665544000 | 404        | NOT FOUND |
