from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime
from config import PORT

app = Flask(__name__, static_folder='dashboard')
CORS(app)

CONFIG_FILE = "config.json"
LOGS_FILE = "logs.json"
STATUS_FILE = "status.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"contacts": []}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

@app.route("/")
def index():
    return send_from_directory('dashboard', 'index.html')

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory('dashboard', filename)

@app.route("/api/config", methods=["GET"])
def get_config():
    return jsonify(load_config())

@app.route("/api/config", methods=["PUT"])
def update_config():
    config = request.json
    save_config(config)
    return jsonify({"status": "ok"})

@app.route("/api/contacts", methods=["GET"])
def get_contacts():
    config = load_config()
    return jsonify(config.get("contacts", []))

@app.route("/api/contacts", methods=["POST"])
def add_contact():
    config = load_config()
    contact = request.json
    contact["id"] = str(len(config.get("contacts", [])) + 1)
    config.setdefault("contacts", []).append(contact)
    save_config(config)
    return jsonify(contact)

@app.route("/api/contacts/<contact_id>", methods=["PUT"])
def update_contact(contact_id):
    config = load_config()
    for i, c in enumerate(config.get("contacts", [])):
        if c.get("id") == contact_id:
            config["contacts"][i] = request.json
            save_config(config)
            return jsonify({"status": "ok"})
    return jsonify({"error": "not found"}), 404

@app.route("/api/contacts/<contact_id>", methods=["DELETE"])
def delete_contact(contact_id):
    config = load_config()
    config["contacts"] = [c for c in config.get("contacts", []) if c.get("id") != contact_id]
    save_config(config)
    return jsonify({"status": "ok"})

@app.route("/api/logs", methods=["GET"])
def get_logs():
    if os.path.exists(LOGS_FILE):
        with open(LOGS_FILE, "r") as f:
            return jsonify(json.load(f))
    return jsonify([])

@app.route("/api/logs", methods=["DELETE"])
def clear_logs():
    with open(LOGS_FILE, "w") as f:
        json.dump([], f)
    return jsonify({"status": "ok"})

@app.route("/api/status", methods=["GET"])
def get_status():
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r") as f:
                status = json.load(f)
            last_update = datetime.fromisoformat(status.get("timestamp", ""))
            age = (datetime.now() - last_update).total_seconds()
            if age > 30:
                return jsonify({"connected": False, "stale": True})
            return jsonify(status)
        except:
            pass
    return jsonify({"connected": False})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=False)
