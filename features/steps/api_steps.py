import json
import os
import sys
import allure
import jsonschema
import requests
from behave import given, when, then

# allow importing from features/utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.db_helper import fetch_envelope

SCHEMAS_DIR = os.path.join(os.path.dirname(__file__), "..", "schemas")


def _resolve(context, key):
    """Resolve a feature-file string against env_config, or return it as-is."""
    return getattr(context.env, key, key)


def _attach_request(url, method="GET", headers=None, body=None):
    info = f"Method: {method}\nURL: {url}"
    if headers:
        safe_headers = {k: (v[:20] + "...") if k == "Authorization" else v for k, v in headers.items()}
        info += f"\nHeaders: {json.dumps(safe_headers, indent=2)}"
    if body:
        info += f"\nBody: {json.dumps(body, indent=2)}"
    allure.attach(info, name="Request", attachment_type=allure.attachment_type.TEXT)


def _attach_response(response):
    try:
        body = json.dumps(response.json(), indent=2)
    except Exception:
        body = response.text
    allure.attach(
        f"Status: {response.status_code}\nBody:\n{body}",
        name="Response", attachment_type=allure.attachment_type.TEXT,
    )


# ── Given ────────────────────────────────────────────────────────────────────

@given('the GET API is running at "{base_url_key}"')
def step_set_get_base_url(context, base_url_key):
    context.base_url = _resolve(context, base_url_key)
    allure.attach(f"Base URL: {context.base_url}", name="Config", attachment_type=allure.attachment_type.TEXT)


@given('the POST API is running at "{base_url_key}"')
def step_set_post_base_url(context, base_url_key):
    context.base_url = _resolve(context, base_url_key)
    allure.attach(f"Base URL: {context.base_url}", name="Config", attachment_type=allure.attachment_type.TEXT)


@given('I have a valid auth token "{token_key}"')
def step_set_auth_token(context, token_key):
    context.auth_token = _resolve(context, token_key)


@given('I obtain an access token using client credentials')
def step_obtain_token(context):
    env = context.env
    token_url     = getattr(env, "TOKEN_URL",     None)
    client_id     = getattr(env, "CLIENT_ID",     None)
    client_secret = getattr(env, "CLIENT_SECRET", None)
    audience      = getattr(env, "AUDIENCE",      None)

    assert token_url,     "TOKEN_URL is not set in env_config.py"
    assert client_id,     "CLIENT_ID is not set in env_config.py"
    assert client_secret, "CLIENT_SECRET is not set in env_config.py"

    data = {
        "grant_type":    "client_credentials",
        "client_id":     client_id,
        "client_secret": client_secret,
    }
    if audience:
        data["audience"] = audience

    allure.attach(
        f"TOKEN_URL: {token_url}\nCLIENT_ID: {client_id}\nAUDIENCE: {audience or 'N/A'}",
        name="Token Request", attachment_type=allure.attachment_type.TEXT,
    )
    response = requests.post(token_url, data=data, timeout=5)
    assert response.status_code == 200, (
        f"Token request failed: {response.status_code} {response.text}"
    )
    context.auth_token = response.json()["access_token"]
    allure.attach("Token obtained successfully ✅", name="Token Status", attachment_type=allure.attachment_type.TEXT)


# ── When ─────────────────────────────────────────────────────────────────────

@when('I request the envelope for client "{client_id}" and envelope "{envelope_number}"')
def step_request_envelope(context, client_id, envelope_number):
    path = f"/clients/{client_id}/envelopes/{envelope_number}"
    url = f"{context.base_url}{path}"
    headers = {"Authorization": f"Bearer {context.auth_token}"}
    headers.update(getattr(context.env, "EXTRA_HEADERS", {}))
    _attach_request(url, headers=headers)
    context.response = requests.get(url, headers=headers, timeout=5)
    _attach_response(context.response)


@when('I send a GET request to "{path}"')
def step_send_get(context, path):
    url = f"{context.base_url}{path}"
    _attach_request(url)
    context.response = requests.get(url, timeout=5)
    _attach_response(context.response)


@when('I make an unauthenticated GET request to "{path}"')
def step_send_get_no_auth(context, path):
    url = f"{context.base_url}{path}"
    allure.attach(f"Method: GET\nURL: {url}\nNo Authorization header", name="Request", attachment_type=allure.attachment_type.TEXT)
    context.response = requests.get(url, timeout=5)
    _attach_response(context.response)


@when('I send an authenticated GET request to "{path}"')
def step_send_authenticated_get(context, path):
    url = f"{context.base_url}{path}"
    headers = {"Authorization": f"Bearer {context.auth_token}"}
    headers.update(getattr(context.env, "EXTRA_HEADERS", {}))
    _attach_request(url, headers=headers)
    context.response = requests.get(url, headers=headers, timeout=5)
    _attach_response(context.response)


@when('I make a GET request to "{path}" with invalid token "{token}"')
def step_send_get_with_invalid_token(context, path, token):
    url = f"{context.base_url}{path}"
    headers = {"Authorization": f"Bearer {token}"}
    _attach_request(url, headers=headers)
    context.response = requests.get(url, headers=headers, timeout=5)
    _attach_response(context.response)


@when('I send a POST request to "{path}" with body')
def step_send_post_with_body(context, path):
    url = f"{context.base_url}{path}"
    payload = json.loads(context.text)
    _attach_request(url, method="POST", body=payload)
    context.response = requests.post(url, json=payload, timeout=5)
    _attach_response(context.response)


