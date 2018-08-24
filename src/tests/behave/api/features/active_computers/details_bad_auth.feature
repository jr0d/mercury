Feature: View active computer negative tests
    As an unauthorized tenant
    I want to not be able to see details of my active_computers

    Background: Test GET /active/computers/<mercury_id> unauthorized
        Given the account is an unauthorized tenant
        And the active_computers client URL is /active/computers

    # /active/computers/<mercury_id> - bad token
    @negative @p0 @smoke
    @not-local
    Scenario: Get Active Computer Details for unauthorized account
        Given a active_computers test entity id is defined for testing
        When I get the entity using the active_computers api
        Then the active_computers response status is 401 X-AUTH-TOKEN HEADER NOT FOUND

    # /active/computers/<mercury_id> - no token
    @negative @p0 @smoke
    @not-local
    Scenario: Get Active Computer Details for unauthorized account with no token
        Given the auth token for the active_computers client is nonexistent
        And a active_computers test entity id is defined for testing
        When I get the entity using the active_computers api
        Then the active_computers response status is 401 X-AUTH-TOKEN HEADER NOT FOUND
