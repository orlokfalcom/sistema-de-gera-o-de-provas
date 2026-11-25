import random
from typing import List, Dict
from backend.app.models import Question

class ExamBuilderService:
    @staticmethod
    def select_questions_by_discipline_counts(
        questions: List[Question],
        counts_per_discipline: Dict[str, int]
    ) -> List[Question]:
        """
        Filters questions according to a dict { discipline_name: count }.
        If a discipline is present in counts_per_discipline, takes at most that many questions (capped at 10 max per subject).
        If a discipline is omitted or None, all its questions are preserved (up to 10 max).
        """
        disc_map: Dict[str, List[Question]] = {}
        for q in questions:
            disc_map.setdefault(q.discipline, []).append(q)

        selected: List[Question] = []
        for disc, q_list in disc_map.items():
            if disc in counts_per_discipline:
                requested_limit = counts_per_discipline[disc]
                # Enforce rule: max 10 questions per discipline
                limit = min(max(requested_limit, 0), 10)
                if limit > 0:
                    selected.extend(q_list[:limit])
            else:
                # Default rule if not specified: cap at 10 questions
                selected.extend(q_list[:10])
        return selected

    @staticmethod
    def organize_questions(
        questions: List[Question],
        mode: str = "by_discipline"
    ) -> List[Question]:
        """
        Organizes questions based on specified mode without losing ANY question:
        - 'by_discipline': Groups all questions by subject.
        - 'interleaved': Round-robin between subjects so student sees Math, Portuguese, Physics, etc.
        - 'random': Shuffles questions randomly.
        """
        if not questions:
            return []

        if mode == "random":
            shuffled = list(questions)
            random.seed(42)  # Deterministic seed for reproducible tests unless changed
            random.shuffle(shuffled)
            return shuffled

        if mode == "interleaved":
            # Group by discipline
            disc_map: Dict[str, List[Question]] = {}
            for q in questions:
                disc_map.setdefault(q.discipline, []).append(q)

            interleaved = []
            max_len = max(len(lst) for lst in disc_map.values())
            disciplines = sorted(disc_map.keys())

            for i in range(max_len):
                for d in disciplines:
                    if i < len(disc_map[d]):
                        interleaved.append(disc_map[d][i])
            return interleaved

        # Default: 'by_discipline'
        # Sort questions grouped by discipline name, preserving their natural order inside each
        return sorted(questions, key=lambda q: (q.discipline, q.created_at))
