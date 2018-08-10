Feature: View RPC Job Information negative tests
    As an unauthorized tenant
    I want to not be able to see details of my rpc jobs

    Background: Test GET /rpc/jobs/<job_id>
        Given the account is an unauthorized tenant
        And the rpc_jobs client URL is /rpc/jobs
        And the rpc_tasks client URL is /rpc/task

    # /rpc/jobs/{job_id} - bad token
    @negative @p0 @smoke
    @not-local
    Scenario: Get RPC Job Details for unauthorized account
        Given a rpc_jobs test entity id is defined for testing
        When I get the entity using the rpc_jobs api
        Then the rpc_jobs response status is 401 X-AUTH-TOKEN HEADER NOT FOUND

    # /rpc/jobs/{job_id} - no token
    @negative @p0 @smoke
    @not-local
    Scenario: Get RPC Job Details for unauthorized account
        Given the auth token for the rpc_jobs client is nonexistent
        And a rpc_jobs test entity id is defined for testing
        When I get the entity using the rpc_jobs api
        Then the rpc_jobs response status is 401 X-AUTH-TOKEN HEADER NOT FOUND

    # /rpc/jobs/{job_id}/status - bad token
    @negative @p0 @smoke
    @not-local
    Scenario: Get RPC Job Status
        Given a rpc_jobs entity id is defined for testing
        When I get the status of the entity using the rpc_jobs api
        Then the rpc_jobs response status is 401 X-AUTH-TOKEN HEADER NOT FOUND

    # /rpc/jobs/{job_id}/status - no token
    @negative @p0 @smoke
    @not-local
    Scenario: Get RPC Job Status
        Given the auth token for the rpc_jobs client is nonexistent
        And a rpc_jobs entity id is defined for testing
        When I get the status of the entity using the rpc_jobs api
        Then the rpc_jobs response status is 401 X-AUTH-TOKEN HEADER NOT FOUND

    # /rpc/jobs/{job_id}/tasks - bad token
    @negative @p0 @smoke
    @not-local
    Scenario: Get RPC Job Tasks
        Given a rpc_jobs entity id is defined for testing
        When I get the rpc_tasks tasks of the entity using the rpc_jobs api
        Then the rpc_tasks response status is 401 X-AUTH-TOKEN HEADER NOT FOUND

    # /rpc/jobs/{job_id}/tasks - no token
    @negative @p0 @smoke
    @not-local
    Scenario: Get RPC Job Tasks
        Given the auth token for the rpc_jobs client is nonexistent
        And a rpc_jobs entity id is defined for testing
        When I get the rpc_tasks tasks of the entity using the rpc_jobs api
        Then the rpc_tasks response status is 401 X-AUTH-TOKEN HEADER NOT FOUND
