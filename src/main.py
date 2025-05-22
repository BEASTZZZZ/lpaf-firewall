from flask import Flask, request, jsonify
from core.detection import is_prompt_safe
from utils.logger import log_prompt

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ LPAF Firewall is running!"

@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    prompt = data.get("prompt", "")

    if is_prompt_safe(prompt):
        log_prompt(prompt, "safe")
        return jsonify({
            "status": "safe",
            "message": "Prompt accepted.",
            "prompt": prompt
        }), 200
    else:
        log_prompt(prompt, "blocked")
        return jsonify({
            "status": "blocked",
            "message": "🚫 Prompt blocked due to injection risk."
        }), 403

if __name__ == "__main__":
    app.run(debug=True)