from flask import Blueprint, render_template, request, session, redirect, url_for
from flask_login import login_required, current_user
from question_engine import generate_question
from models import db, DiagnosticResult, User

diagnostic_bp = Blueprint("diagnostic", __name__)

SECTIONS = ["Quantitative", "Reasoning", "English"]

# --------------------------
# Start Diagnostic
# --------------------------
@diagnostic_bp.route("/diagnostic")
@login_required
def start_diagnostic():

    if current_user.diagnostic_completed:
        return redirect(url_for("dashboard"))

    questions = []

    for section in SECTIONS:
        for _ in range(5):
            q = generate_question(section, "Medium")
            questions.append(q)

    session["diagnostic_questions"] = questions

    return render_template("diagnostic.html", questions=questions)


# --------------------------
# Submit Diagnostic
# --------------------------
@diagnostic_bp.route("/submit_diagnostic", methods=["POST"])
@login_required
def submit_diagnostic():

    questions = session.get("diagnostic_questions")
    if not questions:
        return redirect(url_for("diagnostic.start_diagnostic"))

    section_scores = {
        "Quantitative": 0,
        "Reasoning": 0,
        "English": 0
    }

    for i, q in enumerate(questions):
        user_answer = request.form.get(f"q{i}")
        correct_answer = str(q["answer"])

        if user_answer == correct_answer:
            section_scores[q["section"]] += 1

    total_score = sum(section_scores.values())

    result = DiagnosticResult(
        user_id=current_user.id,
        quantitative_score=section_scores["Quantitative"],
        reasoning_score=section_scores["Reasoning"],
        english_score=section_scores["English"],
        total_score=total_score
    )

    db.session.add(result)

    user = User.query.get(current_user.id)
    user.diagnostic_completed = True

    db.session.commit()

    return render_template("result.html", scores=section_scores, total=total_score)