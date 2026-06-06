import json
import requests
from behave import given, when, then


# ── Given ────────────────────────────────────────────────────────────────────

@given('the GET API is running at "{base_url}"')
def step_set_get_base_url(context, base_url):
    context.base_url = base_url


@given('the POST API is running at "{base_url}"')
def step_set_post_base_url(context, base_url):
    context.base_url = base_url


# ── When ─────────────────────────────────────────────────────────────────────

@when('I send a GET request to "{path}"')
def step_send_get(context, path):
    context.response = requests.get(f"{context.base_url}{path}", timeout=5)


@when('I send a POST request to "{path}" with body')
def step_send_post_with_body(context, path):
    payload = json.loads(context.text)
    context.response = requests.post(
        f"{context.base_url}{path}",
        json=payload,
        timeout=5,
    )


@when('I send a POST request to "{path}" with invalid JSON')
def step_send_post_invalid_json(context, path):
    context.response = requests.post(
        f"{context.base_url}{path}",
        data="not-json",
        headers={"Content-Type": "application/json"},
        timeout=5,
    )


# ── Then ─────────────────────────────────────────────────────────────────────

@then('the response status code should be {expected_code:d}')
def step_check_status(context, expected_code):
    actual = context.response.status_code
    assert actual == expected_code, (
        f"Expected status {expected_code}, got {actual}. "
        f"Body: {context.response.text}"
    )


@then('the response body should be a non-empty list')
def step_check_non_empty_list(context):
    body = context.response.json()
    assert isinstance(body, list) and len(body) > 0, (
        f"Expected a non-empty list, got: {body}"
    )


@then('the response body should contain "{key}" equal to "{value}"')
def step_check_field_value(context, key, value):
    body = context.response.json()
    assert key in body, f"Key '{key}' not found in response: {body}"
    assert str(body[key]) == value, (
        f"Expected '{key}' == '{value}', got '{body[key]}'"
    )


@then('the response body should contain "{key}"')
def step_check_field_exists(context, key):
    body = context.response.json()
    assert key in body, f"Key '{key}' not found in response: {body}"
