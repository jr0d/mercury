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

    # TODO negative testing

    # /rpc/jobs - bad method
    @negative @p0 @smoke
    @nyi
    Scenario Outline: List rpc jobs with bad HTTP method
        When I get the list of rpc_jobs

    # /rpc/jobs - bad url
    @negative @p0 @smoke
    @nyi
    Scenario Outline: List rpc jobs with a bad URL
        When I get the list of rpc_jobs

    # /rpc/jobs - wrong headers
    @negative @p0 @smoke
    @nyi
    Scenario Outline: List rpc jobs with bad headers
        When I get the list of rpc_jobs

    # /rpc/jobs - bad params
    @negative @p0 @smoke
    @nyi
    Scenario Outline: List rpc jobs with bad parameters
        When I get the list of rpc_jobs