@when('I send a POST request to "{path}" with invalid JSON')
def step_send_post_invalid_json(context, path):
    url = f"{context.base_url}{path}"
    allure.attach(f"Method: POST\nURL: {url}\nBody: not-json (invalid)", name="Request", attachment_type=allure.attachment_type.TEXT)
    context.response = requests.post(
        url, data="not-json",
        headers={"Content-Type": "application/json"}, timeout=5,
    )
    _attach_response(context.response)


# ── Then ─────────────────────────────────────────────────────────────────────

@then('the response status code should be {expected_code:d}')
def step_check_status(context, expected_code):
    actual = context.response.status_code
    allure.attach(
        f"Expected: {expected_code}  |  Actual: {actual}  |  {'✅ PASS' if actual == expected_code else '❌ FAIL'}",
        name="Status Check", attachment_type=allure.attachment_type.TEXT,
    )
    assert actual == expected_code, (
        f"Expected status {expected_code}, got {actual}. Body: {context.response.text}"
    )


@then('the response body should be a non-empty list')
def step_check_non_empty_list(context):
    body = context.response.json()
    allure.attach(json.dumps(body, indent=2), name="Response Body", attachment_type=allure.attachment_type.JSON)
    assert isinstance(body, list) and len(body) > 0, f"Expected a non-empty list, got: {body}"


@then('the response body should contain "{key}" equal to "{value}"')
def step_check_field_value(context, key, value):
    body = context.response.json()
    allure.attach(json.dumps(body, indent=2), name="Response Body", attachment_type=allure.attachment_type.JSON)
    assert key in body, f"Key '{key}' not found in response: {body}"
    assert str(body[key]) == value, f"Expected '{key}' == '{value}', got '{body[key]}'"


@then('the response body should contain "{key}"')
def step_check_field_exists(context, key):
    body = context.response.json()
    allure.attach(json.dumps(body, indent=2), name="Response Body", attachment_type=allure.attachment_type.JSON)
    assert key in body, f"Key '{key}' not found in response: {body}"
    allure.attach(f"✅ '{key}' = {body[key]}", name=f"Field: {key}", attachment_type=allure.attachment_type.TEXT)


@then('the response matches schema "{schema_name}"')
def step_validate_schema(context, schema_name):
    schema_path = os.path.join(SCHEMAS_DIR, f"{schema_name}.json")
    with open(schema_path) as f:
        schema = json.load(f)
    body = context.response.json()
    allure.attach(json.dumps(body, indent=2), name="Response Body", attachment_type=allure.attachment_type.JSON)
    allure.attach(json.dumps(schema, indent=2), name="Expected Schema", attachment_type=allure.attachment_type.JSON)
    try:
        jsonschema.validate(instance=body, schema=schema)
        allure.attach("✅ Schema validation passed", name="Schema Check", attachment_type=allure.attachment_type.TEXT)
    except jsonschema.ValidationError as e:
        allure.attach(f"❌ {e.message}", name="Schema Check", attachment_type=allure.attachment_type.TEXT)
        raise AssertionError(f"Schema validation failed: {e.message}")


# ── DB Validation ─────────────────────────────────────────────────────────────

@then('the envelope record should exist in the database')
def step_db_record_exists(context):
    """Verify a row exists in the DB for the envelope returned by the API."""
    body        = context.response.json()
    client_id   = body.get("clientId")
    envelope_no = body.get("envelopeNumber")
    db_config   = context.env.DB_CONFIG
    table       = getattr(context.env, "ENVELOPES_TABLE", "dbo.Envelopes")

    allure.attach(
        f"Table: {table}\nclientId: {client_id}\nenvelopeNumber: {envelope_no}",
        name="DB Query", attachment_type=allure.attachment_type.TEXT,
    )
    row = fetch_envelope(db_config, table, client_id, envelope_no)
    assert row is not None, (
        f"No DB record found for clientId={client_id}, envelopeNumber={envelope_no} in {table}"
    )
    allure.attach(json.dumps(row, indent=2, default=str), name="DB Record", attachment_type=allure.attachment_type.JSON)


@then('the envelope response should match the database record')
def step_db_response_matches(context):
    """Verify API response values match the DB row field-by-field."""
    body        = context.response.json()
    client_id   = body.get("clientId")
    envelope_no = body.get("envelopeNumber")
    db_config   = context.env.DB_CONFIG
    table       = getattr(context.env, "ENVELOPES_TABLE", "dbo.Envelopes")

    row = fetch_envelope(db_config, table, client_id, envelope_no)
    assert row is not None, (
        f"No DB record found for clientId={client_id}, envelopeNumber={envelope_no}"
    )

    # Map API response keys → DB column names (adjust if your columns differ)
    field_map = {
        "envelopeNumber": "envelope_number",
        "clientId":       "client_id",
        "status":         "status",
    }
    mismatches = []
    for api_key, db_col in field_map.items():
        if db_col not in row:
            continue
        api_val = str(body.get(api_key, ""))
        db_val  = str(row[db_col])
        if api_val != db_val:
            mismatches.append(f"  {api_key}: API={api_val!r}  DB={db_val!r}")

    allure.attach(json.dumps(row, indent=2, default=str), name="DB Record", attachment_type=allure.attachment_type.JSON)
    allure.attach(json.dumps(body, indent=2), name="API Response", attachment_type=allure.attachment_type.JSON)

    if mismatches:
        msg = "API vs DB mismatches:\n" + "\n".join(mismatches)
        allure.attach(f"❌ {msg}", name="DB Match Check", attachment_type=allure.attachment_type.TEXT)
        raise AssertionError(msg)

    allure.attach("✅ API response matches DB record", name="DB Match Check", attachment_type=allure.attachment_type.TEXT)
