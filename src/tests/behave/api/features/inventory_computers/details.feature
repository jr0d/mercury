Feature: View Inventory Computer Information
    As an authorized tenant
    I want to be able to see details of my inventory inventory_computers

    Background: Test GET /inventory/computers/<mercury_id>
        Given the account is an authorized tenant
        And the inventory_computers client URL is /inventory/computers

    # /inventory/computers/<mercury_id>
    @positive @p0 @smoke
    Scenario: Get Inventory Computer Details
        Given a inventory_computers entity id is located for testing
        When I get the entity using the inventory_computers api
        Then the inventory_computers response status is 200 OK
        And the inventory_computers response contains valid single entity details

    # /inventory/computers/<mercury_id> - bad id
    @negative @p0 @smoke
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
        | 123e4567-e89b-12d3-a456-42665544000 | 404| Not Found |

    # /inventory/computers/<mercury_id> - bad url
    @negative @p0 @smoke
    @nyi
    Scenario Outline: Get Inventory Computer Details With <bad_url>
        Given a inventory_computers <bad_url> is provided
        # TODO change the client url somehow (might need to use different feature file)
        Then the inventory_computers response status is <status_code> <reason>

        Examples: Invalid Mercury IDs
        | bad_url        | status_code          | reason    |
        | /inventory/typo   | 404                  | Not Found |
        # TODO etc

    # /inventory/computers/<mercury_id> - params
    @positive @p0
    Scenario Outline: Get Inventory Computer Details with parameters
        Given a inventory_computers entity id is located for testing
        When I get with parameters in <filename> the entity using the inventory_computers api
        Then the inventory_computers response status is 200 OK
        And the inventory_computers response contains valid single entity details
        And url parameters to the inventory_computers api are applied

        Examples: Fields
        | filename                    |
        | typical_detail_params.json  |
        # TODO more param files

    # TODO negative test for params
    # /inventory/computers/<mercury_id> - bad params
    @negative @p0 @smoke
    @nyi
    Scenario Outline: Get inventory Computer Details with bad parameters
        Given a inventory_computers entity id is located for testing
        When I get with parameters in <filename> the entity using the inventory_computers api
        # TODO expected behavior?
        Then the inventory_computers response status is 404 Not Found

        Examples: Fields
        | filename                          |
        | non_existant_params.json          |
        | invalid_details_param_values.json |
        # TODO

    # /inventory/computers/<mercury_id> - bad method
    @negative @p0 @smoke
    Scenario: Post instead of getting details of inventory_computers
        When I use post on inventory_computers
        Then the inventory_computers response status is 405 METHOD NOT ALLOWED

    # /inventory/computers/<mercury_id> - wrong headers
    @negative @p0 @smoke
    @nyi
    Scenario: Get inventory Computer Details with wrong headers
        Given a inventory_computers entity id is located for testing
        When I get with bad headers in <filename> the entity using the inventory_computers api
        # TODO expected behavior?
        Then the inventory_computers response status is 400 Bad Request

        Examples: Fields
        | filename                          |
        | bad_details_headers.json          |
        # TODO
