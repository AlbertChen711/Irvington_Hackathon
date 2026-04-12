from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS
import os
import re

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _format_numbers(numbers):
    return ", ".join(str(number) for number in numbers)


def generate_hint(question, category="", answer=""):
    question_text = str(question or "").strip()
    category_text = str(category or "").lower().strip()
    lower_question = question_text.lower()
    numbers = [int(value) for value in re.findall(r"-?\d+", question_text)]

    if category_text == "addition" or "+" in question_text:
        if len(numbers) >= 2:
            return (
                f"Break {numbers[0]} and {numbers[1]} into tens and ones, then add them separately. "
                f"That makes the math easier to track."
            )
        return "Look for the two addends, split one into tens and ones, and add each part separately."

    if category_text == "subtraction" or "-" in question_text:
        if len(numbers) >= 2:
            bigger = max(numbers[0], numbers[1])
            smaller = min(numbers[0], numbers[1])
            return (
                f"Start at {smaller} and count up to {bigger}. The difference is the answer."
            )
        return "Think of subtraction as counting up from the smaller number to the bigger one."

    if category_text == "multiplication" or "x" in lower_question or "*" in question_text:
        if len(numbers) >= 2:
            return (
                f"Treat {numbers[0]} × {numbers[1]} as repeated addition: {numbers[0]} groups of {numbers[1]}."
            )
        return "Use repeated addition or skip-counting to build the product one group at a time."

    if category_text == "algebra" or any(symbol in lower_question for symbol in ["=", "x", "y"]):
        return (
            "Isolate the variable by doing the opposite operation step by step. Whatever is added, subtract it; "
            "whatever is multiplied, divide it."
        )

    if category_text == "geometry" or any(word in lower_question for word in ["area", "perimeter", "radius", "diameter", "circle", "triangle", "rectangle"]):
        if "area" in lower_question and ("rectangle" in lower_question or "square" in lower_question):
            return "Area of a rectangle or square is length × width. Multiply the side lengths carefully."
        if "perimeter" in lower_question:
            return "Perimeter means add all the side lengths together. Watch for any missing side labels."
        if "circle" in lower_question or "radius" in lower_question or "diameter" in lower_question:
            return "For circles, remember the radius, diameter, and π relationship. Check whether the problem wants area or circumference."
        return "Draw the shape and label the sides first. Then choose the formula that matches the shape and what it asks for."

    if numbers:
        return f"Use the numbers { _format_numbers(numbers) } one step at a time and check each operation before you submit."

    if answer:
        return "Read the problem carefully, identify the operation, and verify the result before attacking."

    return "Break the problem into small steps, solve the easiest part first, then combine your work."


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
    return jsonify({"configured": False})


@app.route("/hint", methods=["POST"])
def hint():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "")
    category = data.get("category", "")
    answer = data.get("answer", "")
    return jsonify({
        "hint": generate_hint(question, category=category, answer=answer)
    })


if __name__ == "__main__":
    app.run(port=5000, debug=True)
