@envelope_api
Feature: GET Envelope API
  As a consumer of the Envelope API
  I want to retrieve envelope data by client ID and envelope number
  So that I can display it in my application

  # ── Sanity ────────────────────────────────────────────────────────────────
  @sanity
  Scenario Outline: Retrieve a valid envelope successfully
    When I request the envelope for client "<clientId>" and envelope "<envelopeNumber>"
    Then the response status code should be 200
    And the response matches schema "envelope_schema"
    And the envelope record should exist in the database
    And the envelope response should match the database record

    Examples:
      | clientId | envelopeNumber | description              |
      | 123      | 456            | delivered envelope       |
      | 123      | 457            | pending envelope         |
      | 456      | 789            | different client         |

  # ── Regression ────────────────────────────────────────────────────────────
  @regression
  Scenario Outline: Envelope not found returns 404
    When I request the envelope for client "<clientId>" and envelope "<envelopeNumber>"
    Then the response status code should be 404

    Examples:
      | clientId | envelopeNumber | description              |
      | 999      | 456            | invalid client ID        |
      | 123      | 999            | invalid envelope number  |
      | 999      | 999            | both invalid             |

  # ── Auth / Negative ───────────────────────────────────────────────────────
  @auth @regression
  Scenario Outline: Accessing envelope without valid auth returns 401
    When I make an unauthenticated GET request to "/clients/<clientId>/envelopes/<envelopeNumber>"
    Then the response status code should be 401

    Examples:
      | clientId | envelopeNumber |
      | 123      | 456            |

  @auth @regression
  Scenario Outline: Accessing envelope with invalid token returns 401
    When I make a GET request to "/clients/<clientId>/envelopes/<envelopeNumber>" with invalid token "<token>"
    Then the response status code should be 401

    Examples:
      | clientId | envelopeNumber | token        |
      | 123      | 456            | bad-token    |
      | 123      | 456            | expired-jwt  |
