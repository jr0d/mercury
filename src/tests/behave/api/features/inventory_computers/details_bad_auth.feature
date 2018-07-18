Feature: View inventory computer negative tests
    As an unauthorized tenant
    I want to not be able to see details of my inventory_computers

    Background: Test GET /inventory/computers/<mercury_id> unauthorized
        Given the account is an unauthorized tenant
        And the inventory_computers client URL is /inventory/computers

    # /inventory/computers/<mercury_id> - bad token
    # TODO add more bad token examples?
    @negative @p0 @smoke @not-local
    Scenario: Get Inventory Computer Details for unauthorized account
        Given a inventory_computers test entity id is defined for testing
        When I get the entity using the inventory_computers api
        Then the inventory_computers response status is 401 X-AUTH-TOKEN HEADER NOT FOUND

    # /inventory/computers/<mercury_id> - no token
    @negative @p0 @smoke @not-local
    Scenario: Get Inventory Computer Details for unauthorized account with no token
        Given the auth token for the inventory_computers client is nonexistent
        And a inventory_computers test entity id is defined for testing
        When I get the entity using the inventory_computers api
        Then the inventory_computers response status is 401 X-AUTH-TOKEN HEADER NOT FOUND
