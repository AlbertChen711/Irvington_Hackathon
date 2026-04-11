from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from openai import OpenAI
import json
import os
import traceback

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = os.path.join(BASE_DIR, "OPEN_AI_KEY.txt")


def load_api_key():
    for env_name in ("OPEN_AI_KEY", "OPENAI_API_KEY"):
        env_value = os.getenv(env_name)
        if env_value:
            return env_value.strip()

    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r", encoding="utf-8") as key_file:
            file_value = key_file.read().strip()
            if file_value:
                return file_value

    return None


api_key = load_api_key()
client = OpenAI(api_key=api_key) if api_key else None


@app.route("/ai_status", methods=["GET"])
def ai_status():
    return jsonify({
        "configured": client is not None,
    })


@app.route("/")
def home():
    return send_file(os.path.abspath(os.path.join(BASE_DIR, "..", "index.html")))


@app.route("/hint", methods=["POST"])
def hint():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "")
    category = data.get("category", "Math Problem")

    try:
        if client is None:
            raise RuntimeError("OpenAI client is not configured")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a friendly, encouraging math tutor. Give a short hint "
                        "in 1-2 sentences without revealing the final answer."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Category: {category}\nProblem: {question}\nGive one short helpful hint.",
                },
            ],
            temperature=0.7,
            max_tokens=80,
        )

        raw_text = response.choices[0].message.content.strip()
        parsed = json.loads(raw_text)
        hint_text = str(parsed.get("hint", "")).strip() or "💡 Try one small step at a time."
        return jsonify({"hint": hint_text})
    except Exception as exc:
        print(f"Hint API error: {exc}")
        print(traceback.format_exc())
        return jsonify({
            "hint": "💡 Break the problem into smaller steps. You've got this! 🌟",
            "fallback": True,
        })


@app.route("/question", methods=["POST"])
def question():
    data = request.get_json(silent=True) or {}
    category = data.get("category", "addition")
    difficulty = data.get("difficulty", "easy")
    mode = data.get("mode", "classic")
    turn = data.get("turn", "player")

    try:
        if client is None:
            raise RuntimeError("OpenAI client is not configured")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You create math battle questions. Return ONLY valid JSON with keys "
                        "question, answer, and category. The question should be short and clear. "
                        "The answer must be a number or a simple fraction string like 3/4. "
                        "Do not include markdown or extra text."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Create one {difficulty} {category} question for a {mode} mode turn "
                        f"({turn}). Return JSON only."
                    ),
                },
            ],
            temperature=0.6,
            max_tokens=180,
        )

        raw_text = response.choices[0].message.content.strip()
        payload = json.loads(raw_text)

        question_text = str(payload.get("question", "")).strip()
        answer_value = payload.get("answer", "")
        answer = str(answer_value).strip()
        if not question_text or not answer:
            raise ValueError("OpenAI question response missing question or answer")

        return jsonify({
            "question": question_text,
            "answer": answer,
            "category": category,
            "difficulty": difficulty,
            "mode": mode,
            "turn": turn,
        })
    except Exception as exc:
        print(f"Question API error: {exc}")
        print(traceback.format_exc())
        return jsonify({
            "error": "OpenAI question generation failed",
            "fallback": True,
        }), 500


@app.route("/submit_answer", methods=["POST"])
def submit_answer():
    data = request.get_json(silent=True) or {}
    answer = data.get("answer", "")
    print(f"Answer submitted: {answer}")
    return jsonify({"success": True, "message": "Answer received."})


if __name__ == "__main__":
    app.run(port=5000, debug=False)
