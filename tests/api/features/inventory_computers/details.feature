Feature: View Inventory Computer Information
    As an authorized tenant
    I want to be able to see details of my inventory inventory_computers

    Background: Test GET /inventory/computers/<mercury_id>
        Given the account is an authorized tenant
        And the inventory_computers client URL is /inventory/computers

    @positive @p0 @smoke
    Scenario: Get Inventory Computer Details
        Given a inventory_computers entity id is located for testing
        When I get the entity using the inventory_computers api
        Then the inventory_computers response status is 200 OK
        And the inventory_computers response contains valid single entity details

    @negative @p1
    Scenario Outline: Get inventory Computer Details With <invalid_mercury_id>
        Given a inventory_computers <invalid_mercury_id> is provided
        When I get the entity using the inventory_computers api
        Then the inventory_computers response status is <status_code> <reason>

        Examples: Invalid Loadbalancer IDs
        | invalid_mercury_id        | status_code          | reason    |
        | invalid_device_id_123     | 404                  | Not Found |
        | 0                         | 404                  | Not Found |
        | 9999999999999999999       | 404                  | Not Found |
        | ""                        | 404                  | Not Found |
        | !@#$%^&*()_               | 404                  | Not Found |
        | None                      | 404                  | Not Found |
        | 123e4567-e89b-12d3-a456-42665544000 | 404        | Not Found |
