Feature: Inject Misc Capability RPC Jobs
    As an authorized tenant
    I want to be able to inject new rpc jobs for each of the misc capabilities

    Background: Test POST /rpc/jobs (misc capabilities)
        Given the account is an authorized tenant
        And the rpc_jobs client URL is /rpc/jobs
        And the rpc_tasks client URL is /rpc/task
        And the inventory_computers client URL is /inventory/computers


    # /rpc/jobs run command
    @positive @p0 @smoke
    @MRC-113
    @not-local
    Scenario Outline: Inject rpc run capability
        Given a inventory_computers entity id is located for testing
        And I have job injection details for a specific inventory_computers device in <filename> for creating jobs using the rpc_jobs api
        When I get the injection results from a post to rpc_jobs
        Then the rpc_jobs response status is 200 OK
        Then the response contains a rpc_jobs job_id
        And the corresponding rpc_jobs job is completed with successful rpc_tasks tasks
        And the rpc_jobs response status is 200 OK
        And the first rpc_tasks task for the inventory_computers device has the stdout output contained in <out_filename>

        Examples: Filenames
        | filename      | out_filename     |
        | run_pwd.json  | run_pwd_out.json |
        | run_ip.json   | run_ip_out.json  |

    # /rpc/jobs run_async command
    @positive @p0 @smoke
    @MRC-124
    @not-local
    Scenario Outline: Inject rpc run_async capability
        Given a inventory_computers entity id is located for testing
        And I have job injection details for a specific inventory_computers device in <filename> for creating jobs using the rpc_jobs api
        When I get the injection results from a post to rpc_jobs
        Then the rpc_jobs response status is 200 OK
        Then the response contains a rpc_jobs job_id
        And the corresponding rpc_jobs job is completed with successful rpc_tasks tasks
        And the rpc_jobs response status is 200 OK
        And the first rpc_tasks task for the inventory_computers device has the stdout output contained in <out_filename>

        Examples: Filenames
        | filename      | out_filename     |
        | run_async_pwd.json  | run_async_out.json |
        | run_async_ip.json   | run_async_out.json  |

    # /rpc/jobs inspector RPC capability
    @positive @p0 @smoke
    @MRC-127
    @not-local
    Scenario Outline: Inject rpc inspector capability
        Given a inventory_computers entity id is located for testing
        And I have job injection details for a specific inventory_computers device in <filename> for creating jobs using the rpc_jobs api
        When I get the injection results from a post to rpc_jobs
        Then the rpc_jobs response status is 200 OK
        Then the response contains a rpc_jobs job_id
        And the corresponding rpc_jobs job is completed with successful rpc_tasks tasks
        And the rpc_jobs response status is 200 OK
        And the first rpc_tasks task for the inventory_computers device has the message output contained in <out_filename>

        Examples: Filenames
        | filename                   | out_filename       |
        | inspector_capability.json  | inspector_out.json |
