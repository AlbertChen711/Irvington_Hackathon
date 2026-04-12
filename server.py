from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS
import os
import re
import hashlib

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _format_numbers(numbers):
    return ", ".join(str(number) for number in numbers)


def _seed_for(question, category, answer):
    basis = f"{question}|{category}|{answer}".encode("utf-8", errors="ignore")
    digest = hashlib.sha256(basis).digest()
    return digest[0]


def _pick_variant(question, category, answer, variants):
    if not variants:
        return ""
    return variants[_seed_for(question, category, answer) % len(variants)]


def _join_hint_lines(lines):
    return "\n".join(line for line in lines if line)


def _general_hint(category_text):
    if category_text == "addition":
        return _pick_variant("general", category_text, "", [
            "General strategy: add one place value at a time and watch for carrying.",
            "General strategy: break each number into tens and ones before combining them.",
            "General strategy: check that your sum is bigger than both numbers you started with."
        ])
    if category_text == "subtraction":
        return _pick_variant("general", category_text, "", [
            "General strategy: count up from the smaller number or regroup if the top digit is too small.",
            "General strategy: subtract the ones place first, then adjust the tens if needed.",
            "General strategy: make sure your answer is smaller than the starting number."
        ])
    if category_text == "multiplication":
        return _pick_variant("general", category_text, "", [
            "General strategy: think in equal groups, repeated addition, or arrays.",
            "General strategy: skip-count by one factor until you have all the groups.",
            "General strategy: check both factors so you know how many groups and how many items are in each group."
        ])
    if category_text == "algebra":
        return _pick_variant("general", category_text, "", [
            "General strategy: keep the equation balanced and undo operations step by step.",
            "General strategy: isolate the variable by doing the opposite operation to both sides.",
            "General strategy: verify your answer by plugging it back into the equation."
        ])
    if category_text == "geometry":
        return _pick_variant("general", category_text, "", [
            "General strategy: sketch the shape, label the values, and choose the matching formula.",
            "General strategy: decide whether the question asks for area, perimeter, or a circle formula.",
            "General strategy: use the known measurements first, then fill in the missing one."
        ])
    return _pick_variant("general", category_text, "", [
        "General strategy: identify the operation, write down the key numbers, and solve in small steps.",
        "General strategy: break the problem into parts, solve the easiest part first, then combine the results.",
        "General strategy: estimate first so you can check whether your final answer makes sense."
    ])


