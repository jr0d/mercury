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

    # /inventory/computer - offset_id
    @positive @p0 @smoke @offset @not-local
    Scenario Outline: Get list of inventory_computers and test the offset_id param
        When I get with parameters in <filename> the list of inventory_computers
        Then I get with offset parameters in <second_few> the list of inventory_computers
        Then the inventory_computers response status is 200 OK
        And the response contains an offset list of inventory_computers that have been offset by the offset_id

        Examples: Fields
        | filename        | second_few     |
        | first_ten.json  | next_five.json |

    # TODO negative test for params

    # /inventory/computers - bad method
    @negative @p0 @smoke
    Scenario: Post instead of getting list of inventory_computers
        When I use post on inventory_computers
        Then the inventory_computers response status is 405 METHOD NOT ALLOWED
