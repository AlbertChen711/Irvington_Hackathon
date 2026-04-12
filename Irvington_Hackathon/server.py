from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from openai import OpenAI
import os
import traceback

app = Flask(__name__)
CORS(app)

# ---- CONFIG ----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_api_key():
    return os.getenv("OPENAI_API_KEY")

api_key = load_api_key()

if not api_key:
    print("⚠️ WARNING: OPENAI_API_KEY not set!")

client = OpenAI(api_key=api_key) if api_key else None

# ---- ROUTES ----

@app.route("/ai_status", methods=["GET"])
def ai_status():
    return jsonify({
        "configured": client is not None,
    })

@app.route("/")
def home():
    return send_file(os.path.join(BASE_DIR, "index.html"))

@app.route("/hint", methods=["POST"])
def hint():
    if client is None:
        return jsonify({
            "hint": "⚠️ AI not configured.",
            "fallback": True
        })

    data = request.get_json() or {}
    question = data.get("question", "")
    category = data.get("category", "Math Problem")

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a friendly math tutor. Give a short 1–2 sentence hint without giving the answer."
                },
                {
                    "role": "user",
                    "content": f"Category: {category}\nProblem: {question}"
                }
            ],
            temperature=0.7,
            max_tokens=80,
        )

        hint_text = response.choices[0].message.content.strip()

        return jsonify({"hint": hint_text})

    except Exception as exc:
        print(exc)
        return jsonify({
            "hint": "💡 Break the problem into smaller steps!",
            "fallback": True
        })