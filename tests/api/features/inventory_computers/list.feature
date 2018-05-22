Feature: List inventory Computers
    As an authorized tenant
    I want to be able to see a list of my inventory_computers

    Background: Test GET /inventory/computers
        Given the account is an authorized tenant
        And the inventory_computers client URL is /inventory/computers

    # /inventory/computers
    @positive @p0 @smoke
    Scenario: Get list of inventory_computers
        When I get the list of inventory_computers
        Then the inventory_computers response status is 200 OK
        And the response contains a list of inventory_computers

    # /inventory/computers - params
    @positive @p0 @smoke
    Scenario Outline: Get list of inventory_computers with parameters
        When I get with parameters in <filename> the list of inventory_computers
        Then the inventory_computers response status is 200 OK
        And the response contains a list of inventory_computers
        And url parameters to the inventory_computers api are applied

        Examples: Fields
        | filename                  |
        | typical_list_params.json  |
        # TODO more param files
        # TODO | bad_params.json             |

    # TODO negative test for params

    # /inventory/computers - bad method
    @negative @p1
    Scenario: Post instead of getting list of inventory_computers
        When I use post on inventory_computers
        Then the inventory_computers response status is 405 METHOD NOT ALLOWED
