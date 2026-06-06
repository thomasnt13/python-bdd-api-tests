"""Mock OAuth 2.0 Token API — Client Credentials Grant."""
from flask import Flask, jsonify, request

app = Flask(__name__)

VALID_CLIENT_ID     = "test-client-id"
VALID_CLIENT_SECRET = "test-client-secret"
VALID_AUDIENCE      = "https://api.example.com"
MOCK_TOKEN          = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.mock.token"


@app.route("/oauth/token", methods=["POST"])
def get_token():
    data = request.form or request.get_json() or {}

    grant_type    = data.get("grant_type")
    client_id     = data.get("client_id")
    client_secret = data.get("client_secret")
    audience      = data.get("audience")

    if grant_type != "client_credentials":
        return jsonify({"error": "unsupported_grant_type"}), 400

    if client_id != VALID_CLIENT_ID or client_secret != VALID_CLIENT_SECRET:
        return jsonify({"error": "invalid_client"}), 401

    if audience != VALID_AUDIENCE:
        return jsonify({"error": "invalid_audience"}), 400

    return jsonify({
        "access_token": MOCK_TOKEN,
        "scope":        "fullcontrol:users",
        "expires_in":   86400,
        "token_type":   "Bearer"
    }), 200


if __name__ == "__main__":
    app.run(port=5004)
