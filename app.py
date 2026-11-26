import streamlit as st
import pandas as pd

from engine import (
    initialize_student,
    update_mastery,
    calculate_targets,
    is_complete,
    recommend_question
)

st.set_page_config(
    page_title="MathPath",
    page_icon="📚",
    layout="centered"
)

# 1. Load question bank

questions = pd.read_csv("question_bank.csv")

# 2. Initialize session state

if "student" not in st.session_state:

    initial = initialize_student(
        0.30, 0.60, 0.45
    )

    st.session_state.student = initial.copy()
    st.session_state.initial = initial.copy()

    st.session_state.targets = calculate_targets(
        initial
    )

    st.session_state.used_ids = []
    st.session_state.history = []
    st.session_state.current_question = None
    st.session_state.feedback = None

# 3. Page title

st.title("MathPath")

st.caption("Personalized Mathematics Learning")

st.subheader("Quadratic Functions")

student = st.session_state.student
targets = st.session_state.targets

# 4. Display assignment progress

completed = sum(
    student[s] >= targets[s]
    for s in student
)

st.progress(
    completed / len(student)
)

st.write(
    f"{completed} of {len(student)} "
    "learning targets reached"
)

# 5. Display previous feedback

if st.session_state.feedback is not None:

    feedback = st.session_state.feedback

    if feedback["correct"]:
        st.success("Correct! Great work.")
    else:
        st.warning("Keep practicing!")

    st.write(
        "Expected answer:",
        feedback["answer"]
    )

    if st.button("Next Question"):

        st.session_state.feedback = None
        st.session_state.current_question = None

        st.rerun()

# 6. Check stopping condition

elif is_complete(student, targets):

    st.success("Assignment complete!")

    st.balloons()

elif len(st.session_state.used_ids) >= 20:

    st.info("Practice limit reached.")

# 7. Recommend and display question

else:

    if st.session_state.current_question is None:

        st.session_state.current_question = (
            recommend_question(
                student,
                questions,
                st.session_state.used_ids,
                targets
            )
        )

    question = st.session_state.current_question

    if question is None:

        st.info("No more suitable questions.")

    else:

        qid = question["question_id"]
        skill = question["skill"]

        st.markdown(
            f"### Question "
            f"{len(st.session_state.used_ids) + 1}"
        )

        st.write(question["question"])

        answer = st.text_input(
            "Your answer",
            key=f"answer_{qid}"
        )

        with st.expander("I need a hint"):

            st.write(question["hint"])

        # Temporary self-assessment mechanism

        with st.expander("Check your answer"):

            st.write(question["answer"])

            result = st.radio(
                "Was your answer correct?",
                ["Correct", "Incorrect"],
                index=None,
                key=f"result_{qid}"
            )

            if st.button(
                "Submit",
                disabled=(
                    result is None
                    or not answer.strip()
                )
            ):

                correct = result == "Correct"

                old_mastery = student[skill]

                student[skill] = update_mastery(
                    old_mastery,
                    correct
                )

                st.session_state.used_ids.append(
                    qid
                )

                st.session_state.history.append({
                    "question_id": qid,
                    "skill": skill,
                    "difficulty": int(
                        question["difficulty"]
                    ),
                    "correct": correct,
                    "mastery_before": old_mastery,
                    "mastery_after": student[skill]
                })

                st.session_state.feedback = {
                    "correct": correct,
                    "answer": question["answer"]
                }

                st.rerun()

# 8. Research dashboard

with st.sidebar:

    st.header("Research Dashboard")

    summary = pd.DataFrame({
        "Initial": st.session_state.initial,
        "Current": student,
        "Target": targets
    })

    st.dataframe(summary)

    st.bar_chart(summary)

    st.write(
        "Questions attempted:",
        len(st.session_state.used_ids)
    )

    history = pd.DataFrame(
        st.session_state.history
    )

    if not history.empty:

        st.download_button(
            "Download practice history",
            history.to_csv(index=False),
            file_name="practice_history.csv",
            mime="text/csv"
        )

    if st.button("Restart Assignment"):

        st.session_state.clear()

        st.rerun()
