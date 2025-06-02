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

# Konfiguration
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-3.5-turbo"
SYSTEM_MESSAGE = (
    "Du bist ein freundlicher, lockerer Assistent und der beste Freund von Raphael Gafurow. "
    "Beantworte Fragen über Raphael ehrlich und informativ, aber sprich niemals so, als wärst du Raphael selbst. "
    "Du weißt viel über Raphael und antwortest aus der Perspektive eines engen Freundes, der ihn gut kennt. "
    "Wenn du etwas nicht weißt, gib es offen zu."
)

WISSENSDATEI_PATH = "/etc/secrets/wissen.jsonl"
FRAGEN_LOG_DATEI = os.path.join(tempfile.gettempdir(), "fragen_log.txt")

# Umgebungsvariablen für Passwörter
LOGIN_PASSWORDS = {
    os.getenv("LOGIN_PASSWORD_1"): "Benutzer 1",
    os.getenv("LOGIN_PASSWORD_2"): "Benutzer 2",
    os.getenv("LOGIN_PASSWORD_3"): "Benutzer 3"
}
LOGIN_PASSWORD_ADMIN = os.getenv("LOGIN_PASSWORD_ADMIN")
LOG_SECRET_CODE = os.getenv("LOG_SECRET_CODE")

# Token-Speicher
session_tokens = {}

CORS(app, supports_credentials=True, resources={
    r"/*": {"origins": "https://raphaelgafurow.de"}
})

def load_personal_context():
    try:
        with open(WISSENSDATEI_PATH, "r", encoding="utf-8") as f:
            messages = [json.loads(line)["messages"] for line in f if line.strip()]
            return [msg for sublist in messages for msg in sublist]
    except Exception as e:
        print(f"⚠️ Kontext konnte nicht geladen werden: {e}")
        return [{"role": "system", "content": "Ich bin ein persönlicher Assistent von Raphael Gafurow."}]

def get_user_from_token():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split("Bearer ")[1]
    return session_tokens.get(token)

@app.route('/')
def home():
    return "API läuft!", 200

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    password = data.get("password")

    if not password:
        return jsonify({"error": "Kein Passwort angegeben"}), 400

    if password == LOGIN_PASSWORD_ADMIN:
        token = secrets.token_urlsafe(32)
        session_tokens[token] = {
            "user_identifier": "Admin",
            "is_admin": True,
            "question_count": 0
        }
        return jsonify({"token": token})

    elif password in LOGIN_PASSWORDS:
        token = secrets.token_urlsafe(32)
        session_tokens[token] = {
            "user_identifier": LOGIN_PASSWORDS[password],
            "is_admin": False,
            "question_count": 0
        }
        return jsonify({"token": token})

    return jsonify({"error": "Falsches Passwort"}), 403

@app.route('/ask', methods=['POST'])
def ask():
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Nicht eingeloggt"}), 403

    if not user.get("is_admin") and user["question_count"] >= 10:
        return jsonify({"error": "Du hast die maximale Anzahl an Fragen erreicht."}), 429

    data = request.json
    question = data.get("question")
    if not question:
        return jsonify({"error": "Keine Frage gestellt"}), 400

    messages = [{"role": "system", "content": SYSTEM_MESSAGE}]
    messages.extend(load_personal_context())
    messages.append({"role": "user", "content": question})

    try:
        openai_response = openai.ChatCompletion.create(
            model=MODEL,
            messages=messages
        )
        answer = openai_response.choices[0].message.content

        # Logging
        try:
            with open(FRAGEN_LOG_DATEI, "a", encoding="utf-8") as log_file:
                log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {user['user_identifier']}\n")
                log_file.write(f"❓ Frage: {question}\n")
                log_file.write(f"💬 Antwort: {answer}\n")
                log_file.write("-" * 40 + "\n")
        except Exception as log_e:
            print(f"⚠️ Fehler beim Loggen der Frage: {log_e}")

        if not user.get("is_admin"):
            user["question_count"] += 1

        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/festival_kochbuch")Add commentMore actions
def festival_kochbuch():
    return send_file("festival_kochbuch.html")

@app.route("/api/festival_rezept", methods=["POST"])
def festival_rezept():
    items = request.json.get("items", [])
    prompt = f"""Du bist ein Festival-Koch. Nutze nur folgende Zutaten: {', '.join(items)}.
Gib ein einfaches Gericht an, das mit einem Gaskocher zubereitet werden kann."""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        recipe = response.choices[0].message.content
        return jsonify({"recipe": recipe})

    except Exception as e:
        print(f"❌ Fehler bei Rezeptgenerierung: {e}")
        return jsonify({"recipe": f"Fehler: {str(e)}"}), 500

@app.route(f'/show-logs-{LOG_SECRET_CODE}', methods=['GET'])
def show_logs():
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Nicht eingeloggt"}), 403

    if os.path.exists(FRAGEN_LOG_DATEI):
        return send_file(FRAGEN_LOG_DATEI, mimetype='text/plain')
    else:
        return jsonify({"error": "Keine Logs vorhanden"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
