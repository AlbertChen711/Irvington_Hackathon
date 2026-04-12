from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS
from openai import OpenAI
import json
import os
import traceback

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_CANDIDATES = [
    os.path.join(BASE_DIR, "OPEN_AI_KEY.txt"),
    os.path.join(BASE_DIR, "Irvington_Hackathon", "OPEN_AI_KEY.txt"),
]


def load_api_key():
    for env_name in ("OPEN_AI_KEY", "OPENAI_API_KEY"):
        env_value = os.getenv(env_name)
        if env_value:
            return env_value.strip()

    for key_file in KEY_CANDIDATES:
        if os.path.exists(key_file):
            with open(key_file, "r", encoding="utf-8") as file:
                file_value = file.read().strip()
                if file_value and not file_value.startswith("SET_YOUR_OPENAI_API_KEY"):
                    return file_value

    return None


api_key = load_api_key()
client = OpenAI(api_key=api_key) if api_key else None


@app.route("/")
def home():
    return send_file(os.path.join(BASE_DIR, "index.html"))


@app.route("/<path:requested_path>")
def static_files(requested_path):
    absolute_path = os.path.abspath(os.path.join(BASE_DIR, requested_path))
    if not absolute_path.startswith(BASE_DIR):
        abort(404)
    if not os.path.isfile(absolute_path):
        abort(404)
    return send_file(absolute_path)


@app.route("/ai_status", methods=["GET"])
def ai_status():
    return jsonify({"configured": client is not None})


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
                        "Return JSON only with key 'hint'. Give one short, supportive hint "
                        "without revealing the final answer."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Category: {category}\nProblem: {question}",
                },
            ],
            temperature=0.7,
            max_tokens=100,
        )

        raw_text = response.choices[0].message.content.strip()
        parsed = json.loads(raw_text)
        hint_text = str(parsed.get("hint", "")).strip() or "💡 Try one step at a time."
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
                        "Return JSON only with keys: question and answer. "
                        "Question should be a short math prompt. "
                        "Answer should be a number or simple fraction string."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Create one {difficulty} {category} question for {mode} mode, {turn} turn."
                    ),
                },
            ],
            temperature=0.6,
            max_tokens=180,
        )

        raw_text = response.choices[0].message.content.strip()
        parsed = json.loads(raw_text)

        question_text = str(parsed.get("question", "")).strip()
        answer = str(parsed.get("answer", "")).strip()
        if not question_text or not answer:
            raise ValueError("Question payload missing fields")

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
        return jsonify({"error": "OpenAI question generation failed", "fallback": True}), 500


if __name__ == "__main__":
    app.run(port=5000, debug=False)
