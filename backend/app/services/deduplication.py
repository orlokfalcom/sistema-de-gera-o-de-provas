import re
from typing import List, Tuple, Optional
from backend.app.models import Question

def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-záàâãéèêíïóôõöúç0-9\s]', '', text)
    return " ".join(text.split())

def calculate_similarity(text1: str, text2: str) -> float:
    t1 = set(normalize_text(text1).split())
    t2 = set(normalize_text(text2).split())
    if not t1 or not t2:
        return 0.0
    intersection = len(t1.intersection(t2))
    union = len(t1.union(t2))
    return intersection / union

def check_duplicate_question(statement: str, existing_questions: List[Question], threshold: float = 0.80) -> Tuple[bool, Optional[str]]:
    """
    Checks if a question statement has >= threshold word similarity with any existing question.
    Returns (is_duplicate, duplicate_of_id).
    """
    for eq in existing_questions:
        sim = calculate_similarity(statement, eq.statement)
        if sim >= threshold:
            return True, eq.id
    return False, None
