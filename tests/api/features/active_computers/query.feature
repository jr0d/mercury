Feature: Query Active Computers
    I want to be able to query active computers

    Background: Test POST /active/computers/query
      Given the account is an authorized tenant
      And the active_computers client URL is /active/computers

    # /active/computers/query
    @positive @p0 @smoke
    Scenario Outline: Query Active Computers
        Given I have query details in <filename> for entities using the active_computers api
        When I get the query_results from a query of active_computers
        Then the active_computers response status is 200 OK
        And the response contains a list of active_computers
        And the active_computers entities in the response contain the data from <filename>

        Examples: Fields
        | filename              |
        | active_rpc_port.json  |
        | active_ping_port.json |

    # /active/computers/query - params
    @positive @p0 @smoke
    Scenario Outline: Query Active Computers parameters
        Given I have query details in <query_filename> for entities using the active_computers api
        When I get with parameters in <param_filename> the query_results from a query of active_computers
        Then the active_computers response status is 200 OK
        And the response contains a list of active_computers
        And url parameters to the active_computers api are applied
        And the active_computers entities in the response contain the data from <filename>

        Examples: Fields
        | query_filename              | param_filename            |
        | active_rpc_port.json        | typical_query_params.json |
        | active_ping_port.json       | typical_query_params.json |

    # TODO negative testing
