Feature: List Active Computers
    As an authorized tenant
    I want to be able to see a list of my mercury_computers

    Background: Test GET /active/computers
        Given the account is an authorized tenant
        And the mercury_computers client URL is /active/computers

    @positive @p0 @smoke
    Scenario: Get list of mercury_computers
        When I get the list of mercury_computers
        Then the mercury_computers response status is 200 OK
        And the response contains a list of mercury_computers on my account

    @negative @p1 @not-tested
    Scenario: Get list of mercury_computers for unauthorized account
        Given the account is an unauthorized tenant
        And the mercury_computers client URL is /active/computers
        When I get the list of mercury_computers
        Then the mercury_computers response status is 401 UNAUTHORIZED
        And the mercury_computers response contains an error message of
            """
            UNAUTHORIZED
            """
