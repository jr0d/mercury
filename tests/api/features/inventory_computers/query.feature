Feature: Query inventory Computers
    I want to be able to query inventory computers

    Background: Test POST /inventory/computers/query
      Given the account is an authorized tenant
      And the inventory_computers client URL is /inventory/computers

    @positive @p0 @smoke
    Scenario Outline: Query inventory Computers With <field> <value>
        Given I have 'query' details for entities using the inventory_computers api
            """
            { <query> : { <field>: <value> }}
            """
        When I get the query_results from a query of inventory_computers
        Then the inventory_computers response status is 200 OK
        And the response contains a list of inventory_computers
        And the inventory_computers entities in the response contain <field> with <value>

        Examples: Fields
        | field            | value         | query   |
        | 'dmi.sys_vendor' | 'HP'          | 'query' |
        | 'mem.Dirty'      | 0             | 'query' |
