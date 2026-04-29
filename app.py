from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random

# ----------------------------
# App Config
# ----------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = "prepgen_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///prepgen.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# ----------------------------
# DATABASE MODELS
# ----------------------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))
    exam_selected = db.Column(db.String(50))
    diagnostic_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class DiagnosticResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    quantitative_score = db.Column(db.Integer)
    reasoning_score = db.Column(db.Integer)
    english_score = db.Column(db.Integer)
    total_score = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PracticeResult(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    score = db.Column(db.Integer)
    total = db.Column(db.Integer)
    percentage = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
# ----------------------------
# LOGIN MANAGER
# ----------------------------

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ----------------------------
# HYBRID AI QUESTION ENGINE
# ----------------------------

def generate_options(correct_answer):
    options = [correct_answer]

    while len(options) < 4:
        fake = correct_answer + random.randint(-10, 10)
        if fake != correct_answer and fake not in options:
            options.append(fake)

    random.shuffle(options)
    return options


# ----------------------------
# QUANTITATIVE QUESTIONS
# ----------------------------

def generate_addition_question():
    a = random.randint(10, 100)
    b = random.randint(10, 100)
    answer = a + b

    return {
        "question": f"What is {a} + {b}?",
        "options": generate_options(answer),
        "answer": answer,
        "section": "Quantitative"
    }


def generate_percentage_question():

    price = random.randint(200, 1000)
    discount = random.choice([5, 10, 15, 20])

    discount_amount = price * discount / 100
    final_price = round(price - discount_amount)

    return {
        "question": f"A product costs ₹{price}. A discount of {discount}% is applied. What is the final price?",
        "options": generate_options(final_price),
        "answer": final_price,
        "section": "Quantitative"
    }


def generate_profit_loss_question():

    cost = random.randint(100, 500)
    profit_percent = random.choice([10, 20, 25])

    selling_price = round(cost * (1 + profit_percent / 100))

    return {
        "question": f"A shopkeeper buys an item for ₹{cost} and sells it at {profit_percent}% profit. What is the selling price?",
        "options": generate_options(selling_price),
        "answer": selling_price,
        "section": "Quantitative"
    }


def generate_interest_question():

    principal = random.randint(1000, 5000)
    rate = random.choice([5, 10])
    time = random.randint(1, 5)

    interest = round((principal * rate * time) / 100)

    return {
        "question": f"Find the simple interest on ₹{principal} at {rate}% for {time} years.",
        "options": generate_options(interest),
        "answer": interest,
        "section": "Quantitative"
    }


quant_generators = [
    generate_addition_question,
    generate_percentage_question,
    generate_profit_loss_question,
    generate_interest_question
]


# ----------------------------
# REASONING QUESTIONS
# ----------------------------

def generate_number_series():

    start = random.randint(1, 10)
    diff = random.randint(2, 8)

    series = [start + i * diff for i in range(4)]
    next_value = start + 4 * diff

    return {
        "question": f"Find the next number in the series: {series[0]}, {series[1]}, {series[2]}, {series[3]}, ?",
        "options": generate_options(next_value),
        "answer": next_value,
        "section": "Reasoning"
    }


def generate_odd_one_out():

    base = random.randint(2, 5)
    nums = [base, base*2, base*3, base*4]

    odd = base*5 + random.randint(1,3)

    options = nums[:3] + [odd]
    random.shuffle(options)

    return {
        "question": "Find the odd number out.",
        "options": options,
        "answer": odd,
        "section": "Reasoning"
    }


reasoning_generators = [
    generate_number_series,
    generate_odd_one_out
]


# ----------------------------
# ENGLISH QUESTIONS
# ----------------------------

SYNONYMS = [
    ("happy", "joyful"),
    ("fast", "quick"),
    ("big", "large"),
    ("small", "tiny")
]

ANTONYMS = [
    ("hot", "cold"),
    ("up", "down"),
    ("rich", "poor"),
    ("strong", "weak")
]


def generate_synonym_question():

    word, synonym = random.choice(SYNONYMS)

    options = [synonym]
    distractors = [w[1] for w in SYNONYMS if w[1] != synonym]

    while len(options) < 4:
        fake = random.choice(distractors)
        if fake not in options:
            options.append(fake)

    random.shuffle(options)

    return {
        "question": f"Select the synonym of '{word}'",
        "options": options,
        "answer": synonym,
        "section": "English"
    }


def generate_antonym_question():

    word, antonym = random.choice(ANTONYMS)

    options = [antonym]
    distractors = [w[1] for w in ANTONYMS if w[1] != antonym]

    while len(options) < 4:
        fake = random.choice(distractors)
        if fake not in options:
            options.append(fake)

    random.shuffle(options)

    return {
        "question": f"Select the antonym of '{word}'",
        "options": options,
        "answer": antonym,
        "section": "English"
    }


english_generators = [
    generate_synonym_question,
    generate_antonym_question
]


# ----------------------------
# MASTER QUESTION GENERATOR
# ----------------------------

def generate_question(section):

    if section == "Quantitative":
        generator = random.choice(quant_generators)
        return generator()

    elif section == "Reasoning":
        generator = random.choice(reasoning_generators)
        return generator()

    elif section == "English":
        generator = random.choice(english_generators)
        return generator()

# ----------------------------
# ROUTES
# ----------------------------

@app.route("/")
def home():
    return redirect(url_for("login"))


# -------- REGISTER --------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        user = User(name=name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))

    return render_template("register.html")


# -------- LOGIN --------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))

    return render_template("login.html")


# -------- DASHBOARD --------
@app.route("/dashboard")
@login_required
def dashboard():

    result = DiagnosticResult.query.filter_by(user_id=current_user.id).first()

    weakest_section = None

    if result:
        scores = {
            "Quantitative": result.quantitative_score,
            "Reasoning": result.reasoning_score,
            "English": result.english_score
        }

        weakest_section = min(scores, key=scores.get)

    # Fetch practice history
    practice_history = PracticeResult.query.filter_by(
        user_id=current_user.id
    ).order_by(PracticeResult.created_at.desc()).all()

    return render_template(
        "dashboard.html",
        user=current_user,
        result=result,
        weakest=weakest_section,
        history=practice_history
    )

# -------- SELECT EXAM --------
@app.route("/select_exam", methods=["POST"])
@login_required
def select_exam():
    exam = request.form["exam"]
    current_user.exam_selected = exam
    db.session.commit()
    return redirect(url_for("dashboard"))


# -------- DIAGNOSTIC --------
@app.route("/diagnostic")
@login_required
def diagnostic():

    if current_user.diagnostic_completed:
        return redirect(url_for("dashboard"))

    questions = []

    for section in ["Quantitative", "Reasoning", "English"]:
        for _ in range(5):
            questions.append(generate_question(section))

    session["questions"] = questions
    return render_template("diagnostic.html", questions=questions)


@app.route("/submit_diagnostic", methods=["POST"])
@login_required
def submit_diagnostic():

    questions = session.get("questions")

    scores = {
        "Quantitative": 0,
        "Reasoning": 0,
        "English": 0
    }

    for i, q in enumerate(questions):
        user_answer = request.form.get(f"q{i}")
        if user_answer == str(q["answer"]):
            scores[q["section"]] += 1

    total = sum(scores.values())

    result = DiagnosticResult(
        user_id=current_user.id,
        quantitative_score=scores["Quantitative"],
        reasoning_score=scores["Reasoning"],
        english_score=scores["English"],
        total_score=total
    )

    current_user.diagnostic_completed = True

    db.session.add(result)
    db.session.commit()

    return render_template("result.html", scores=scores, total=total)

@app.route("/practice")
@login_required
def practice():

    result = DiagnosticResult.query.filter_by(user_id=current_user.id).first()

    if not result:
        return redirect("/diagnostic")

    score_percentage = (result.total_score / 15) * 100

    if score_percentage < 40:
        difficulty = "Easy"
    elif score_percentage < 70:
        difficulty = "Medium"
    else:
        difficulty = "Hard"

    questions = []

    for section in ["Quantitative","Reasoning","English"]:
        for _ in range(5):
            questions.append(generate_question(section))

    session["practice_questions"] = questions

    return render_template("practice.html",questions=questions,difficulty=difficulty)

@app.route("/submit_practice", methods=["POST"])
@login_required
def submit_practice():

    questions = session.get("practice_questions")

    if not questions:
        return redirect("/practice")

    correct = 0

    for i, q in enumerate(questions):
        user_answer = request.form.get(f"q{i}")

        if user_answer == str(q["answer"]):
            correct += 1

    total = len(questions)

    score_percentage = round((correct / total) * 100)

    # Save practice result to database
    result = PracticeResult(
        user_id=current_user.id,
        score=correct,
        total=total,
        percentage=score_percentage
    )

    db.session.add(result)
    db.session.commit()

    return render_template(
        "practice_result.html",
        correct=correct,
        total=total,
        percentage=score_percentage
    )

# -------- LOGOUT --------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# ----------------------------
# RUN
# ----------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)