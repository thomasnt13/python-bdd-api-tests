"""Behave environment hooks — start/stop mock APIs around the test suite."""
import subprocess
import time
import sys
import os
import config.env_config as env_config

_get_proc = None
_post_proc = None
_envelope_proc = None
_token_proc = None

MOCK_DIR = os.path.join(os.path.dirname(__file__), "..", "mock_apis")


def before_all(context):
    global _get_proc, _post_proc, _envelope_proc, _token_proc

    use_mocks = getattr(env_config, "USE_MOCKS", True)

    if use_mocks:
        _get_proc = subprocess.Popen(
            [sys.executable, os.path.join(MOCK_DIR, "get_api.py")],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        _post_proc = subprocess.Popen(
            [sys.executable, os.path.join(MOCK_DIR, "post_api.py")],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        _envelope_proc = subprocess.Popen(
            [sys.executable, os.path.join(MOCK_DIR, "envelope_api.py")],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        _token_proc = subprocess.Popen(
            [sys.executable, os.path.join(MOCK_DIR, "token_api.py")],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        # Give Flask a moment to start
        time.sleep(3)

    context.env = env_config


def before_scenario(context, scenario):
    """Set up base URL and fetch token before each scenario based on feature tags."""
    import requests

    tags = scenario.feature.tags + scenario.tags

    if "envelope_api" in tags:
        context.base_url = env_config.ENVELOPE_API_BASE_URL
        token_url     = getattr(env_config, "TOKEN_URL", None)
        client_id     = getattr(env_config, "CLIENT_ID", None)
        client_secret = getattr(env_config, "CLIENT_SECRET", None)
        audience      = getattr(env_config, "AUDIENCE", None)
        if token_url and client_id and client_secret:
            data = {"grant_type": "client_credentials", "client_id": client_id, "client_secret": client_secret}
            if audience:
                data["audience"] = audience
            resp = requests.post(token_url, data=data, timeout=5)
            context.auth_token = resp.json().get("access_token", "") if resp.status_code == 200 else ""

    elif "get_api" in tags:
        context.base_url  = env_config.GET_API_BASE_URL
        context.auth_token = env_config.AUTH_TOKEN

    elif "post_api" in tags:
        context.base_url  = env_config.POST_API_BASE_URL
        context.auth_token = env_config.AUTH_TOKEN


def after_all(context):
    if _get_proc:
        _get_proc.terminate()
    if _post_proc:
        _post_proc.terminate()
    if _envelope_proc:
        _envelope_proc.terminate()
    if _token_proc:
        _token_proc.terminate()
