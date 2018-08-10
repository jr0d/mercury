Feature: View RPC Job Information
    As an authorized tenant
    I want to be able to see details of my rpc jobs

    Background: Test GET /rpc/jobs/<job_id>
        Given the account is an authorized tenant
        And the rpc_jobs client URL is /rpc/jobs
        And the rpc_tasks client URL is /rpc/task

    # /rpc/jobs/{job_id}
    @positive @p0 @smoke
    @not-local
    Scenario: Get RPC Job Details
        Given a rpc_jobs entity id is located for testing
        When I get the entity using the rpc_jobs api
        Then the rpc_jobs response status is 200 OK
        And the rpc_jobs response contains valid single entity details

    # /rpc/jobs/{job_id}/status
    @positive @p0 @smoke
    @not-local
    Scenario: Get RPC Job Status
        Given a rpc_jobs entity id is located for testing
        When I get the status of the entity using the rpc_jobs api
        Then the rpc_jobs response status is 200 OK
        And the rpc_jobs response contains valid single entity status details

    # /rpc/jobs/{job_id}/tasks
    @positive @p0 @smoke
    @not-local
    Scenario: Get RPC Job Tasks
        Given a rpc_jobs entity id is located for testing
        When I get the rpc_tasks tasks of the entity using the rpc_jobs api
        Then the rpc_tasks response status is 200 OK
        And the response contains a list of rpc_tasks

    # /rpc/task/{task_id}
    @positive @p0 @smoke
    @not-local
    Scenario: Get RPC Task Details
        Given a rpc_jobs entity id is located for testing
        When I get the rpc_tasks tasks of the entity using the rpc_jobs api
        And I get a task from the rpc_jobs entity using the rpc_tasks api
        Then the rpc_tasks response status is 200 OK
        And the rpc_tasks response contains valid single entity details

    # TODO
    # Bad method tests

    # /rpc/jobs/{job_id}
    @negative @p0 @smoke
    Scenario Outline: Get RPC Job Details With <invalid_job_id>
        Given a rpc_jobs <invalid_job_id> is provided
        When I get the entity using the rpc_jobs api
        Then the rpc_jobs response status is <status_code> <reason>

        Examples: Invalid Loadbalancer IDs
        | invalid_job_id            | status_code          | reason    |
        | invalid_job_id_123        | 404                  | Not Found |
        | 0                         | 404                  | Not Found |
        | 9999999999999999999       | 404                  | Not Found |
        | ""                        | 404                  | Not Found |
        | !@#$%^&*()_               | 404                  | Not Found |
        | None                      | 404                  | Not Found |
        | 123e4567-e89b-12d3-a456-42665544000 | 404        | Not Found |
