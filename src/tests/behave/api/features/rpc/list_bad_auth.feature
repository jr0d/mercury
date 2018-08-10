Feature: List RPC Jobs negative tests
    As an unauthorized tenant
    I want to be able to see a list of my rpc jobs

    Background: Test GET /rpc/jobs
        Given the account is an unauthorized tenant
        And the rpc_jobs client URL is /rpc/jobs

    # /rpc/jobs - bad token
    @negative @p0 @smoke
    @not-local
    Scenario: Get list of rpc jobs
        When I get the list of rpc_jobs
        Then the rpc_jobs response status is 401 X-AUTH-TOKEN HEADER NOT FOUND

    # /rpc/jobs - no token
    @negative @p0 @smoke
    @not-local
    Scenario: Get list of rpc jobs
        Given the auth token for the rpc_jobs client is nonexistent
        When I get the list of rpc_jobs
        Then the rpc_jobs response status is 401 X-AUTH-TOKEN HEADER NOT FOUND
