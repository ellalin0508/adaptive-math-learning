import pandas as pd


# ==================================================
# 1. Initialize Student Knowledge Model
# ==================================================

def initialize_student(s01, s02, s03):
    return {
        "S01": s01,
        "S02": s02,
        "S03": s03
    }


# ==================================================
# 2. Select the Weakest Skill
# ==================================================

def select_skill(student):
    return min(student, key=student.get)


# ==================================================
# 3. Select Question Difficulty
# ==================================================

def select_difficulty(mastery):

    if mastery < 0.40:
        return 1

    elif mastery < 0.75:
        return 2

    else:
        return 3


# ==================================================
# 4. Bayesian Knowledge Tracing (BKT)
# ==================================================

def update_mastery(
    prior,
    correct,
    p_learn=0.15,
    p_guess=0.20,
    p_slip=0.10
):

    # Bayesian inference

    if correct:
        numerator = prior * (1 - p_slip)
        denominator = (
            numerator + (1 - prior) * p_guess
        )

    else:
        numerator = prior * p_slip
        denominator = (
            numerator + (1 - prior) * (1 - p_guess)
        )

    posterior = numerator / denominator

    # Markov transition

    updated = posterior + (1 - posterior) * p_learn

    return updated


# ==================================================
# 5. Calculate Individual Growth Targets
# ==================================================

def calculate_targets(initial_student, growth=0.20):

    targets = {}

    for skill, mastery in initial_student.items():

        targets[skill] = (
            mastery + growth * (1 - mastery)
        )

    return targets


# ==================================================
# 6. Check Assignment Completion
# ==================================================

def is_complete(student, targets):

    for skill in student:

        if student[skill] < targets[skill]:
            return False

    return True


# ==================================================
# 7. Adaptive Question Recommendation Engine
# ==================================================

def recommend_question(
    student,
    questions,
    used_ids,
    targets
):

    # Identify unfinished skills

    unfinished_skills = [
        skill for skill in student
        if student[skill] < targets[skill]
    ]

    # Exclude completed skills and previously used questions

    available = questions[
        (~questions["question_id"].isin(used_ids)) &
        (questions["skill"].isin(unfinished_skills))
    ]

    # Stop if there are no available questions

    if available.empty:
        return None

    # Select the weakest available skill

    available_skills = available["skill"].unique()

    skill = min(
        available_skills,
        key=student.get
    )

    # Determine the ideal difficulty

    difficulty = select_difficulty(student[skill])

    # Filter questions by skill

    candidates = available[
        available["skill"] == skill
    ].copy()

    # Find the closest available difficulty

    candidates["distance"] = abs(
        candidates["difficulty"] - difficulty
    )

    best_candidates = candidates[
        candidates["distance"] ==
        candidates["distance"].min()
    ]

    # Randomly select one suitable question

    return best_candidates.sample(1).iloc[0]
