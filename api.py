from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

CONFIG_FILE = "config.json"

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
    return send_file("index.html")

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
