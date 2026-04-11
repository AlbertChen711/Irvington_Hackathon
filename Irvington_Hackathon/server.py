from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from openai import OpenAI
import traceback
import os
app = Flask(__name__)
CORS(app)

# Initialize OpenAI client with your API key
client = OpenAI(api_key=os.getenv("OPEN_AI_KEY"))

# Track the current question to prevent duplicate submissions
current_question_id = None

@app.route("/")
def home():
    return send_file("index.html")

@app.route("/hint", methods=["POST"])\ndef hint():
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

@app.route("/submit_answer", methods=["POST"])\ndef submit_answer():
    global current_question_id
    data = request.get_json()
    question_id = data.get("question_id")
    answer = data.get("answer", "")
    
    # Check if this is the same question being submitted again
    if question_id == current_question_id:
        return jsonify({"error": "Already submitted for this question. Waiting for next question..."}), 400
    
    # Update the current question ID
    current_question_id = question_id
    
    print(f"Answer submitted for question {question_id}: {answer}")
    
    # Process the answer (your existing logic here)
    return jsonify({"success": True, "message": "Answer submitted! Loading next question..."})

@app.route("/next_question", methods=["POST"])\ndef next_question():
    global current_question_id
    # Reset the question ID when a new question is loaded
    current_question_id = None
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(port=5000, debug=False)