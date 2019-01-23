Feature: Inject HP Firmware Capability RPC Jobs
    As an authorized tenant
    I want to be able to inject new rpc jobs for each of the hp firmware capabilities

    Background: Test POST /rpc/jobs (hp firmware capabilities)
        Given the account is an authorized tenant
        And the rpc_jobs client URL is /rpc/jobs
        And the rpc_tasks client URL is /rpc/task
        And the inventory_computers client URL is /inventory/computers
        And the active_computers client URL is /active/computers


    # /rpc/jobs hp_update_firmware - no url
    @negative @p0 @smoke
    @quarantined @MRC-131
    @MRC-130
    @not-local
    Scenario Outline: Inject rpc hp_update_firmware capability with no url
        Given first device queried from <query_filename> of type active_computers entity id is located for testing
        And I have job injection details for a specific active_computers device in <job_filename> for creating jobs using the rpc_jobs api
        When I get the injection results from a post to rpc_jobs
        Then the rpc_jobs response status is 200 OK
        Then the response contains a rpc_jobs job_id
        And the corresponding rpc_jobs job is completed with ERROR state rpc_tasks tasks
        And the rpc_jobs response status is 200 OK

        Examples: Filenames
        | query_filename | job_filename                         |
        | hp_query.json  | hp_firmware_update_job_null_url.json |


    # /rpc/jobs hp_update_firmware - bad url
    @negative @p0 @smoke
    @MRC-130
    @not-local
    Scenario Outline: Inject rpc hp_update_firmware capability with a bad url
      Given first device queried from <query_filename> of type active_computers entity id is located for testing
      And I have job injection details for a specific active_computers device in <job_filename> for creating jobs using the rpc_jobs api
      When I get the injection results from a post to rpc_jobs
      Then the rpc_jobs response status is 200 OK
      Then the response contains a rpc_jobs job_id
      And the corresponding rpc_jobs job is completed with ERROR state rpc_taks tasks
      And the rpc_jobs response status is 200 OK

      Examples: Filenames
      | query_filename | job_filename                        |
      | hp_query.json  | hp_firmware_update_job_bad_url.json |
