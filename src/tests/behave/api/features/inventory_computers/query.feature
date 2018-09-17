Feature: Query inventory Computers
    I want to be able to query inventory computers

    Background: Test POST /inventory/computers/query
      Given the account is an authorized tenant
      And the inventory_computers client URL is /inventory/computers

    # /inventory/computers/query
    @positive @p0 @smoke
    @MRC-57
    Scenario Outline: Query inventory Computers
        Given I have query details in <filename> for entities using the inventory_computers api
        When I get the query_results from a query of inventory_computers
        Then the inventory_computers response status is 200 OK
        And the response contains a list of inventory_computers
        And the inventory_computers entities in the response contain the data from <filename>

        Examples: Filenames
        | filename              |
        | active_rpc_port.json  |
        | active_ping_port.json |

    # /inventory/computers/query - not local
    @positive @p0 @smoke
    @MRC-57
    @not-local
    Scenario Outline: Query inventory Computers not local
        Given I have query details in <filename> for entities using the inventory_computers api
        When I get the query_results from a query of inventory_computers
        Then the inventory_computers response status is 200 OK
        And the response contains a list of inventory_computers
        And the inventory_computers entities in the response contain the data from <filename>

        Examples: Filenames
        | filename              |
        | dmi_sys_vendor.json   |
        | mem_Dirty.json        |

    # /inventory/computers/query - params
    @positive @p0
    @MRC-70
    Scenario Outline: Query Inventory Computers parameters
        Given I have query details in <query_filename> for entities using the inventory_computers api
        When I get with parameters in <param_filename> the query_results from a query of inventory_computers
        Then the inventory_computers response status is 200 OK
        And the response contains a list of inventory_computers
        And url parameters to the inventory_computers api are applied
        And the inventory_computers entities in the response contain the data from <filename>

        Examples: Fields
        | query_filename              | param_filename            |
        | active_rpc_port.json        | typical_query_params.json |
        | active_ping_port.json       | typical_query_params.json |

    # /inventory/computers/query - params - not local
    @positive @p0
    @MRC-70
    @not-local
    Scenario Outline: Query Inventory Computers parameters not local
        Given I have query details in <query_filename> for entities using the inventory_computers api
        When I get with parameters in <param_filename> the query_results from a query of inventory_computers
        Then the inventory_computers response status is 200 OK
        And the response contains a list of inventory_computers
        And url parameters to the inventory_computers api are applied
        And the inventory_computers entities in the response contain the data from <filename>

        Examples: Fields
        | query_filename              | param_filename            |
        | dmi_sys_vendor.json         | typical_query_params.json |
        | mem_Dirty.json              | typical_query_params.json |

    # /inventory/computers/query - offset_id
    @positive @p0
    @MRC-70
    @offset @not-local
    Scenario Outline: Query Inventory Computers parameters and test the offset_id param
        Given I have query details in <query_filename> for entities using the inventory_computers api
        When I get with parameters in <param_filename> the query_results from a query of inventory_computers
        Then I get with offset parameters in <second_few> the query_results from a query of inventory_computers
        Then the inventory_computers response status is 200 OK
        And the response contains an offset list of inventory_computers that have been offset by the offset_id
        And the inventory_computers entities in the response contain the data from <filename>

        Examples: Fields
        | query_filename              | param_filename | second_few |
        | active_rpc_port.json        | first_ten.json | next_five.json |
        | active_ping_port.json       | first_ten.json | next_five.json |


    # /inventory/computers/query - bad method
    @negative @p0 @smoke
    @quarantined @MRC-110
    @MRC-103
    Scenario Outline: Query Inventory Computers with bad HTTP method
        Given I have query details in <query_filename> for entities using the inventory_computers api
        When I query with get for inventory_computers
        Then the inventory_computers response status is 405 METHOD NOT ALLOWED

        Examples: Fields
        | query_filename        |
        | active_rpc_port.json  |
        | active_ping_port.json |

    # /inventory/computers/query - bad url
    @negative @p0 @smoke
    @MRC-103
    Scenario Outline: Query Inventory Computers with a bad URL
        Given I have query details in <query_filename> for entities using the inventory_computers api
        Given a inventory_computers bad url <bad_url> is provided
        When I get the query_results from a query of inventory_computers
        Then the inventory_computers response status is 404 Not Found

        Examples: Fields
        | query_filename        | bad_url               |
        | active_rpc_port.json  | /inventory/typo/query    |
        | active_rpc_port.json  | /inventory/computer/typo |
        | active_ping_port.json | /inventory/typo/query    |
        | active_ping_port.json | /inventory/computer/typo |

    # /inventory/computers/query - wrong headers
    @negative @p0 @smoke
    @MRC-103
    Scenario Outline: Query Inventory Computers with bad headers
        Given I have query details in <query_filename> for entities using the inventory_computers api
        When I get with bad headers in <filename> the query_results from a query of inventory_computers
        Then the inventory_computers response status is <status_code> <reason>

        Examples: Fields
        | query_filename        | filename         | status_code | reason |
        | active_rpc_port.json  | bad_headers.json | 500 | Internal Server Error |
        | active_ping_port.json | bad_headers.json | 500 | Internal Server Error |

    # /inventory/computers/query - extra headers
    @positive @p0 @smoke
    @MRC-103
    Scenario Outline: Query Active Computers with extra headers
        Given I have query details in <query_filename> for entities using the inventory_computers api
        When I get with bad headers in <filename> the query_results from a query of inventory_computers
        Then the inventory_computers response status is <status_code> <reason>
        And the response contains a list of inventory_computers
        And the inventory_computers entities in the response contain the data from <filename>

        Examples: Fields
        | query_filename        | filename         | status_code | reason |
        | active_rpc_port.json  | extra_headers.json | 200 | OK |
        | active_ping_port.json | extra_headers.json | 200 | OK |

    # /inventory/computers/query - bad params
    @negative @p0 @smoke
    @MRC-103
    Scenario Outline: Query Inventory Computers with bad parameters
        Given I have query details in <query_filename> for entities using the inventory_computers api
        When I get with parameters in <param_filename> the query_results from a query of inventory_computers
        Then the inventory_computers response status is 200 OK
        And the response contains a list of inventory_computers
        And the valid url parameters to the inventory_computers api are applied
        And the inventory_computers entities in the response contain the data from <filename>

        Examples: Fields
        | query_filename              | param_filename                  |
        | active_rpc_port.json  | invalid_query_param_values.json |
        | active_ping_port.json | invalid_query_param_values.json |
