"""Behave environment hooks — start/stop mock APIs around the test suite."""
import subprocess
import time
import sys
import os
import config.env_config as env_config

_get_proc = None
_post_proc = None

MOCK_DIR = os.path.join(os.path.dirname(__file__), "..", "mock_apis")


def before_all(context):
    global _get_proc, _post_proc

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
    # Give Flask a moment to start — increased to 3s for slower machines
    time.sleep(3)
    context.env = env_config


def after_all(context):
    if _get_proc:
        _get_proc.terminate()
    if _post_proc:
        _post_proc.terminate()
