Feature: View Active Computer Information
    As an authorized tenant
    I want to be able to see details of my active active_computers

    Background: Test GET /active/computers/<mercury_id>
        Given the account is an authorized tenant
        And the active_computers client URL is /active/computers

    # /active/computers/<mercury_id>
    @positive @p0 @smoke
    Scenario: Get Active Computer Details
        Given a active_computers entity id is located for testing
        When I get the entity using the active_computers api
        Then the active_computers response status is 200 OK
        And the active_computers response contains valid single entity details

    # /active/computers/<mercury_id> - bad id
    @negative @p0 @smoke
    Scenario Outline: Get Active Computer Details With <invalid_mercury_id>
        Given a active_computers <invalid_mercury_id> is provided
        When I get the entity using the active_computers api
        Then the active_computers response status is <status_code> <reason>

        Examples: Invalid Mercury IDs
        | invalid_mercury_id        | status_code          | reason    |
        | invalid_device_id_123     | 404                  | Not Found |
        | 0                         | 404                  | Not Found |
        | 9999999999999999999       | 404                  | Not Found |
        | ""                        | 404                  | Not Found |
        | !@#$%^&*()_               | 404                  | Not Found |
        | None                      | 404                  | Not Found |
        | 123e4567-e89b-12d3-a456-42665544000 | 404        | Not Found |

    # /active/computers/<mercury_id> - bad url
    @negative @p0 @smoke
    @nyi
    Scenario Outline: Get Active Computer Details With <bad_url>
        Given a active_computers <bad_url> is provided
        # TODO change the client url somehow (might need to use different feature file)
        Then the active_computers response status is <status_code> <reason>

        Examples: Invalid Mercury IDs
        | bad_url        | status_code          | reason    |
        | /active/typo   | 404                  | Not Found |
        # TODO etc

    # /active/computers/<mercury_id> - params
    @positive @p0
    Scenario Outline: Get Active Computer Details with parameters
        Given a active_computers entity id is located for testing
        When I get with parameters in <filename> the entity using the active_computers api
        Then the active_computers response status is 200 OK
        And the active_computers response contains valid single entity details
        And url parameters to the active_computers api are applied

        Examples: Fields
        | filename                    |
        | typical_detail_params.json  |
        # TODO more param files

    # TODO negative test for params
    # /active/computers/<mercury_id> - bad params
    @negative @p0 @smoke
    @nyi
    Scenario Outline: Get active Computer Details with bad parameters
        Given a active_computers entity id is located for testing
        When I get with parameters in <filename> the entity using the active_computers api
        # TODO expected behavior?
        Then the active_computers response status is 404 Not Found

        Examples: Fields
        | filename                          |
        | non_existant_params.json          |
        | invalid_details_param_values.json |
        # TODO

    # /active/computers/<mercury_id> - bad method
    @negative @p0 @smoke
    Scenario: Post instead of getting details of active_computers
        When I use post on active_computers
        Then the active_computers response status is 405 METHOD NOT ALLOWED

    # /active/computers/<mercury_id> - wrong headers
    @negative @p0 @smoke
    @nyi
    Scenario Outline: Get active Computer Details with wrong headers
        Given a active_computers entity id is located for testing
        When I get with bad headers in <filename> the entity using the active_computers api
        # TODO expected behavior?
        Then the active_computers response status is 400 Bad Request

        Examples: Fields
        | filename                          |
        | bad_details_headers.json          |
        # TODO
