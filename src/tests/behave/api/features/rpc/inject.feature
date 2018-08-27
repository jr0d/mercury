Feature: Inject RPC Jobs
    As an authorized tenant
    I want to be able to inject new rpc jobs to run

    Background: Test POST /rpc/jobs
        Given the account is an authorized tenant
        And the rpc_jobs client URL is /rpc/jobs

    # /rpc/jobs
    @positive @p0 @smoke
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

    # TODO negative testing

    # /rpc/jobs - bad method
    @negative @p0 @smoke
    @nyi
    Scenario Outline: Inject rpc jobs with bad HTTP method
        Given I have job injection details in <filename> for creating jobs using the rpc_jobs api

        Examples: Filenames
        | filename           |
        | echo_job.json      |
        | inspector_job.json |

    # /rpc/jobs - bad url
    @negative @p0 @smoke
    @nyi
    Scenario Outline: Inject rpc jobs with a bad URL
        Given I have job injection details in <filename> for creating jobs using the rpc_jobs api

        Examples: Filenames
        | filename           |
        | echo_job.json      |
        | inspector_job.json |

    # /rpc/jobs - wrong headers
    @negative @p0 @smoke
    @nyi
    Scenario Outline: Inject rpc jobs with bad headers
        Given I have job injection details in <filename> for creating jobs using the rpc_jobs api

        Examples: Filenames
        | filename           |
        | echo_job.json      |
        | inspector_job.json |

    # /rpc/jobs - bad params
    @negative @p0 @smoke
    @nyi
    Scenario Outline: Inject rpc jobs with bad parameters
        Given I have job injection details in <filename> for creating jobs using the rpc_jobs api

        Examples: Filenames
        | filename           |
        | echo_job.json      |
        | inspector_job.json |
