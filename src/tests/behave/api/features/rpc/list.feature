Feature: List RPC Jobs
    As an authorized tenant
    I want to be able to see a list of my rpc jobs

    Background: Test GET /rpc/jobs
        Given the account is an authorized tenant
        And the rpc_jobs client URL is /rpc/jobs

    # /rpc/jobs
    @positive @p0 @smoke
    @MRC-63
    Scenario: Get list of rpc jobs
        When I get the list of rpc_jobs
        Then the rpc_jobs response status is 200 OK
        And the response contains a list of rpc_jobs

    # /rpc/jobs - bad method
    @negative @p0 @smoke
    @MRC-103
    Scenario Outline: List rpc jobs with bad HTTP method
        When I use post on rpc_jobs
        Then the rpc_jobs response status is 405 METHOD NOT ALLOWED

    # /rpc/jobs - bad url
    @negative @p0 @smoke
    @MRC-103
    Scenario Outline: List rpc jobs with a bad URL
        Given a rpc_jobs bad url <bad_url> is provided
        When I get the list of rpc_jobs
        Then the rpc_jobs response status is <status_code> <reason>

        Examples: Bad URLs
        | bad_url           | status_code          | reason    |
        | /rpc/typo         | 404                  | Not Found |

    # /rpc/jobs - ignored headers
    @positive @p0 @smoke
    @MRC-103
    Scenario Outline: List rpc jobs with bad headers
        When I get with bad headers in <filename> the list of rpc_jobs
        Then the rpc_jobs response status is 200 OK
        And the response contains a list of rpc_jobs

        Examples: Filename
        | filename         |
        | bad_headers.json |
