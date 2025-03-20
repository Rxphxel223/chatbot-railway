import openai
import os
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
import tempfile  # Wichtig für stabilen Speicherort

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default-secret")

# 🛠 FIX: Persistente Flask-Sessions
SESSION_DIR = tempfile.mkdtemp()  # Stellt sicher, dass die Session stabil gespeichert bleibt
app.config["SESSION_FILE_DIR"] = SESSION_DIR
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

CORS(app, supports_credentials=True)

openai.api_key = os.getenv("OPENAI_API_KEY")
LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD", "fallback-passwort")

@app.route('/')
def home():
    return "API läuft!", 200

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if data.get("password") == LOGIN_PASSWORD:
        session["logged_in"] = True
        session.modified = True  # Speichert die Session sofort
        return jsonify({"message": "Erfolgreich eingeloggt"}), 200
    return jsonify({"error": "Falsches Passwort"}), 403

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Erfolgreich ausgeloggt"}), 200

@app.route('/ask', methods=['POST'])
def ask():
    print("🔍 /ask wurde aufgerufen")
    if not session.get("logged_in"):
        print("❌ Nicht eingeloggt")
        return jsonify({"error": "Nicht eingeloggt"}), 403

    data = request.json
    print("📩 Eingehende Anfrage:", data)  

    if not data or "question" not in data:
        print("❌ Fehler: Keine Frage gesendet")
        return jsonify({"error": "Keine Frage gestellt"}), 400

    question = data.get("question")
    try:
        print("🎯 Anfrage an OpenAI wird gesendet...")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Du bist ein Assistent, der Fragen über Raphael beantwortet."},
                      {"role": "user", "content": question}]
        )
        answer = response.choices[0].message.content  
        print("✅ OpenAI Antwort:", answer)  

        return jsonify({"answer": answer})

    except Exception as e:
        print("❌ OpenAI Fehler:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
