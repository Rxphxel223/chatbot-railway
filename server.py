import openai
import os
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
import tempfile

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default-secret")

# ✅ Session für Render korrekt konfigurieren
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

# ❗ Hier deinen echten Modellnamen eintragen
FINE_TUNED_MODEL = "ft:gpt-3.5-turbo-1106:raphael::BDTAb8wD"

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
        openai_response = openai.ChatCompletion.create(
            model=FINE_TUNED_MODEL,
            messages=[
                {"role": "user", "content": question}
            ]
        )
        answer = openai_response.choices[0].message.content
        print("✅ Antwort vom Modell:", answer)
        return jsonify({"answer": answer})

    except Exception as e:
        print("❌ Fehler bei Anfrage an OpenAI:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
