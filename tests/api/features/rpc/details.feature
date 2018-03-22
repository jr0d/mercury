Feature: View RPC Job Information
    As an authorized tenant
    I want to be able to see details of my rpc jobs

    Background: Test GET /rpc/jobs/<job_id>
        Given the account is an authorized tenant
        And the rpc_jobs client URL is /rpc/jobs

    @positive @p0 @smoke
    Scenario: Get RPC Job Details
        Given a rpc_jobs entity id is located for testing
        When I get the entity using the rpc_jobs api
        Then the rpc_jobs response status is 200 OK
        And the rpc_jobs response contains valid single entity details

    @negative @p1
    Scenario Outline: Get RPC Job Details With <invalid_job_id>
        Given a rpc_jobs <invalid_job_id> is provided
        When I get the entity using the rpc_jobs api
        Then the rpc_jobs response status is <status_code> <reason>

        Examples: Invalid Loadbalancer IDs
        | invalid_job_id            | status_code          | reason    |
        | invalid_job_id_123        | 404                  | NOT FOUND |
        | 0                         | 404                  | NOT FOUND |
        | 9999999999999999999       | 404                  | NOT FOUND |
        | ""                        | 404                  | NOT FOUND |
        | !@#$%^&*()_               | 404                  | NOT FOUND |
        | None                      | 404                  | NOT FOUND |
        | 123e4567-e89b-12d3-a456-42665544000 | 404        | NOT FOUND |
