Feature: List inventory Computers
    As an authorized tenant
    I want to be able to see a list of my inventory_computers

    Background: Test GET /inventory/computers
        Given the account is an authorized tenant
        And the inventory_computers client URL is /inventory/computers

    # /inventory/computers
    @positive @p0 @smoke
    @MRC-57
    Scenario: Get list of inventory_computers
        When I get the list of inventory_computers
        Then the inventory_computers response status is 200 OK
        And the response contains a list of inventory_computers

    # /inventory/computers - bad url
    @negative @p0 @smoke
    @MRC-68
    Scenario Outline: Get list of inventory_computers with a bad url
        Given a inventory_computers bad url <bad_url> is provided
        When I get the list of inventory_computers
        Then the inventory_computers response status is <status_code> <reason>

        Examples: Bad URLs
        | bad_url           | status_code          | reason    |
        | /inventory/typo   | 404                  | Not Found |

    # /inventory/computers - params
    @positive @p0
    @MRC-70
    Scenario Outline: Get list of inventory_computers with parameters
        When I get with parameters in <filename> the list of inventory_computers
        Then the inventory_computers response status is 200 OK
        And the response contains a list of inventory_computers
        And url parameters to the inventory_computers api are applied

        Examples: Filename
        | filename                  |
        | typical_list_params.json  |        

    # /inventory/computer - offset_id
    @positive @p0
    @MRC-70
    @offset @not-local
    Scenario Outline: Get list of inventory_computers and test the offset_id param
        When I get with parameters in <filename> the list of inventory_computers
        Then I get with offset parameters in <second_few> the list of inventory_computers
        Then the inventory_computers response status is 200 OK
        And the response contains an offset list of inventory_computers that have been offset by the offset_id

        Examples: Filenames
        | filename        | second_few     |
        | first_ten.json  | next_five.json |

    # /inventory/computers - bad params
    @positive @p0
    @MRC-103
    Scenario Outline: Get list of inventory_computers with bad parameters
        When I get with parameters in <filename> the list of inventory_computers
        Then the inventory_computers response status is 200 OK
        And the response contains a list of inventory_computers
        And the valid url parameters to the inventory_computers api are applied

        Examples: Filename
        | filename                         |
        | non_existant_list_params.json    |
        | invalid_list_param_values.json   |
        | invalid_list_param_values_2.json |

    # /inventory/computers - bad method
    @negative @p0 @smoke
    @MRC-68
    Scenario: Post instead of getting list of inventory_computers
        When I use post on inventory_computers
        Then the inventory_computers response status is 405 METHOD NOT ALLOWED

    # /inventory/computers - ignored headers
    @positive @p0 @smoke
    @MRC-103
    Scenario Outline: Get list of inventory_computers with invalid headers that are ignored by mercury
        When I get with bad headers in <filename> the list of inventory_computers
        Then the inventory_computers response status is 200 OK
        And the response contains a list of inventory_computers

        Examples: Filename
        | filename         |
        | bad_headers.json |
