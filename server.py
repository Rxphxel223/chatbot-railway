from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
import tempfile
import openai
import os
import json
import time
import secrets

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-3.5-turbo"
FRAGEN_LOG_DATEI = os.path.join(tempfile.gettempdir(), "fragen_log.txt")

TOKENS = {
    os.getenv("LOGIN_PASSWORD_1"): secrets.token_urlsafe(24),
    os.getenv("LOGIN_PASSWORD_2"): secrets.token_urlsafe(24),
    os.getenv("LOGIN_PASSWORD_3"): secrets.token_urlsafe(24),
}
ADMIN_PASSWORD = os.getenv("LOGIN_PASSWORD_ADMIN")
ADMIN_TOKEN = secrets.token_urlsafe(32)

USER_TOKENS = {v: k for k, v in TOKENS.items()}
USER_TOKENS[ADMIN_TOKEN] = "Admin"

SYSTEM_MESSAGE = (
    "Du bist ein freundlicher, lockerer Assistent und der beste Freund von Raphael Gafurow. "
    "Beantworte Fragen über Raphael ehrlich und informativ, aber sprich niemals so, als wärst du Raphael selbst. "
    "Du weißt viel über Raphael und antwortest aus der Perspektive eines engen Freundes, der ihn gut kennt. "
    "Wenn du etwas nicht weißt, gib es offen zu."
)

WISSENSDATEI_PATH = "/etc/secrets/wissen.jsonl"
def load_personal_context():
    try:
        with open(WISSENSDATEI_PATH, "r", encoding="utf-8") as f:
            messages = [json.loads(line)["messages"] for line in f if line.strip()]
            return [msg for sublist in messages for msg in sublist]
    except Exception as e:
        print(f"⚠️ Kontext konnte nicht geladen werden: {e}")
        return [{"role": "system", "content": "Ich bin ein persönlicher Assistent von Raphael Gafurow."}]

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    password = data.get("password")

    if password == ADMIN_PASSWORD:
        return jsonify({"message": "Erfolgreich als Admin eingeloggt", "token": ADMIN_TOKEN}), 200

    elif password in TOKENS:
        return jsonify({"message": "Erfolgreich eingeloggt", "token": TOKENS[password]}), 200

    return jsonify({"error": "Falsches Passwort"}), 403

@app.route("/ask", methods=["POST"])
def ask():
    token = request.headers.get("Authorization")
    user = USER_TOKENS.get(token)

    if not user:
        return jsonify({"error": "Nicht eingeloggt"}), 403

    is_admin = (user == "Admin")
    data = request.json

    if not data or "question" not in data:
        return jsonify({"error": "Keine Frage gestellt"}), 400

    question = data.get("question")

    messages = [{"role": "system", "content": SYSTEM_MESSAGE}]
    messages.extend(load_personal_context())
    messages.append({"role": "user", "content": question})

    try:
        openai_response = openai.ChatCompletion.create(
            model=MODEL,
            messages=messages
        )
        answer = openai_response.choices[0].message.content

        try:
            with open(FRAGEN_LOG_DATEI, "a", encoding="utf-8") as log_file:
                log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {user}:\n")
                log_file.write(f"❓ Frage: {question}\n")
                log_file.write(f"💬 Antwort: {answer}\n")
                log_file.write("-" * 40 + "\n")
        except Exception as log_e:
            print(f"⚠️ Fehler beim Loggen: {log_e}")

        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route(f'/show-logs-{os.getenv("LOG_SECRET_CODE")}', methods=['GET'])
def show_logs():
    token = request.headers.get("Authorization")
    user = USER_TOKENS.get(token)

    if user != "Admin":
        return jsonify({"error": "Nicht autorisiert"}), 403

    if os.path.exists(FRAGEN_LOG_DATEI):
        return send_file(FRAGEN_LOG_DATEI, mimetype='text/plain')
    else:
        return jsonify({"error": "Keine Logs vorhanden"}), 404

@app.route("/")
def home():
    return "API läuft!", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