def _specific_hint(question_text, category_text, numbers):
    lower_question = question_text.lower()

    equation_match = re.search(r"\b(-?\d+)\s*([+\-*/×x])\s*(-?\d+)\b", lower_question)
    if equation_match:
        left_number = int(equation_match.group(1))
        operator = equation_match.group(2)
        right_number = int(equation_match.group(3))

        if operator == "+":
            return _pick_variant(question_text, category_text, "", [
                f"Specific hint: add {left_number} and {right_number} by combining the ones first, then carry any extra ten.",
                f"Specific hint: split {right_number} into tens and ones so you can add it to {left_number} more easily.",
                f"Specific hint: make a friendly number if you can, then finish the remaining addends."
            ])
        if operator == "-":
            return _pick_variant(question_text, category_text, "", [
                f"Specific hint: if the top ones digit is smaller than the bottom one, regroup before subtracting.",
                f"Specific hint: count up from the smaller number to the bigger one to see the difference.",
                f"Specific hint: subtract the ones place first, then handle the tens place."
            ])
        if operator in ("x", "×", "*"):
            return _pick_variant(question_text, category_text, "", [
                f"Specific hint: treat {left_number} and {right_number} as equal groups and use repeated addition.",
                f"Specific hint: skip-count by one factor {right_number} times or by the other factor {left_number} times.",
                f"Specific hint: draw an array or set of groups so you can count without missing any items."
            ])
        if operator == "/":
            return _pick_variant(question_text, category_text, "", [
                f"Specific hint: think of {left_number} ÷ {right_number} as sharing or grouping evenly.",
                f"Specific hint: ask how many groups of {right_number} fit into {left_number}.",
                f"Specific hint: if it does not divide evenly, check whether the problem wants a remainder or a fraction."
            ])

    if re.search(r"\b[xy]\s*[+\-*/=]", lower_question) or re.search(r"[+\-*/=]\s*[xy]\b", lower_question):
        if "=" in lower_question:
            return _pick_variant(question_text, category_text, "", [
                "Specific hint: isolate the variable by undoing the operation that is touching it first.",
                "Specific hint: do the same inverse operation to both sides so the equation stays balanced.",
                "Specific hint: once the variable is alone, check your result by substituting it back in."
            ])
        return _pick_variant(question_text, category_text, "", [
            "Specific hint: identify what operation is being done to the variable, then reverse it.",
            "Specific hint: keep the variable on one side and move the other numbers away in the opposite way.",
            "Specific hint: if there are multiple steps, undo them in reverse order."
        ])

    if any(word in lower_question for word in ["how many more", "difference", "left", "in all", "altogether", "each", "groups of", "shared equally"]):
        if any(word in lower_question for word in ["how many more", "difference", "left"]):
            return _pick_variant(question_text, category_text, "", [
                "Specific hint: this sounds like a subtraction question, so look for what is being taken away or compared.",
                "Specific hint: start from the larger amount and count down or count up to find the change.",
                "Specific hint: pay attention to which number is the starting amount and which is the amount being removed."
            ])
        if any(word in lower_question for word in ["in all", "altogether"]):
            return _pick_variant(question_text, category_text, "", [
                "Specific hint: 'in all' or 'altogether' usually means add the quantities together.",
                "Specific hint: identify each amount, then combine them one step at a time.",
                "Specific hint: if there are several parts, add them in an easy order to avoid mistakes."
            ])
        if any(word in lower_question for word in ["each", "groups of"]):
            return _pick_variant(question_text, category_text, "", [
                "Specific hint: 'each' and 'groups of' usually point to multiplication.",
                "Specific hint: multiply the number of groups by the number in each group.",
                "Specific hint: draw the groups if that makes the counting clearer."
            ])
        if "shared equally" in lower_question:
            return _pick_variant(question_text, category_text, "", [
                "Specific hint: 'shared equally' usually means division.",
                "Specific hint: ask how many are in each group or how many groups you can make.",
                "Specific hint: if there is a remainder, check whether the problem expects one."
            ])

    if category_text == "geometry":
        if "area" in lower_question and ("rectangle" in lower_question or "square" in lower_question):
            return _pick_variant(question_text, category_text, "", [
                "Specific hint: area of a rectangle or square is length times width.",
                "Specific hint: multiply the side lengths that are given, and make sure the units are squared.",
                "Specific hint: if one side is missing, use the other information in the problem to find it first."
            ])
        if "perimeter" in lower_question:
            return _pick_variant(question_text, category_text, "", [
                "Specific hint: perimeter means adding all the outer sides.",
                "Specific hint: count every side around the shape, including repeated sides when the shape is closed.",
                "Specific hint: if one side is unknown, use the perimeter formula or the other side lengths to find it."
            ])
        if "circle" in lower_question or "radius" in lower_question or "diameter" in lower_question:
            return _pick_variant(question_text, category_text, "", [
                "Specific hint: circles usually need you to choose between radius, diameter, area, or circumference.",
                "Specific hint: check whether the given measurement is the radius or the diameter before using the formula.",
                "Specific hint: remember that diameter is twice the radius."
            ])

    if any(token in lower_question for token in ["fraction", "numerator", "denominator"]):
        return _pick_variant(question_text, category_text, "", [
            "Specific hint: if the fractions are being added or subtracted, make the denominators the same first.",
            "Specific hint: if the problem is multiplication, multiply the numerators and denominators straight across.",
            "Specific hint: simplify your fraction at the end so the final answer is in lowest terms."
        ])

    if any(token in lower_question for token in ["decimal", "."]):
        return _pick_variant(question_text, category_text, "", [
            "Specific hint: line up decimal points before adding or subtracting.",
            "Specific hint: keep track of place value so tenths, hundredths, and thousandths stay aligned.",
            "Specific hint: if multiplying by 10, 100, or 1000, move the decimal the same number of places."
        ])

    if any(token in lower_question for token in ["percent", "%"]):
        return _pick_variant(question_text, category_text, "", [
            "Specific hint: convert the percent to a decimal or fraction before you calculate.",
            "Specific hint: percent means 'out of 100,' so use that to set up the problem.",
            "Specific hint: if this is a discount or increase, find the percent amount first, then apply it to the whole."
        ])

    if numbers:
        return _pick_variant(question_text, category_text, "", [
            f"Specific hint: the important numbers are {_format_numbers(numbers)}. Figure out which operation connects them.",
            f"Specific hint: use {_format_numbers(numbers)} to decide whether you should add, subtract, multiply, or divide.",
            "Specific hint: write the numbers in the order they appear and solve the smallest step first."
        ])

    return _pick_variant(question_text, category_text, "", [
        "Specific hint: read the wording carefully and look for clue words like 'in all,' 'left,' 'each,' or 'shared equally'.",
        "Specific hint: if the operation is not obvious, rewrite the question in simpler words before solving.",
        "Specific hint: identify the known values, decide what is being asked, and solve one step at a time."
    ])


