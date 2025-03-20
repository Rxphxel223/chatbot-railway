import openai
import os
from flask import Flask, request, jsonify, session
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default-secret")  # Lädt SECRET_KEY aus Render
CORS(app, supports_credentials=True)

# OpenAI API-Schlüssel aus Umgebungsvariablen laden
openai.api_key = os.getenv("OPENAI_API_KEY")

# Passwort für den Login aus Umgebungsvariablen
LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD", "fallback-passwort")

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if data.get("password") == LOGIN_PASSWORD:
        session["logged_in"] = True
        return jsonify({"message": "Erfolgreich eingeloggt"}), 200
    return jsonify({"error": "Falsches Passwort"}), 403

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Erfolgreich ausgeloggt"}), 200

@app.route('/ask', methods=['POST'])
def ask():
    if not session.get("logged_in"):
        return jsonify({"error": "Nicht eingeloggt"}), 403

    data = request.json
    question = data.get("question")

    if not question:
        return jsonify({"error": "Keine Frage gestellt"}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Du bist ein Assistent, der Fragen über Raphael beantwortet."},
                {"role": "user", "content": question}
            ]
        )
        answer = response.choices[0].message.content  # ✅ Korrekte Syntax für OpenAI v1.0+
        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
