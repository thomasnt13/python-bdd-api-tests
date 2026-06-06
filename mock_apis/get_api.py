"""Mock GET API — serves /users and /users/<id> with Bearer token auth."""
from flask import Flask, jsonify, request

app = Flask(__name__)

VALID_TOKEN = "test-token-123"

USERS = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob",   "email": "bob@example.com"},
]


def check_auth():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"error": "Missing authorization header"}), 401
    token = auth.split(" ", 1)[1]
    if token != VALID_TOKEN:
        return jsonify({"error": "Invalid or expired token"}), 401
    return None


@app.route("/users", methods=["GET"])
def get_users():
    err = check_auth()
    if err:
        return err
    return jsonify(USERS), 200


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    err = check_auth()
    if err:
        return err
    user = next((u for u in USERS if u["id"] == user_id), None)
    if user:
        return jsonify(user), 200
    return jsonify({"error": "User not found"}), 404


if __name__ == "__main__":
    app.run(port=5001)
