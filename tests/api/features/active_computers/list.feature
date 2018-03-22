Feature: List Active Computers
    As an authorized tenant
    I want to be able to see a list of my active_computers

    Background: Test GET /active/computers
        Given the account is an authorized tenant
        And the active_computers client URL is /active/computers

    @positive @p0 @smoke
    Scenario: Get list of active_computers
        When I get the list of active_computers
        Then the active_computers response status is 200 OK
        And the response contains a list of active_computers

    @negative @p1 @not-tested
    Scenario: Get list of active_computers for unauthorized account
        Given the account is an unauthorized tenant
        And the active_computers client URL is /active/computers
        When I get the list of active_computers
        Then the active_computers response status is 401 UNAUTHORIZED
        And the active_computers response contains an error message of
            """
            UNAUTHORIZED
            """
