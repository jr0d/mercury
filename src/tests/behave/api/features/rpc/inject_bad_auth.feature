Feature: Inject RPC Jobs negative tests
    As an unauthorized tenant
    I want to not be able to inject new rpc jobs to run

    Background: Test POST /rpc/jobs
        Given the account is an unauthorized tenant
        And the rpc_jobs client URL is /rpc/jobs

    # /rpc/jobs - bad token
    @negative @p0 @smoke
    @not-local
    Scenario Outline: Inject rpc jobs
        # Filename should have a query dict and an instruction dict
        Given I have job injection details in <filename> for creating jobs using the rpc_jobs api
        When I get the injection results from a post to rpc_jobs
        Then the rpc_jobs response status is 401 X-AUTH-TOKEN HEADER NOT FOUND

        Examples: Filenames
        | filename           |
        | echo_job.json      |
        | inspector_job.json |

    # /rpc/jobs - no token
    @negative @p0 @smoke
    @not-local
    Scenario Outline: Inject rpc jobs
        # Filename should have a query dict and an insruction dict
        Given the auth token for the rpc_jobs client is nonexistent
        And I have job injection details in <filename> for creating jobs using the rpc_jobs api
        When I get the injection results from a post to rpc_jobs
        Then the rpc_jobs response status is 401 X-AUTH-TOKEN HEADER NOT FOUND

        Examples: Filenames
        | filename           |
        | echo_job.json      |
        | inspector_job.json |
