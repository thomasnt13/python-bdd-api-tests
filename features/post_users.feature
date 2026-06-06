@post_api
Feature: POST Users API
  As a consumer of the Users API
  I want to create new users
  So that they are persisted in the system

  Background:
    Given the POST API is running at "http://localhost:5002"
    And I have a valid auth token "test-token-123"

  # ── Sanity ────────────────────────────────────────────────────────────────
  @sanity
  Scenario: Successfully create a new user
    When I send an authenticated POST request to "/users" with name "Charlie" and email "charlie@example.com"
    Then the response status code should be 201
    And the response body should contain "id"
    And the response body should contain "name" equal to "Charlie"

  # ── Regression ────────────────────────────────────────────────────────────
  @regression
  Scenario: Create user and validate DB record
    When I send an authenticated POST request to "/users" with name "Dave" and email "dave@example.com"
    Then the response status code should be 201
    And the response body should contain "name" equal to "Dave"
    And the response data should match the database record for user "Dave"

  @regression
  Scenario: Create user with missing fields returns 422
    When I send an authenticated POST request to "/users" with name "Incomplete" and no email
    Then the response status code should be 422
    And the response body should contain "error"

  @regression
  Scenario: Create user with invalid JSON returns 400
    When I send an authenticated POST request to "/users" with invalid JSON
    Then the response status code should be 400
    And the response body should contain "error"

  @regression
  Scenario: Create user with missing name returns 422
    When I send an authenticated POST request to "/users" with email only "orphan@example.com"
    Then the response status code should be 422
    And the response body should contain "error"

  # ── Auth / Negative ───────────────────────────────────────────────────────
  @auth @regression
  Scenario: Create user without auth token returns 401
    When I send a POST request to "/users" without auth with name "Ghost" and email "ghost@example.com"
    Then the response status code should be 401
    And the response body should contain "error"

  @auth @regression
  Scenario: Create user with invalid token returns 401
    When I send an authenticated POST request to "/users" with name "Ghost" and email "ghost@example.com" with token "wrong-token"
    Then the response status code should be 401
    And the response body should contain "error"