def generate_hint(question, category="", answer=""):
    question_text = str(question or "").strip()
    category_text = str(category or "").lower().strip()
    lower_question = question_text.lower()
    numbers = [int(value) for value in re.findall(r"-?\d+", question_text)]
    stripped_answer = str(answer or "").strip()

    if not question_text:
        return "Read the problem carefully, find the numbers or operation, and solve it one step at a time."

    general_hint = _general_hint(category_text)
    specific_hint = _specific_hint(question_text, category_text, numbers)

    if specific_hint:
        return _join_hint_lines([general_hint, specific_hint])

    if category_text == "addition" or "+" in question_text:
        if len(numbers) >= 2:
            first, second = numbers[0], numbers[1]
            variants = [
                _join_hint_lines([
                    f"Step 1: Break {first} and {second} into tens and ones.",
                    "Step 2: Add the tens first, then the ones.",
                    "Step 3: Combine the partial sums to get the final total."
                ]),
                _join_hint_lines([
                    f"Start by making a friendly number with {first} or {second}.",
                    "Then add the leftover pieces separately.",
                    "That keeps the total easier to track in your head."
                ]),
                _join_hint_lines([
                    f"Use the numbers {first} and {second} as two parts of one total.",
                    "Add one place value at a time instead of all at once.",
                    "Check that your final answer is bigger than both addends."
                ])
            ]
            return _pick_variant(question_text, category_text, stripped_answer, variants)
        return _pick_variant(question_text, category_text, stripped_answer, [
            "Look for the two addends, split one into tens and ones, and add each part separately.",
            "Add the ones first, then the tens. If the ones make 10 or more, carry the extra into the tens place.",
            "Try using a number line or breaking one number into smaller chunks to make the sum easier."
        ])

    if category_text == "subtraction" or "-" in question_text:
        if len(numbers) >= 2:
            bigger = max(numbers[0], numbers[1])
            smaller = min(numbers[0], numbers[1])
            variants = [
                _join_hint_lines([
                    f"Start at {smaller} and count up to {bigger}.",
                    "The number of steps you take is the difference.",
                    "This is often easier than trying to subtract all at once."
                ]),
                _join_hint_lines([
                    f"Borrow or count up using {smaller} and {bigger}.",
                    "Subtract the ones place first, then check if the tens need adjusting.",
                    "Make sure your answer is smaller than the number you started with."
                ]),
                _join_hint_lines([
                    f"Use {bigger} as your starting point and walk backward to {smaller}.",
                    "Or count forward from the smaller number until you hit the bigger one.",
                    "Both methods should give the same difference."
                ])
            ]
            return _pick_variant(question_text, category_text, stripped_answer, variants)
        return _pick_variant(question_text, category_text, stripped_answer, [
            "Think of subtraction as counting up from the smaller number to the bigger one.",
            "If the numbers are close, count forward step by step to find the difference.",
            "Check whether you need to regroup before subtracting each place value."
        ])

    if category_text == "multiplication" or "x" in lower_question or "*" in question_text:
        if len(numbers) >= 2:
            a, b = numbers[0], numbers[1]
            variants = [
                _join_hint_lines([
                    f"Treat {a} × {b} as repeated addition.",
                    f"That means {a} groups of {b} or {b} groups of {a}.",
                    "Count each group carefully so you do not skip any."
                ]),
                _join_hint_lines([
                    f"Use skip-counting by {a} or by {b}.",
                    "Write out the groups if it helps you stay organized.",
                    "The product should grow faster than addition because you are making groups."
                ]),
                _join_hint_lines([
                    f"Think of {a} × {b} as a rectangle with {a} rows and {b} columns.",
                    "Count one row or one column at a time.",
                    "Arrays are a great way to avoid missing a factor."
                ])
            ]
            return _pick_variant(question_text, category_text, stripped_answer, variants)
        return _pick_variant(question_text, category_text, stripped_answer, [
            "Use repeated addition or skip-counting to build the product one group at a time.",
            "Think of multiplication as equal groups, arrays, or jumps on a number line.",
            "If you know one factor, count by that number until you have the right number of groups."
        ])

    if category_text == "algebra" or any(symbol in lower_question for symbol in ["=", "x", "y"]):
        algebra_variants = [
            _join_hint_lines([
                "Isolate the variable by undoing the operations around it one layer at a time.",
                "Whatever is added, subtract it; whatever is multiplied, divide it.",
                "Keep the equation balanced on both sides."
            ]),
            _join_hint_lines([
                "Find what is happening to the variable first.",
                "Then use the inverse operation to move everything else away from it.",
                "Do the same thing to both sides so the equation stays balanced."
            ]),
            _join_hint_lines([
                "Treat the variable like a mystery number.",
                "Your job is to undo each operation until only the variable is left.",
                "Check your solution by plugging it back into the equation."
            ])
        ]
        return _pick_variant(question_text, category_text, stripped_answer, algebra_variants)

    if category_text == "geometry" or any(word in lower_question for word in ["area", "perimeter", "radius", "diameter", "circle", "triangle", "rectangle"]):
        if "area" in lower_question and ("rectangle" in lower_question or "square" in lower_question):
            if len(numbers) >= 2:
                return _pick_variant(question_text, category_text, stripped_answer, [
                    f"Area = length × width, so multiply the two side lengths {numbers[0]} and {numbers[1]}.",
                    f"Take the two side measurements and multiply them to get the area.",
                    f"For a rectangle or square, area is one side times the other side."
                ])
            return "Area of a rectangle or square is length × width. Multiply the side lengths carefully."
        if "perimeter" in lower_question:
            return _pick_variant(question_text, category_text, stripped_answer, [
                "Perimeter means add all the side lengths together. Watch for any missing side labels.",
                "Walk around the shape and add each edge length one by one.",
                "If a side is repeated, make sure you count it the correct number of times."
            ])
        if "circle" in lower_question or "radius" in lower_question or "diameter" in lower_question:
            return _pick_variant(question_text, category_text, stripped_answer, [
                "For circles, remember the radius, diameter, and π relationship. Check whether the problem wants area or circumference.",
                "Identify whether the question uses radius or diameter before choosing the formula.",
                "Circle problems usually need π, so read carefully and match the formula to what is being asked."
            ])
        return _pick_variant(question_text, category_text, stripped_answer, [
            "Draw the shape and label the sides first. Then choose the formula that matches the shape and what it asks for.",
            "Mark the known measurements on the figure before you calculate anything.",
            "Geometry is easier when you sketch the shape and decide whether the problem asks for area, perimeter, or another measurement."
        ])

    if any(token in lower_question for token in ["fraction", "/", "numerator", "denominator"]):
        return _pick_variant(question_text, category_text, stripped_answer, [
            "For fractions, make sure the denominators match before adding or subtracting. If they do not match, find a common denominator first.",
            "Multiply fractions straight across, but add or subtract only after making the denominators the same.",
            "If the fraction is improper, rewrite it carefully and simplify at the end."
        ])

    if any(token in lower_question for token in ["decimal", "."]):
        return _pick_variant(question_text, category_text, stripped_answer, [
            "Line up the decimal points before you add or subtract. That keeps the place values in the right columns.",
            "For decimals, think in place value: tenths, hundredths, and thousandths.",
            "Move the decimal the same number of places only when multiplying or dividing by powers of 10."
        ])

    if any(token in lower_question for token in ["percent", "%"]):
        return _pick_variant(question_text, category_text, stripped_answer, [
            "Convert the percent to a decimal or fraction first, then multiply by the whole.",
            "Remember that percent means out of 100.",
            "If this is a discount or increase problem, find 10% first and build from there if needed."
        ])

    if numbers:
        return _pick_variant(question_text, category_text, stripped_answer, [
            f"Use the numbers {_format_numbers(numbers)} one step at a time and check each operation before you submit.",
            f"Circle the important numbers {_format_numbers(numbers)} and decide which operation connects them.",
            "Write the problem in smaller pieces, solve the easiest piece first, then combine the results."
        ])

    if stripped_answer:
        return _pick_variant(question_text, category_text, stripped_answer, [
            "Read the problem carefully, identify the operation, and verify the result before attacking.",
            "Solve a small checkpoint first, then use it to finish the whole problem.",
            "If you are unsure, estimate the answer and see whether your final result is reasonable."
        ])

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
