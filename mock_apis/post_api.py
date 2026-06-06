"""Mock POST API — accepts new users via /users with Bearer token auth."""
from flask import Flask, jsonify, request

app = Flask(__name__)

VALID_TOKEN = "test-token-123"
USERS = []
_next_id = 1


def check_auth():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"error": "Missing authorization header"}), 401
    token = auth.split(" ", 1)[1]
    if token != VALID_TOKEN:
        return jsonify({"error": "Invalid or expired token"}), 401
    return None


@app.route("/users", methods=["POST"])
def create_user():
    global _next_id
    err = check_auth()
    if err:
        return err
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    missing = {"name", "email"} - data.keys()
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 422
    user = {"id": _next_id, "name": data["name"], "email": data["email"]}
    USERS.append(user)
    _next_id += 1
    return jsonify(user), 201


if __name__ == "__main__":
    app.run(port=5002)
