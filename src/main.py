from flask import Flask, request, jsonify
from core.detection import is_prompt_safe, get_prompt_risk_score
from utils.logger import log_prompt

app = Flask(__name__)

@app.route('/')
def home():
    return "LPAF Firewall with risk scoring is running!"

@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    prompt = data.get("prompt", "")

    # Get risk score
    score = get_prompt_risk_score(prompt)

    if score < 50:
        log_prompt(prompt, "safe")
        return jsonify({
            "status": "safe",
            "message": "Prompt accepted.",
            "prompt": prompt,
            "risk_score": score
        }), 200
    else:
        log_prompt(prompt, "blocked")
        return jsonify({
            "status": "blocked",
            "message": "Prompt blocked due to injection risk.",
            "prompt": prompt,
            "risk_score": score
        }), 403

if __name__ == "__main__":
    app.run(debug=True)