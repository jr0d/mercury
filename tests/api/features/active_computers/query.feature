Feature: Query Active Computers
    I want to be able to query active computers

    Background: Test POST /active/computers/query
      Given the account is an authorized tenant
      And the active_computers client URL is /active/computers

    @positive @p0 @smoke
    Scenario Outline: Query Active Computers With <field> <value>
        Given I have 'query' details for entities using the active_computers api
            """
            { <query> : { <field>: <value> }}
            """
        When I get the query_results from a query of active_computers
        Then the active_computers response status is 200 OK
        And the response contains a list of active_computers
        And the active_computers entities in the response contain <field> with <value>

        Examples: Fields
        | field                    | value     | query   |
        | 'active.rpc_port'        | 9003      | 'query' |
        | 'active.ping_port'       | 9004      | 'query' |
