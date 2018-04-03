Feature: List RPC Jobs
    As an authorized tenant
    I want to be able to see a list of my rpc jobs

    Background: Test GET /rpc/jobs
        Given the account is an authorized tenant
        And the rpc_jobs client URL is /rpc/jobs

    # /rpc/jobs
    @positive @p0 @smoke
    Scenario: Get list of rpc jobs
        When I get the list of rpc_jobs
        Then the rpc_jobs response status is 200 OK
        And the response contains a list of rpc_jobs

    # TODO make the test work with bad auth
    @negative @p1 @not-tested
    Scenario: Get list of inventory_computers for unauthorized account
        Given the account is an unauthorized tenant
        And the inventory_computers client URL is /inventory/computers
        When I get the list of inventory_computers
        Then the inventory_computers response status is 401 UNAUTHORIZED
        And the inventory_computers response contains an error message of
            """
            UNAUTHORIZED
            """
