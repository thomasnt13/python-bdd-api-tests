"""Step definitions for GET Envelope API feature."""
import json
import requests
import allure
import pytest
from jsonschema import validate, ValidationError
from pytest_bdd import scenarios, given, when, then, parsers
from schemas import ENVELOPE_SCHEMA, ERROR_SCHEMA
from config.env_config import ENVELOPE_API_BASE_URL, TOKEN_URL, CLIENT_ID, CLIENT_SECRET, AUDIENCE, EXTRA_HEADERS

pytestmark = [pytest.mark.envelope_api]

scenarios("../features/get_envelopes.feature")


@pytest.fixture
def context():
    return {}


def validate_schema(body, schema, name):
    with allure.step(f"Validate schema: {name}"):
        allure.attach(json.dumps(schema, indent=2), name="Schema", attachment_type=allure.attachment_type.JSON)
        try:
            validate(instance=body, schema=schema)
            allure.attach("✅ Schema validation passed", name="Result", attachment_type=allure.attachment_type.TEXT)
        except ValidationError as e:
            allure.attach(str(e.message), name="Schema Validation Error", attachment_type=allure.attachment_type.TEXT)
            raise


# ── Given ─────────────────────────────────────────────────────────────────────

@given(parsers.parse('the GET API is running at "{base_url_key}"'))
def set_base_url(context, base_url_key):
    resolved = ENVELOPE_API_BASE_URL if base_url_key == "ENVELOPE_API_BASE_URL" else base_url_key
    with allure.step(f"Set base URL to {resolved}"):
        context["base_url"] = resolved
        context["headers"] = {**EXTRA_HEADERS}


@given("I obtain an access token using client credentials")
def obtain_token(context):
    with allure.step("Obtain OAuth access token"):
        allure.attach(
            f"TOKEN_URL: {TOKEN_URL}\nCLIENT_ID: {CLIENT_ID}\nAUDIENCE: {AUDIENCE}",
            name="Token Request", attachment_type=allure.attachment_type.TEXT,
        )
        response = requests.post(
            TOKEN_URL,
            data={
                "grant_type":    "client_credentials",
                "client_id":     CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "audience":      AUDIENCE,
            },
            timeout=5,
        )
        assert response.status_code == 200, (
            f"Token request failed: {response.status_code} {response.text}"
        )
        token = response.json()["access_token"]
        context["headers"]["Authorization"] = f"Bearer {token}"
        allure.attach(f"Token obtained successfully", name="Token Status", attachment_type=allure.attachment_type.TEXT)


# ── When ──────────────────────────────────────────────────────────────────────

@when(parsers.parse('I send an authenticated GET request to "{path}"'))
def send_authenticated_get(context, path):
    url = f"{context['base_url']}{path}"
    with allure.step(f"GET {url} (authenticated)"):
        allure.attach(
            f"URL: GET {url}\nHeaders: {json.dumps(context['headers'], indent=2)}",
            name="Request", attachment_type=allure.attachment_type.TEXT,
        )
        context["response"] = requests.get(url, headers=context["headers"], timeout=5)
        allure.attach(
            f"Status: {context['response'].status_code}\nBody:\n{context['response'].text}",
            name="Response", attachment_type=allure.attachment_type.TEXT,
        )


@when(parsers.parse('I make an unauthenticated GET request to "{path}"'))
def send_get_no_auth(context, path):
    url = f"{context['base_url']}{path}"
    with allure.step(f"GET {url} (no auth)"):
        allure.attach(f"URL: GET {url}\nNo Authorization header", name="Request", attachment_type=allure.attachment_type.TEXT)
        context["response"] = requests.get(url, timeout=5)
        allure.attach(
            f"Status: {context['response'].status_code}\nBody:\n{context['response'].text}",
            name="Response", attachment_type=allure.attachment_type.TEXT,
        )


@when(parsers.parse('I make a GET request to "{path}" with invalid token "{token}"'))
def send_get_with_invalid_token(context, path, token):
    url = f"{context['base_url']}{path}"
    headers = {"Authorization": f"Bearer {token}"}
    with allure.step(f"GET {url} (invalid token)"):
        allure.attach(f"URL: GET {url}\nToken: {token}", name="Request", attachment_type=allure.attachment_type.TEXT)
        context["response"] = requests.get(url, headers=headers, timeout=5)
        allure.attach(
            f"Status: {context['response'].status_code}\nBody:\n{context['response'].text}",
            name="Response", attachment_type=allure.attachment_type.TEXT,
        )


# ── Then ──────────────────────────────────────────────────────────────────────

@then(parsers.parse("the response status code should be {code:d}"))
def check_status(context, code):
    with allure.step(f"Assert status code == {code}"):
        actual = context["response"].status_code
        allure.attach(f"Expected: {code}  |  Actual: {actual}", name="Status Check", attachment_type=allure.attachment_type.TEXT)
        assert actual == code, f"Expected {code}, got {actual}"


@then(parsers.parse('the response body should contain "{key}"'))
def check_field_exists(context, key):
    with allure.step(f"Assert '{key}' exists in response"):
        body = context["response"].json()
        allure.attach(json.dumps(body, indent=2), name="Response Body", attachment_type=allure.attachment_type.JSON)
        schema = ENVELOPE_SCHEMA if context["response"].status_code < 400 else ERROR_SCHEMA
        validate_schema(body, schema, "ENVELOPE_SCHEMA" if context["response"].status_code < 400 else "ERROR_SCHEMA")
        assert key in body, f"Key '{key}' not found in response: {body}"


@then(parsers.parse('the response body should contain "{key}" equal to "{value}"'))
def check_field_value(context, key, value):
    with allure.step(f"Assert '{key}' == '{value}'"):
        body = context["response"].json()
        allure.attach(json.dumps(body, indent=2), name="Response Body", attachment_type=allure.attachment_type.JSON)
        schema = ENVELOPE_SCHEMA if context["response"].status_code < 400 else ERROR_SCHEMA
        validate_schema(body, schema, "ENVELOPE_SCHEMA" if context["response"].status_code < 400 else "ERROR_SCHEMA")
        assert key in body, f"Key '{key}' not found in response: {body}"
        assert str(body[key]) == value, f"Expected '{key}' == '{value}', got '{body[key]}'"
