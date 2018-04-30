Feature: Query Inventory Computers negative tests
    As an unauthorized tenant
    I want to not be able to query inventory computers

    Background: Test POST /inventory/computers/query
      Given the account is an unauthorized tenant
      And the inventory_computers client URL is /inventory/computers

    @negative @p0 @smoke
    Scenario Outline: Query Inventory Computers
        Given I have query details in <filename> for entities using the inventory_computers api
        When I get the query_results from a query of inventory_computers
        Then the inventory_computers response status is 401 X-AUTH-TOKEN HEADER NOT FOUND

        Examples: Fields
        | filename              |
        | active_rpc_port.json  |
        | active_ping_port.json |


    # TODO negative testing
