Feature: List inventory Computers
    As an authorized tenant
    I want to be able to see a list of my inventory_computers

    Background: Test GET /inventory/computers
        Given the account is an authorized tenant
        And the inventory_computers client URL is /inventory/computers

    @positive @p0 @smoke
    Scenario: Get list of inventory_computers
        When I get the list of inventory_computers
        Then the inventory_computers response status is 200 OK
        And the response contains a list of inventory_computers
