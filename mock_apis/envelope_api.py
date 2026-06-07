"""Mock Envelope API — serves /clients/<clientId>/envelopes/<envelopeNumber> with Bearer token auth."""
from flask import Flask, jsonify, request

app = Flask(__name__)

VALID_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.mock.token"

ENVELOPES = [
    {
        "envelopeNumber":  456,
        "clientId":        123,
        "status":          "delivered",
        "createdAt":       "2024-01-15T10:00:00Z",
        "recipientEmail":  "alice@example.com",
    },
    {
        "envelopeNumber":  457,
        "clientId":        123,
        "status":          "pending",
        "createdAt":       "2024-01-16T10:00:00Z",
        "recipientEmail":  "bob@example.com",
    },
    {
        "envelopeNumber":  789,
        "clientId":        456,
        "status":          "delivered",
        "createdAt":       "2024-01-17T10:00:00Z",
        "recipientEmail":  "charlie@example.com",
    },
]

# Fields returned when includeDetails=false
SUMMARY_FIELDS = {"envelopeNumber", "status"}


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
        None,
    )
    if envelope is None:
        return jsonify({"error": "Envelope not found"}), 404

    include_details = request.args.get("includeDetails", "false").lower() == "true"
    if include_details:
        return jsonify(envelope), 200
    else:
        return jsonify({k: v for k, v in envelope.items() if k in SUMMARY_FIELDS}), 200


if __name__ == "__main__":
    app.run(port=5003)
