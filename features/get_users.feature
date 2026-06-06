@get_api
Feature: GET Users API
  As a consumer of the Users API
  I want to retrieve user data
  So that I can display it in my application

  Background:
    Given the GET API is running at "GET_API_BASE_URL"
    And I have a valid auth token "AUTH_TOKEN"

  # ── Sanity ────────────────────────────────────────────────────────────────
  @sanity
  Scenario: Get all users returns 200 with a list
    When I send an authenticated GET request to "/users"
    Then the response status code should be 200
    And the response body should be a non-empty list

  @sanity
  Scenario: Get a specific user by valid ID
    When I send an authenticated GET request to "/users/1"
    Then the response status code should be 200
    And the response body should contain "name" equal to "Alice"

  # ── Regression ────────────────────────────────────────────────────────────
  @regression
  Scenario: Get a specific user and validate DB record
    When I send an authenticated GET request to "/users/1"
    Then the response status code should be 200
    And the response body should contain "name" equal to "Alice"
    And the response data should match the database record for user id 1

  @regression
  Scenario: Get a user with an invalid ID returns 404
    When I send an authenticated GET request to "/users/999"
    Then the response status code should be 404
    And the response body should contain "error"

  @regression
  Scenario: Get user by ID 2 returns correct data
    When I send an authenticated GET request to "/users/2"
    Then the response status code should be 200
    And the response body should contain "name" equal to "Bob"
    And the response body should contain "email" equal to "bob@example.com"

  # ── Auth / Negative ───────────────────────────────────────────────────────
  @auth @regression
  Scenario: Get users without auth token returns 401
    When I send a GET request to "/users" without auth
    Then the response status code should be 401
    And the response body should contain "error"

  @auth @regression
  Scenario: Get users with invalid token returns 401
    When I send an authenticated GET request to "/users" with token "bad-token"
    Then the response status code should be 401
    And the response body should contain "error"

  @auth @regression
  Scenario: Get specific user without auth token returns 401
    When I send a GET request to "/users/1" without auth
    Then the response status code should be 401
    And the response body should contain "error"
