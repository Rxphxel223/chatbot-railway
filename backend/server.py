from flask import Flask, request, jsonify

app = Flask(__name__)

# 🔒 API-Startseite blockieren
@app.route('/')
def home():
    return "403 Forbidden", 403

# 🔒 API nur für POST-Anfragen erlauben
@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    
    if not data or "question" not in data:
        return jsonify({"error": "Fehlende Frage"}), 400
    
    return jsonify({"answer": f"Ich habe deine Frage gehört: {data['question']}"})

# 🔒 Debug-Modus deaktivieren
if __name__ == '__main__':
    app.run(debug=False)
