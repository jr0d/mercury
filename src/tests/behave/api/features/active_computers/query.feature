Feature: Query Active Computers
    I want to be able to query active computers

    Background: Test POST /active/computers/query
      Given the account is an authorized tenant
      And the active_computers client URL is /active/computers

    # /active/computers/query
    @positive @p0 @smoke
    @MRC-56
    Scenario Outline: Query Active Computers
        Given I have query details in <filename> for entities using the active_computers api
        When I get the query_results from a query of active_computers
        Then the active_computers response status is 200 OK
        And the response contains a list of active_computers
        And the active_computers entities in the response contain the data from <filename>

        Examples: Filename
        | filename              |
        | active_rpc_port.json  |
        | active_ping_port.json |

    # /active/computers/query - params
    @positive @p0
    @MRC-70
    Scenario Outline: Query Active Computers parameters
        Given I have query details in <query_filename> for entities using the active_computers api
        When I get with parameters in <param_filename> the query_results from a query of active_computers
        Then the active_computers response status is 200 OK
        And the response contains a list of active_computers
        And url parameters to the active_computers api are applied
        And the active_computers entities in the response contain the data from <filename>

        Examples: Filenames
        | query_filename              | param_filename            |
        | active_rpc_port.json        | typical_query_params.json |
        | active_ping_port.json       | typical_query_params.json |

    # /active/computers/query - offset_id
    @positive @p0
    @quarantined @MRC-118
    @MRC-70
    @offset @not-local
    Scenario Outline: Query Active Computers parameters and test the offset_id param
        Given I have query details in <query_filename> for entities using the active_computers api
        When I get with parameters in <param_filename> the query_results from a query of active_computers
        Then I get with offset parameters in <second_few> the query_results from a query of active_computers
        Then the active_computers response status is 200 OK
        And the response contains an offset list of active_computers that have been offset by the offset_id
        And the active_computers entities in the response contain the data from <filename>

        Examples: Filenames
        | query_filename              | param_filename | second_few     |
        | active_rpc_port.json        | first_ten.json | next_five.json |
        | active_ping_port.json       | first_ten.json | next_five.json |


    # /active/computers/query - bad method
    @negative @p0 @smoke
    @MRC-103
    Scenario Outline: Query Active Computers with bad HTTP method
        Given I have query details in <query_filename> for entities using the active_computers api
        When I query with get for active_computers
        Then the active_computers response status is 405 METHOD NOT ALLOWED

        Examples: Filename
        | query_filename        |
        | active_rpc_port.json  |
        | active_ping_port.json |

    # /active/computers/query - bad url
    @negative @p0 @smoke
    @MRC-103
    Scenario Outline: Query Active Computers with a bad URL
        Given I have query details in <query_filename> for entities using the active_computers api
        Given a active_computers bad url <bad_url> is provided
        When I get the query_results from a query of active_computers
        Then the active_computers response status is 404 Not Found

        Examples: Filename and Bad URLs
        | query_filename        | bad_url               |
        | active_rpc_port.json  | /active/typo/query    |
        | active_rpc_port.json  | /active/computer/typo |
        | active_ping_port.json | /active/typo/query    |
        | active_ping_port.json | /active/computer/typo |

    # /active/computers/query - wrong headers
    @negative @p0 @smoke
    @quarantined @MRC-115
    @MRC-103
    Scenario Outline: Query Active Computers with bad headers
        Given I have query details in <query_filename> for entities using the active_computers api
        When I get with bad headers in <filename> the query_results from a query of active_computers
        Then the active_computers response status is <status_code> <reason>

        Examples: Filenames
        | query_filename        | filename         | status_code | reason                |
        | active_rpc_port.json  | bad_headers.json | 500         | Internal Server Error |
        | active_ping_port.json | bad_headers.json | 500         | Internal Server Error |

    # /active/computers/query - extra headers
    @positive @p0 @smoke
    @MRC-103
    Scenario Outline: Query Active Computers with extra headers
        Given I have query details in <query_filename> for entities using the active_computers api
        When I get with bad headers in <filename> the query_results from a query of active_computers
        Then the active_computers response status is <status_code> <reason>
        And the response contains a list of active_computers
        And the active_computers entities in the response contain the data from <filename>

        Examples: Filenames
        | query_filename        | filename           | status_code | reason |
        | active_rpc_port.json  | extra_headers.json | 200         | OK     |
        | active_ping_port.json | extra_headers.json | 200         | OK     |

    # /active/computers/query - invalid params
    @positive @p0 @smoke
    @MRC-103
    Scenario Outline: Query Active Computers with bad parameters
        Given I have query details in <filename> for entities using the active_computers api
        When I get with parameters in <param_filename> the query_results from a query of active_computers
        Then the active_computers response status is 200 OK
        And the response contains a list of active_computers
        And the valid url parameters to the active_computers api are applied
        And the active_computers entities in the response contain the data from <filename>

        Examples: Filenames
        | filename              | param_filename                  |
        | active_rpc_port.json  | invalid_query_param_values.json |
        | active_ping_port.json | invalid_query_param_values.json |
