"""Step definitions for GET Users API feature."""
import json
import requests
import allure
import pytest
from jsonschema import validate, ValidationError
from pytest_bdd import scenarios, given, when, then, parsers
from schemas import USER_SCHEMA, USER_LIST_SCHEMA, ERROR_SCHEMA
from db_helper import fetch_user_by_id, validate_api_vs_db, DB_NOT_CONFIGURED

pytestmark = [pytest.mark.get_api]

scenarios("../features/get_users.feature")


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

@given(parsers.parse('the GET API is running at "{base_url}"'))
def set_base_url(context, base_url):
    with allure.step(f"Set base URL to {base_url}"):
        context["base_url"] = base_url
        context["headers"] = {}


@given(parsers.parse('I have a valid auth token "{token}"'))
def set_auth_token(context, token):
    with allure.step("Set Authorization header"):
        context["token"] = token
        context["headers"]["Authorization"] = f"Bearer {token}"


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


@when(parsers.parse('I send an authenticated GET request to "{path}" with token "{token}"'))
def send_get_with_custom_token(context, path, token):
    url = f"{context['base_url']}{path}"
    headers = {"Authorization": f"Bearer {token}"}
    with allure.step(f"GET {url} (token: {token})"):
        allure.attach(f"URL: GET {url}\nToken: {token}", name="Request", attachment_type=allure.attachment_type.TEXT)
        context["response"] = requests.get(url, headers=headers, timeout=5)
        allure.attach(
            f"Status: {context['response'].status_code}\nBody:\n{context['response'].text}",
            name="Response", attachment_type=allure.attachment_type.TEXT,
        )


@when(parsers.parse('I send a GET request to "{path}" without auth'))
def send_get_no_auth(context, path):
    url = f"{context['base_url']}{path}"
    with allure.step(f"GET {url} (no auth)"):
        allure.attach(f"URL: GET {url}\nNo Authorization header", name="Request", attachment_type=allure.attachment_type.TEXT)
        context["response"] = requests.get(url, timeout=5)
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


@then("the response body should be a non-empty list")
def check_non_empty_list(context):
    with allure.step("Assert response is a non-empty list and validate schema"):
        body = context["response"].json()
        allure.attach(json.dumps(body, indent=2), name="Response Body", attachment_type=allure.attachment_type.JSON)
        assert isinstance(body, list) and len(body) > 0
        validate_schema(body, USER_LIST_SCHEMA, "USER_LIST_SCHEMA")


@then(parsers.parse('the response body should contain "{key}" equal to "{value}"'))
def check_field_value(context, key, value):
    with allure.step(f"Assert '{key}' == '{value}'"):
        body = context["response"].json()
        allure.attach(json.dumps(body, indent=2), name="Response Body", attachment_type=allure.attachment_type.JSON)
        schema = USER_SCHEMA if context["response"].status_code < 400 else ERROR_SCHEMA
        validate_schema(body, schema, "USER_SCHEMA" if context["response"].status_code < 400 else "ERROR_SCHEMA")
        assert str(body[key]) == value


@then(parsers.parse('the response body should contain "{key}"'))
def check_field_exists(context, key):
    with allure.step(f"Assert '{key}' exists in response"):
        body = context["response"].json()
        allure.attach(json.dumps(body, indent=2), name="Response Body", attachment_type=allure.attachment_type.JSON)
        schema = USER_SCHEMA if context["response"].status_code < 400 else ERROR_SCHEMA
        validate_schema(body, schema, "USER_SCHEMA" if context["response"].status_code < 400 else "ERROR_SCHEMA")
        assert key in body


@then(parsers.parse("the response data should match the database record for user id {user_id:d}"))
def validate_db_match_by_id(context, user_id):
    with allure.step(f"Validate API response matches DB record for user id {user_id}"):
        if DB_NOT_CONFIGURED:
            allure.attach("DB not configured — skipping DB validation.", name="DB Status", attachment_type=allure.attachment_type.TEXT)
            pytest.skip("DB credentials not configured in config/db_config.py")
        api_record = context["response"].json()
        allure.attach(json.dumps(api_record, indent=2), name="API Record", attachment_type=allure.attachment_type.JSON)
        db_record = fetch_user_by_id(user_id)
        if db_record is None:
            raise AssertionError(f"User id={user_id} not found in database")
        allure.attach(json.dumps(db_record, indent=2), name="DB Record", attachment_type=allure.attachment_type.JSON)
        validate_api_vs_db(api_record, db_record)
