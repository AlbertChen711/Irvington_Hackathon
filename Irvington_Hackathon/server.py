from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from openai import OpenAI
import traceback
import os
app = Flask(__name__)
CORS(app)

# Initialize OpenAI client with your API key
client = OpenAI(api_key=os.getenv("OPEN_AI_KEY"))

@app.route("/")
def home():
    return send_file("index.html")

@app.route("/hint", methods=["POST"])
def hint():
    data = request.get_json()
    question = data.get("question", "")
    answer = data.get("answer", "")
    category = data.get("category", "Math Problem")

    try:
        # Use OpenAI API to generate an encouraging, specific hint
        print(f"Requesting hint for: {question} (Category: {category})")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a friendly, encouraging math tutor. Give SHORT hints (max 2 sentences) without revealing the answer. Use emojis and be supportive!"
                },
                {
                    "role": "user",
                    "content": f"{category} problem: {question}\nGive a hint to help solve it. Be brief!"
                }
            ],
            temperature=0.7,
            max_tokens=80
        )
        
        hint_text = response.choices[0].message.content
        print(f"API Success: {hint_text}")
    except Exception as e:
        # Fallback to mock hints if API fails
        print(f"API Error occurred: {str(e)}")
        print(traceback.format_exc())
        hint_text = f"💡 Break the problem into smaller steps. You've got this! 🌟"

    return jsonify({"hint": hint_text})

if __name__ == "__main__":
    app.run(port=5000, debug=False)