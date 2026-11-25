"""
Seeder institucional de questões — Ensino Médio (BNCC) + Atividades Integradoras + Itinerários Técnicos SEE/MG.
Alimenta de forma idempotente as tabelas `documents` e `questions` do banco de dados SQLite.
"""
import json
import re
from pathlib import Path
from sqlalchemy.orm import Session
from backend.app.models import Document, Question


def load_seemg_seed_data():
    """Loads the canonical SEE/MG question bank from assets/js/catalog-data.js (or legacy index.html)."""
    repo_root = Path(__file__).resolve().parents[2]
    candidates = [
        repo_root / "assets" / "js" / "catalog-data.js",
        repo_root / "backend" / "static" / "assets" / "js" / "catalog-data.js",
        repo_root / "index.html",
    ]
    for path in candidates:
        if path.exists():
            content = path.read_text(encoding="utf-8")
            m = re.search(r"const DEFAULT_SAMPLE_QUESTIONS = (\[[\s\S]*?\]);", content)
            if m:
                return json.loads(m.group(1))
    return []


def seed_seemg_questions(db: Session) -> dict:
    """Idempotently inserts all SEE/MG High School and Technical Itinerary sample questions into the database."""
    questions_data = load_seemg_seed_data()
    if not questions_data:
        return {"documents_added": 0, "questions_added": 0}

    docs_added = 0
    questions_added = 0

    # Group by discipline to create one source Document per discipline
    by_discipline = {}
    for q in questions_data:
        by_discipline.setdefault(q["discipline"], []).append(q)

    for idx, (disc, q_list) in enumerate(by_discipline.items(), start=1):
        doc_id = f"doc-seemg-{idx:03d}"
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            doc = Document(
                id=doc_id,
                filename=q_list[0].get("source_filename", f"{idx:02d}_seemg.pdf"),
                storage_path=f"seed/seemg/{doc_id}.pdf",
                discipline=disc,
                target_grade="Ensino Médio / SEE-MG",
                academic_period="2026 - 1º Trimestre",
                status="completed",
                total_questions_found=len(q_list),
                uploaded_by="admin-001"
            )
            db.add(doc)
            docs_added += 1

        for q in q_list:
            existing_q = db.query(Question).filter(Question.id == q["id"]).first()
            if not existing_q:
                new_q = Question(
                    id=q["id"],
                    document_id=doc_id,
                    discipline=disc,
                    teacher_name=q.get("teacher_name", "Docente SEE/MG"),
                    question_type=q.get("question_type", "multiple_choice"),
                    statement=q["statement"],
                    options_json=q.get("options_json"),
                    correct_answer=q.get("correct_answer", "A"),
                    difficulty="medio",
                    validation_status=q.get("validation_status", "approved"),
                    page_number=1
                )
                db.add(new_q)
                questions_added += 1

    db.commit()
    return {
        "documents_added": docs_added,
        "questions_added": questions_added,
        "total_questions_in_db": db.query(Question).count(),
        "total_disciplines_in_db": db.query(Question.discipline).distinct().count(),
    }


if __name__ == "__main__":
    from backend.app.database import SessionLocal
    from backend.app.init_db import init_database
    init_database()
    db = SessionLocal()
    try:
        res = seed_seemg_questions(db)
        print("SEE/MG DB Seed Result:", res)
    finally:
        db.close()
