"""Step definitions for POST Users API feature."""
import json
import requests
import allure
import pytest
from jsonschema import validate, ValidationError
from pytest_bdd import scenarios, given, when, then, parsers
from schemas import USER_SCHEMA, ERROR_SCHEMA
from db_helper import fetch_user_by_name, validate_api_vs_db, DB_NOT_CONFIGURED

pytestmark = [pytest.mark.post_api]

scenarios("../features/post_users.feature")


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

@given(parsers.parse('the POST API is running at "{base_url}"'))
def set_base_url(context, base_url):
    with allure.step(f"Set base URL to {base_url}"):
        context["base_url"] = base_url
        context["headers"] = {"Content-Type": "application/json"}


@given(parsers.parse('I have a valid auth token "{token}"'))
def set_auth_token(context, token):
    with allure.step("Set Authorization header"):
        context["token"] = token
        context["headers"]["Authorization"] = f"Bearer {token}"


# ── When ──────────────────────────────────────────────────────────────────────

@when(parsers.parse('I send an authenticated POST request to "{path}" with name "{name}" and email "{email}"'))
def send_post_with_body(context, path, name, email):
    url = f"{context['base_url']}{path}"
    payload = {"name": name, "email": email}
    with allure.step(f"POST {url}"):
        allure.attach(f"URL: POST {url}\nBody:\n{json.dumps(payload, indent=2)}", name="Request", attachment_type=allure.attachment_type.TEXT)
        context["response"] = requests.post(url, json=payload, headers=context["headers"], timeout=5)
        allure.attach(f"Status: {context['response'].status_code}\nBody:\n{context['response'].text}", name="Response", attachment_type=allure.attachment_type.TEXT)


@when(parsers.parse('I send an authenticated POST request to "{path}" with name "{name}" and no email'))
def send_post_missing_email(context, path, name):
    url = f"{context['base_url']}{path}"
    payload = {"name": name}
    with allure.step(f"POST {url} (missing email)"):
        allure.attach(f"URL: POST {url}\nBody:\n{json.dumps(payload, indent=2)}", name="Request", attachment_type=allure.attachment_type.TEXT)
        context["response"] = requests.post(url, json=payload, headers=context["headers"], timeout=5)
        allure.attach(f"Status: {context['response'].status_code}\nBody:\n{context['response'].text}", name="Response", attachment_type=allure.attachment_type.TEXT)


@when(parsers.parse('I send an authenticated POST request to "/users" with email only "{email}"'))
def send_post_email_only(context, email):
    url = f"{context['base_url']}/users"
    payload = {"email": email}
    with allure.step(f"POST {url} (email only, missing name)"):
        allure.attach(f"URL: POST {url}\nBody:\n{json.dumps(payload, indent=2)}", name="Request", attachment_type=allure.attachment_type.TEXT)
        context["response"] = requests.post(url, json=payload, headers=context["headers"], timeout=5)
        allure.attach(f"Status: {context['response'].status_code}\nBody:\n{context['response'].text}", name="Response", attachment_type=allure.attachment_type.TEXT)


@when(parsers.parse('I send an authenticated POST request to "{path}" with invalid JSON'))
def send_post_invalid_json(context, path):
    url = f"{context['base_url']}{path}"
    with allure.step(f"POST {url} (invalid JSON)"):
        allure.attach(f"URL: POST {url}\nBody: not-json", name="Request", attachment_type=allure.attachment_type.TEXT)
        context["response"] = requests.post(url, data="not-json", headers=context["headers"], timeout=5)
        allure.attach(f"Status: {context['response'].status_code}\nBody:\n{context['response'].text}", name="Response", attachment_type=allure.attachment_type.TEXT)


@when(parsers.parse('I send a POST request to "{path}" without auth with name "{name}" and email "{email}"'))
def send_post_no_auth(context, path, name, email):
    url = f"{context['base_url']}{path}"
    payload = {"name": name, "email": email}
    with allure.step(f"POST {url} (no auth)"):
        allure.attach(f"URL: POST {url}\nNo Authorization header\nBody:\n{json.dumps(payload, indent=2)}", name="Request", attachment_type=allure.attachment_type.TEXT)
        context["response"] = requests.post(url, json=payload, timeout=5)
        allure.attach(f"Status: {context['response'].status_code}\nBody:\n{context['response'].text}", name="Response", attachment_type=allure.attachment_type.TEXT)


@when(parsers.parse('I send an authenticated POST request to "{path}" with name "{name}" and email "{email}" with token "{token}"'))
def send_post_with_bad_token(context, path, name, email, token):
    url = f"{context['base_url']}{path}"
    payload = {"name": name, "email": email}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    with allure.step(f"POST {url} (token: {token})"):
        allure.attach(f"URL: POST {url}\nToken: {token}\nBody:\n{json.dumps(payload, indent=2)}", name="Request", attachment_type=allure.attachment_type.TEXT)
        context["response"] = requests.post(url, json=payload, headers=headers, timeout=5)
        allure.attach(f"Status: {context['response'].status_code}\nBody:\n{context['response'].text}", name="Response", attachment_type=allure.attachment_type.TEXT)


# ── Then ──────────────────────────────────────────────────────────────────────

@then(parsers.parse("the response status code should be {code:d}"))
def check_status(context, code):
    with allure.step(f"Assert status code == {code}"):
        actual = context["response"].status_code
        allure.attach(f"Expected: {code}  |  Actual: {actual}", name="Status Check", attachment_type=allure.attachment_type.TEXT)
        assert actual == code, f"Expected {code}, got {actual}"


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


@then(parsers.parse('the response data should match the database record for user "{name}"'))
def validate_db_match_by_name(context, name):
    with allure.step(f"Validate API response matches DB record for user '{name}'"):
        if DB_NOT_CONFIGURED:
            allure.attach("DB not configured — skipping DB validation.", name="DB Status", attachment_type=allure.attachment_type.TEXT)
            pytest.skip("DB credentials not configured in config/db_config.py")
        api_record = context["response"].json()
        allure.attach(json.dumps(api_record, indent=2), name="API Record", attachment_type=allure.attachment_type.JSON)
        db_record = fetch_user_by_name(name)
        if db_record is None:
            raise AssertionError(f"User '{name}' not found in database")
        allure.attach(json.dumps(db_record, indent=2), name="DB Record", attachment_type=allure.attachment_type.JSON)
        validate_api_vs_db(api_record, db_record)
