Feature: List Active Computers
    As an authorized tenant
    I want to be able to see a list of my active_computers

    Background: Test GET /active/computers
        Given the account is an authorized tenant
        And the active_computers client URL is /active/computers

    # /active/computers
    @positive @p0 @smoke
    Scenario: Get list of active_computers
        When I get the list of active_computers
        Then the active_computers response status is 200 OK
        And the response contains a list of active_computers

    # /active/computers - params
    @positive @p0
    Scenario Outline: Get list of active_computers with parameters
        When I get with parameters in <filename> the list of active_computers
        Then the active_computers response status is 200 OK
        And the response contains a list of active_computers
        And url parameters to the active_computers api are applied

        Examples: Fields
        | filename                  |
        | typical_list_params.json  |
        # TODO more param files
        # TODO | bad_params.json             |

    # TODO negative test for params

    # /active/computers - bad method
    @negative @p1
    Scenario: Post instead of getting list of active_computers
        When I use post on active_computers
        Then the active_computers response status is 405 METHOD NOT ALLOWED
