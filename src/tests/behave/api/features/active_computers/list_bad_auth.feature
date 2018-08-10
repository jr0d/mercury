Feature: List active computer negative tests
    As an unauthorized tenant
    I want to not be able to see a list of my active_computers

    Background: Test GET /active/computers unauthorized
        Given the account is an unauthorized tenant
        And the active_computers client URL is /active/computers

    # /active/computers - bad token
    # TODO add more bad token examples?
    @negative @p0 @smoke
    @not-local
    Scenario: Get list of active_computers for unauthorized account
        When I get the list of active_computers
        Then the active_computers response status is 401 X-AUTH-TOKEN HEADER NOT FOUND

    # /active/computers - no token
    @negative @p0 @smoke
    @not-local
    Scenario: Get list of active_computers for unauthorized account with no token
        Given the auth token for the active_computers client is nonexistent
        When I get the list of active_computers
        Then the active_computers response status is 401 X-AUTH-TOKEN HEADER NOT FOUND
