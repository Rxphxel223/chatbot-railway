
from flask import Flask, request, jsonify, session, send_file
from flask_cors import CORS
from flask_session import Session
from datetime import datetime
import tempfile
import openai
import os
import json
import time

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default-secret")

SESSION_DIR = tempfile.mkdtemp()
app.config["SESSION_FILE_DIR"] = SESSION_DIR
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_COOKIE_HTTPONLY"] = False
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = True
Session(app)

CORS(app, supports_credentials=True)

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-3.5-turbo"
FRAGEN_LOG_DATEI = os.path.join(tempfile.gettempdir(), "fragen_log.txt")

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

LOGIN_PASSWORDS = {
    os.getenv("LOGIN_PASSWORD_1"): "Benutzer 1",
    os.getenv("LOGIN_PASSWORD_2"): "Benutzer 2",
    os.getenv("LOGIN_PASSWORD_3"): "Benutzer 3"
}
LOGIN_PASSWORD_ADMIN = os.getenv("LOGIN_PASSWORD_ADMIN")

@app.route('/')
def home():
    return "API läuft!", 200

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    password = data.get("password")

    attempts = session.get('login_attempts', 0)

    if attempts >= 3:
        time.sleep(5)

    if password == LOGIN_PASSWORD_ADMIN:
        session["logged_in"] = True
        session["user_identifier"] = "Admin"
        session["is_admin"] = True
        session["login_attempts"] = 0
        session.modified = True
        return jsonify({"message": "Erfolgreich als Admin eingeloggt"}), 200

    elif password in LOGIN_PASSWORDS:
        session["logged_in"] = True
        session["user_identifier"] = LOGIN_PASSWORDS[password]
        session["is_admin"] = False
        session["login_attempts"] = 0
        session.modified = True
        return jsonify({"message": "Erfolgreich eingeloggt"}), 200

    else:
        session["login_attempts"] = attempts + 1
        session.modified = True
        return jsonify({"error": "Falsches Passwort"}), 403

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Erfolgreich ausgeloggt"}), 200

@app.route('/ask', methods=['POST'])
def ask():
    print("🔍 /ask wurde aufgerufen")
    print("📂 Session Inhalt:", session)

    if not session.get("logged_in"):
        print("❌ Nicht eingeloggt")
        return jsonify({"error": "Nicht eingeloggt"}), 403

    if "question_count" not in session:
        session["question_count"] = 0

    is_admin = session.get("is_admin", False)

    if not is_admin and session["question_count"] >= 10:
        return jsonify({"error": "Du hast die maximale Anzahl an Fragen erreicht."}), 429

    data = request.json
    print("📩 Eingehende Anfrage:", data)

    if not data or "question" not in data:
        print("❌ Fehler: Keine Frage gestellt")
        return jsonify({"error": "Keine Frage gestellt"}), 400

    question = data.get("question")

    user_identifier = session.get("user_identifier", "Unbekannt")
    try:
        with open(FRAGEN_LOG_DATEI, "a", encoding="utf-8") as log_file:
            log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {user_identifier}: {question}\n")
    except Exception as e:
        print(f"⚠️ Fehler beim Loggen der Frage: {e}")

    messages = [{"role": "system", "content": SYSTEM_MESSAGE}]
    messages.extend(load_personal_context())
    messages.append({"role": "user", "content": question})

    try:
        openai_response = openai.ChatCompletion.create(
            model=MODEL,
            messages=messages
        )
        answer = openai_response.choices[0].message.content
        print("✅ Antwort vom Modell:", answer)

        if not is_admin:
            session["question_count"] += 1
            session.modified = True
        
        return jsonify({"answer": answer})

    except Exception as e:
        print("❌ Fehler bei Anfrage an OpenAI:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route(f'/show-logs-{os.getenv("LOG_SECRET_CODE")}', methods=['GET'])
def show_logs():
    if not session.get("logged_in"):
        return jsonify({"error": "Nicht eingeloggt"}), 403

    if os.path.exists(FRAGEN_LOG_DATEI):
        return send_file(FRAGEN_LOG_DATEI, mimetype='text/plain')
    else:
        return jsonify({"error": "Keine Logs vorhanden"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
