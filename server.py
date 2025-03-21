import openai
import os
import pandas as pd
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
import tempfile  # WICHTIG: Sicherstellen, dass Flask die Session speichert!

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default-secret")

# 🛠 FIX: Stabile Session-Speicherung auf Render
SESSION_DIR = tempfile.mkdtemp()  # Temporäres Verzeichnis für Sessions
app.config["SESSION_FILE_DIR"] = SESSION_DIR
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_COOKIE_HTTPONLY"] = False  # WICHTIG: Muss für JavaScript deaktiviert sein!
app.config["SESSION_COOKIE_SAMESITE"] = "None"  # WICHTIG für CORS-Cookies!
app.config["SESSION_COOKIE_SECURE"] = True  # Muss auf True sein, wenn HTTPS genutzt wird
Session(app)

CORS(app, supports_credentials=True)

openai.api_key = os.getenv("OPENAI_API_KEY")
LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD", "fallback-passwort")

# 📌 1️⃣ Fragenkatalog laden (als Kontext für OpenAI)
file_path = "/mnt/data/fragenkatalog.xlsx"
df = pd.read_excel(file_path)

# 🔥 2️⃣ Erstelle eine Zusammenfassung deines Wissens aus der Datei
def generate_personal_context():
    context = "Hier sind einige Fakten über Raphael Gafurow:\n"
    for _, row in df.iterrows():
        context += f"- {row['Frage']}: {row['Antwort']}\n"
    context += "\nAntworte immer so, als wärst du ein guter Freund von Raphael."
    return context


@app.route('/')
def home():
    return "API läuft!", 200

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if data.get("password") == LOGIN_PASSWORD:
        session["logged_in"] = True
        session.modified = True  # 🛠 FIX: Session wird direkt gespeichert
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
        print("❌ Fehler: Keine Frage gesendet")
        return jsonify({"error": "Keine Frage gestellt"}), 400

    question = data.get("question")
    try:
        openai_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": personal_context},  # Dein Wissen als Kontext
                {"role": "user", "content": question}
            ]
        )
        answer = response.choices[0].message.content  
        print("✅ OpenAI Antwort:", answer)  

        return jsonify({"answer": answer})

    except Exception as e:
        print("❌ OpenAI Fehler:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
