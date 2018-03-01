Feature: Query Active Computers
    I want to be able to query active computers

    Background: Test POST /active/computers/query
      Given the account is an authorized tenant
      And the mercury_computers client URL is /active/computers

    @positive @p0 @smoke
    Scenario Outline: Query Active Comuters With <field>
        Given I have 'query' details for entities using the mercury_computers api
            """
            { <query> : { <field>: <value> }}
            """
        When I get the query_results from a query of mercury_computers
        Then the mercury_computers response status is 200 OK
        And the response contains a list of mercury_computers on my account

        Examples: Fields
        | field            | value   | query   |
        | 'dmi.sys_vendor' | 'HP'    | 'query' |
