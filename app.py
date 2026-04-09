from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    create_access_token,
    get_jwt
)
from datetime import timedelta
import os

import single_access_kpi
import fmea
import all_access_kpi
import health_index

app = Flask(__name__)

# ================= JWT CONFIG =================
app.config["JWT_SECRET_KEY"] = os.getenv(
    "JWT_SECRET_KEY",
    "this_is_a_very_long_random_secret_key_1234567890"
)

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=10)  # ⏳ for testing

jwt = JWTManager(app)

# ================= TOKEN BLACKLIST =================
blacklist = set()

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    return jwt_payload["jti"] in blacklist


# ================= LOGIN API =================
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Missing JSON data"}), 400

        username = data.get("username")
        password = data.get("password")

        # 🔴 Replace with DB validation
        if username == "admin" and password == "1234":
            token = create_access_token(identity=username)
            return jsonify({"access_token": token}), 200

        return jsonify({"error": "Invalid credentials"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================= LOGOUT API =================
@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    try:
        jti = get_jwt()["jti"]   # unique token ID
        blacklist.add(jti)      # revoke token

        return jsonify({"msg": "Token revoked successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================= API ROUTES (PROTECTED) =================
@app.route("/single_access_kpi", methods=["POST"])
@jwt_required()
def handle_single_access_kpi():
    return process_request(single_access_kpi.main)


@app.route("/fmea", methods=["POST"])
@jwt_required()
def handle_fmea():
    return process_request(fmea.main)


@app.route("/all_access_kpi", methods=["POST"])
@jwt_required()
def handle_all_access_kpi():
    return process_request(all_access_kpi.main)


@app.route("/health_index", methods=["POST"])
@jwt_required()
def handle_health_index():
    return process_request(health_index.main)


# ================= COMMON PROCESS FUNCTION =================
def process_request(function_to_call):
    try:
        incoming_data = request.get_json(force=True, silent=True)

        if not incoming_data or not isinstance(incoming_data, dict):
            return jsonify({
                "result": "",
                "error": "Invalid or missing JSON data"
            }), 400

        args = {"body": incoming_data}

        processed_data = function_to_call(args, {})

        return jsonify({
            "result": processed_data,
            "error": ""
        }), 200

    except Exception as e:
        return jsonify({
            "result": "",
            "error": str(e) or "An unexpected error occurred."
        }), 500


# ================= HEADERS =================
@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    response.cache_control.must_revalidate = True
    return response


# ================= RUN APP =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=False)