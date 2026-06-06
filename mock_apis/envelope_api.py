"""Mock Envelope API — serves /clients/<clientId>/envelopes/<envelopeNumber> with Bearer token auth."""
from flask import Flask, jsonify, request

app = Flask(__name__)

VALID_TOKEN = "test-token-123"

ENVELOPES = [
    {
        "envelopeNumber": 456,
        "clientId": 123,
        "status": "delivered",
        "subject": "Contract Agreement",
        "sentDate": "2024-01-15",
        "recipients": ["alice@example.com"]
    },
    {
        "envelopeNumber": 457,
        "clientId": 123,
        "status": "pending",
        "subject": "NDA Document",
        "sentDate": "2024-01-16",
        "recipients": ["bob@example.com"]
    },
    {
        "envelopeNumber": 789,
        "clientId": 456,
        "status": "completed",
        "subject": "Service Agreement",
        "sentDate": "2024-01-17",
        "recipients": ["charlie@example.com"]
    },
]


def check_auth():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"error": "Missing authorization header"}), 401
    token = auth.split(" ", 1)[1]
    if token != VALID_TOKEN:
        return jsonify({"error": "Invalid or expired token"}), 401
    return None


@app.route("/clients/<int:client_id>/envelopes/<int:envelope_number>", methods=["GET"])
def get_envelope(client_id, envelope_number):
    err = check_auth()
    if err:
        return err
    envelope = next(
        (e for e in ENVELOPES if e["clientId"] == client_id and e["envelopeNumber"] == envelope_number),
        None
    )
    if envelope:
        return jsonify(envelope), 200
    return jsonify({"error": "Envelope not found"}), 404


if __name__ == "__main__":
    app.run(port=5003)
