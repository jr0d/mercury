Feature: Query inventory Computers
    I want to be able to query inventory computers

    Background: Test POST /inventory/computers/query
      Given the account is an authorized tenant
      And the inventory_computers client URL is /inventory/computers

    # /inventory/computers/query
    @positive @p0 @smoke
    Scenario Outline: Query inventory Computers
        Given I have query details in <filename> for entities using the inventory_computers api
        When I get the query_results from a query of inventory_computers
        Then the inventory_computers response status is 200 OK
        And the response contains a list of inventory_computers
        And the inventory_computers entities in the response contain the data from <filename>

        Examples: Filenames
        | filename              |
        #| dmi_sys_vendor.json   |
        #| mem_Dirty.json        |
        | active_rpc_port.json  |
        | active_ping_port.json |
        #| dmi_virtual_box.json |

    # /inventory/computers/query - params
    @positive @p0 @smoke
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
        #| dmi_sys_vendor.json         | typical_query_params.json |
        #| mem_Dirty.json              | typical_query_params.json |

        # TODO negative testing
