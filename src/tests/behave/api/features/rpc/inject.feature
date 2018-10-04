Feature: Inject RPC Jobs
    As an authorized tenant
    I want to be able to inject new rpc jobs to run

    Background: Test POST /rpc/jobs
        Given the account is an authorized tenant
        And the rpc_jobs client URL is /rpc/jobs

    # /rpc/jobs
    @positive @p0 @smoke
    @MRC-63
    @not-local
    Scenario Outline: Inject rpc jobs
        # Filename should have a query dict and an instruction dict
        Given I have job injection details in <filename> for creating jobs using the rpc_jobs api
        When I get the injection results from a post to rpc_jobs
        Then the rpc_jobs response status is 200 OK
        Then the response contains a rpc_jobs job_id
        And the corresponding rpc_jobs job is completed with successful tasks
        And the rpc_jobs response status is 200 OK

        Examples: Filenames
        | filename           |
        | echo_job.json      |
        | inspector_job.json |

    # /rpc/jobs - bad method
    @negative @p0 @smoke
    @MRC-103
    Scenario Outline: Inject rpc jobs with bad HTTP method
        Given I have job injection details in <filename> for creating jobs using the rpc_jobs api
        When I inject with delete for rpc_jobs
        Then the rpc_jobs response status is 405 METHOD NOT ALLOWED

        Examples: Filenames
        | filename           |
        | echo_job.json      |
        | inspector_job.json |

    # /rpc/jobs - bad url
    @negative @p0 @smoke
    @MRC-103
    Scenario Outline: Inject rpc jobs with a bad URL
        Given I have job injection details in <filename> for creating jobs using the rpc_jobs api
        Given a rpc_jobs bad url <bad_url> is provided
        When I get the injection results from a post to rpc_jobs
        Then the rpc_jobs response status is <status_code> <reason>

        Examples: Bad URLs and Filename
        | filename           | bad_url     | status_code | reason    |
        | echo_job.json      | /rpc/typos  | 404         | Not Found |
        | inspector_job.json | /typos/jobs | 404         | Not Found |

    # /rpc/jobs - ignored headers
    @positive @p0 @smoke
    @MRC-103
    @not-local
    Scenario Outline: Inject rpc jobs with ignored headers
        Given I have job injection details in <filename> for creating jobs using the rpc_jobs api
        When I get with bad headers in <bad_header_filename> the injection results from a post to rpc_jobs
        Then the rpc_jobs response status is 200 OK
        Then the response contains a rpc_jobs job_id
        And the corresponding rpc_jobs job is completed with successful tasks
        And the rpc_jobs response status is 200 OK

        Examples: Filenames
        | filename           | bad_header_filename |
        | echo_job.json      | extra_headers.json  |
        | inspector_job.json | extra_headers.json  |

    # /rpc/jobs - bad headers
    @negative @p0 @smoke
    @quarantined @MRC-115
    @MRC-103
    Scenario Outline: Inject rpc jobs with bad headers
        Given I have job injection details in <filename> for creating jobs using the rpc_jobs api
        When I get with bad headers in <bad_header_filename> the injection results from a post to rpc_jobs
        Then the rpc_jobs response status is 500 Internal Server Error

        Examples: Filenames
        | filename           | bad_header_filename |
        | echo_job.json      | bad_headers.json    |
        | inspector_job.json | bad_headers.json    |
