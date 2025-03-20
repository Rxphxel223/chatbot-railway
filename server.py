from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)

# Erlaube NUR deine Webseite
CORS(app, origins=["https://raphaelgafurow.de"])

# OpenAI API-Key aus Umgebungsvariablen holen
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get("question")

    if not question:
        return jsonify({"error": "Keine Frage gestellt"}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Du bist ein Assistent, der Fragen über Raphael beantwortet."},
                      {"role": "user", "content": question}]
        )
        answer = response["choices"][0]["message"]["content"]
        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)