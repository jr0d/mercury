Feature: Query Active Computers negative tests
    As an unauthorized tenant
    I want to not be able to query active computers

    Background: Test POST /active/computers/query
      Given the account is an unauthorized tenant
      And the active_computers client URL is /active/computers

    @negative @p0 @smoke @not-local
    Scenario Outline: Query Active Computers
        Given I have query details in <filename> for entities using the active_computers api
        When I get the query_results from a query of active_computers
        Then the active_computers response status is 401 X-AUTH-TOKEN HEADER NOT FOUND

        Examples: Fields
        | filename              |
        | active_rpc_port.json  |
        | active_ping_port.json |


    # TODO negative testing
