import openai
import os
import json
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
from datetime import datetime
import tempfile

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
LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD", "fallback-passwort")
MODEL = "gpt-3.5-turbo"
FRAGEN_LOG_DATEI = "/etc/secrets/fragen_log.txt"

SYSTEM_MESSAGE = (
    "Du bist ein freundlicher, lockerer Assistent und der beste Freund von Raphael Gafurow. "
    "Beantworte Fragen über Raphael ehrlich und informativ, aber sprich niemals so, als wärst du Raphael selbst. "
    "Du weißt viel über Raphael und antwortest aus der Perspektive eines engen Freundes, der ihn gut kennt. "
    "Wenn du etwas nicht weißt, gib es offen zu."
)

# Wissen aus Datei einlesen
WISSENSDATEI_PATH = "/etc/secrets/wissen.jsonl"
def load_personal_context():
    try:
        with open(WISSENSDATEI_PATH, "r", encoding="utf-8") as f:
            messages = [json.loads(line)["messages"] for line in f if line.strip()]
            return [msg for sublist in messages for msg in sublist]  # Flacht zu einer Liste ab
    except Exception as e:
        print(f"⚠️ Kontext konnte nicht geladen werden: {e}")
        return [{"role": "system", "content": "Ich bin ein persönlicher Assistent von Raphael Gafurow."}]

@app.route('/')
def home():
    return "API läuft!", 200

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if data.get("password") == LOGIN_PASSWORD:
        session["logged_in"] = True
        session.modified = True
        return jsonify({"message": "Erfolgreich eingeloggt"}), 200
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

    data = request.json
    print("📩 Eingehende Anfrage:", data)

    if not data or "question" not in data:
        print("❌ Fehler: Keine Frage gestellt")
        return jsonify({"error": "Keine Frage gestellt"}), 400

    question = data.get("question")

    try:
        with open(FRAGEN_LOG_DATEI, "a", encoding="utf-8") as log_file:
            log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {question}\n")
    except Exception as e:
        print(f"⚠️ Fehler beim Loggen der Frage: {e}")

    # System Message – definiert Ton und Rolle des Bots
    messages = [{"role": "system", "content": SYSTEM_MESSAGE}]

    # Wissen laden und als Kontext einfügen
    messages.extend(load_personal_context())

    # Nutzerfrage anhängen
    messages.append({"role": "user", "content": question})

    try:
        openai_response = openai.ChatCompletion.create(
            model=MODEL,
            messages=messages
        )
        answer = openai_response.choices[0].message.content
        print("✅ Antwort vom Modell:", answer)
        return jsonify({"answer": answer})

    except Exception as e:
        print("❌ Fehler bei Anfrage an OpenAI:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
