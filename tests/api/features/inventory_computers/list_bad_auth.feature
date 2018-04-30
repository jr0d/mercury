Feature: List inventory computer negative tests
    As an unauthorized tenant
    I want to not be able to see a list of my inventory_computers

    Background: Test GET /inventory/computers unauthorized
        Given the account is an unauthorized tenant
        And the inventory_computers client URL is /inventory/computers

    # /inventory/computers - bad token
    # TODO add more bad token examples?
    @negative @p1
    Scenario: Get list of inventory_computers for unauthorized account
        When I get the list of inventory_computers
        Then the inventory_computers response status is 401 X-AUTH-TOKEN HEADER NOT FOUND

    # /inventory/computers - no token
    @negative @p1
    Scenario: Get list of inventory_computers for unauthorized account with no token
        Given the auth token for the inventory_computers client is nonexistent
        When I get the list of inventory_computers
        Then the inventory_computers response status is 401 X-AUTH-TOKEN HEADER NOT FOUND
    
