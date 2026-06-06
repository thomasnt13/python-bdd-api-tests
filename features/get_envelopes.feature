@envelope_api
Feature: GET Envelope API
  As a consumer of the Envelope API
  I want to retrieve envelope data by client ID and envelope number
  So that I can display it in my application

  Background:
    Given the GET API is running at "ENVELOPE_API_BASE_URL"
    And I obtain an access token using client credentials

  # ── Sanity ────────────────────────────────────────────────────────────────
  @sanity
  Scenario: Get envelope by valid client ID and envelope number returns 200
    When I send an authenticated GET request to "/clients/123/envelopes/456"
    Then the response status code should be 200

  # ── Regression ────────────────────────────────────────────────────────────
  @regression
  Scenario: Get envelope response contains expected fields
    When I send an authenticated GET request to "/clients/123/envelopes/456"
    Then the response status code should be 200
    And the response body should contain "envelopeNumber"
    And the response body should contain "clientId"

  @regression
  Scenario: Get envelope with invalid client ID returns 404
    When I send an authenticated GET request to "/clients/999/envelopes/456"
    Then the response status code should be 404

  @regression
  Scenario: Get envelope with invalid envelope number returns 404
    When I send an authenticated GET request to "/clients/123/envelopes/999"
    Then the response status code should be 404

  # ── Auth / Negative ───────────────────────────────────────────────────────
  @auth @regression
  Scenario: Get envelope without auth token returns 401
    When I make an unauthenticated GET request to "/clients/123/envelopes/456"
    Then the response status code should be 401

  @auth @regression
  Scenario: Get envelope with invalid token returns 401
    When I make a GET request to "/clients/123/envelopes/456" with invalid token "bad-token"
    Then the response status code should be 401
