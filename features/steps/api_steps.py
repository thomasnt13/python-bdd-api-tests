import json
import requests
from behave import given, when, then


def _resolve(context, key):
    """Resolve a feature-file string against env_config, or return it as-is."""
    return getattr(context.env, key, key)


# ── Given ────────────────────────────────────────────────────────────────────

@given('the GET API is running at "{base_url_key}"')
def step_set_get_base_url(context, base_url_key):
    context.base_url = _resolve(context, base_url_key)


@given('the POST API is running at "{base_url_key}"')
def step_set_post_base_url(context, base_url_key):
    context.base_url = _resolve(context, base_url_key)


@given('I have a valid auth token "{token_key}"')
def step_set_auth_token(context, token_key):
    context.auth_token = _resolve(context, token_key)


# ── When ─────────────────────────────────────────────────────────────────────

@when('I send a GET request to "{path}"')
def step_send_get(context, path):
    context.response = requests.get(f"{context.base_url}{path}", timeout=5)


@when('I send a GET request to "{path}" without auth')
def step_send_get_no_auth(context, path):
    context.response = requests.get(f"{context.base_url}{path}", timeout=5)


@when('I send an authenticated GET request to "{path}"')
def step_send_authenticated_get(context, path):
    headers = {"Authorization": f"Bearer {context.auth_token}"}
    headers.update(getattr(context.env, "EXTRA_HEADERS", {}))
    context.response = requests.get(
        f"{context.base_url}{path}", headers=headers, timeout=5
    )


@when('I send an authenticated GET request to "{path}" with token "{token}"')
def step_send_authenticated_get_with_token(context, path, token):
    headers = {"Authorization": f"Bearer {token}"}
    context.response = requests.get(
        f"{context.base_url}{path}", headers=headers, timeout=5
    )


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
