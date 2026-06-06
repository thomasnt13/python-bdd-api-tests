"""Pytest fixtures — start/stop mock APIs for the whole test session."""
import subprocess
import time
import sys
import os
import socket
import pytest

sys.path.insert(0, os.path.dirname(__file__))
from config.env_config import GET_API_BASE_URL, POST_API_BASE_URL, AUTH_TOKEN, EXTRA_HEADERS, ENVELOPE_API_BASE_URL, TOKEN_URL

MOCK_DIR = os.path.join(os.path.dirname(__file__), "mock_apis")


def kill_port(port):
    """Kill any process occupying the given port (Windows)."""
    try:
        result = subprocess.run(
            f'netstat -ano | findstr :{port}',
            shell=True, capture_output=True, text=True
        )
        for line in result.stdout.splitlines():
            parts = line.split()
            if parts and parts[-1].isdigit():
                pid = int(parts[-1])
                subprocess.run(f"taskkill /PID {pid} /F", shell=True,
                               capture_output=True)
    except Exception:
        pass


def wait_for_port(port, timeout=10):
    """Wait until a port is accepting connections."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(("localhost", port), timeout=1):
                return True
        except OSError:
            time.sleep(0.3)
    return False


@pytest.fixture(scope="session", autouse=True)
def start_mock_apis():
    # Kill any stale processes on these ports first
    kill_port(5001)
    kill_port(5002)
    kill_port(5003)
    kill_port(5004)
    time.sleep(1)

    get_proc = subprocess.Popen(
        [sys.executable, os.path.join(MOCK_DIR, "get_api.py")],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    post_proc = subprocess.Popen(
        [sys.executable, os.path.join(MOCK_DIR, "post_api.py")],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    envelope_proc = subprocess.Popen(
        [sys.executable, os.path.join(MOCK_DIR, "envelope_api.py")],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    token_proc = subprocess.Popen(
        [sys.executable, os.path.join(MOCK_DIR, "token_api.py")],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Wait until all ports are ready
    wait_for_port(5001)
    wait_for_port(5002)
    wait_for_port(5003)
    wait_for_port(5004)

    yield

    get_proc.terminate()
    post_proc.terminate()
    envelope_proc.terminate()
    token_proc.terminate()
    kill_port(5001)
    kill_port(5002)
    kill_port(5003)
    kill_port(5004)
