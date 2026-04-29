import random

# -----------------------------
# Utility: Shuffle Options
# -----------------------------
def generate_options(correct_answer):
    options = [correct_answer]

    while len(options) < 4:
        fake = correct_answer + random.randint(-10, 10)
        if fake != correct_answer and fake not in options:
            options.append(fake)

    random.shuffle(options)

    return options


# -----------------------------
# Quantitative Generators
# -----------------------------

def generate_addition_question(difficulty):
    if difficulty == "Easy":
        a = random.randint(1, 20)
        b = random.randint(1, 20)
    elif difficulty == "Medium":
        a = random.randint(20, 100)
        b = random.randint(20, 100)
    else:
        a = random.randint(100, 500)
        b = random.randint(100, 500)

    question = f"What is {a} + {b}?"
    answer = a + b
    options = generate_options(answer)

    return {
        "question": question,
        "options": options,
        "answer": answer,
        "section": "Quantitative",
        "difficulty": difficulty
    }


# -----------------------------
# Reasoning Generators
# -----------------------------

def generate_number_series(difficulty):
    start = random.randint(1, 10)

    if difficulty == "Easy":
        diff = random.randint(1, 5)
    elif difficulty == "Medium":
        diff = random.randint(5, 10)
    else:
        diff = random.randint(10, 20)

    series = [start + i * diff for i in range(4)]
    next_value = start + 4 * diff

    question = f"Find the next number in the series: {series[0]}, {series[1]}, {series[2]}, {series[3]}, ?"

    options = generate_options(next_value)

    return {
        "question": question,
        "options": options,
        "answer": next_value,
        "section": "Reasoning",
        "difficulty": difficulty
    }


# -----------------------------
# English Generators
# -----------------------------

ENGLISH_WORDS = [
    ("happy", "joyful"),
    ("fast", "quick"),
    ("big", "large"),
    ("small", "tiny"),
]

def generate_synonym_question(difficulty):
    word, synonym = random.choice(ENGLISH_WORDS)

    options = [synonym]

    distractors = [w[1] for w in ENGLISH_WORDS if w[1] != synonym]
    while len(options) < 4:
        fake = random.choice(distractors)
        if fake not in options:
            options.append(fake)

    random.shuffle(options)

    return {
        "question": f"Select the synonym of '{word}'",
        "options": options,
        "answer": synonym,
        "section": "English",
        "difficulty": difficulty
    }


# -----------------------------
# Master Generator
# -----------------------------

def generate_question(section, difficulty):
    if section == "Quantitative":
        return generate_addition_question(difficulty)

    elif section == "Reasoning":
        return generate_number_series(difficulty)

    elif section == "English":
        return generate_synonym_question(difficulty)

    else:
        return None