"""Keyword-based HR knowledge base backed by canned policy answers."""

_POLICIES = {
    "leave": "Employees accrue 1.5 days of paid leave per month, up to 18 days per year.",
    "insurance": "The company insurance policy covers medical, dental, and vision for employees and dependents.",
}


def answer_hr_question(question: str) -> str:
    if not question or not question.strip():
        raise ValueError("question must not be empty")

    question_lower = question.lower()
    for keyword, answer in _POLICIES.items():
        if keyword in question_lower:
            return answer
    return "I don't have information on that HR topic yet. Please contact HR directly."
