from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.database import get_db
from backend.app.models import User, Document, Question, Exam

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard & Indicadores"])

@router.get("/metrics")
def get_dashboard_metrics(db: Session = Depends(get_db)):
    total_teachers = db.query(User).filter(User.role == "professor").count()
    total_documents = db.query(Document).count()
    total_questions = db.query(Question).count()
    total_approved = db.query(Question).filter(Question.validation_status == "approved").count()
    total_pending = db.query(Question).filter(Question.validation_status == "pending_review").count()
    total_duplicates = db.query(Question).filter(Question.is_duplicate == True).count()
    total_exams = db.query(Exam).count()

    # Distinct disciplines
    disciplines_count = db.query(Question.discipline).distinct().count()

    # Questions per discipline
    disc_distribution = (
        db.query(Question.discipline, func.count(Question.id))
        .group_by(Question.discipline)
        .all()
    )

    return {
        "total_teachers": total_teachers or 1,
        "total_documents": total_documents,
        "total_disciplines": disciplines_count,
        "total_questions": total_questions,
        "total_approved": total_approved,
        "total_pending": total_pending,
        "total_duplicates": total_duplicates,
        "total_exams": total_exams,
        "discipline_breakdown": [
            {"discipline": d[0], "count": d[1]} for d in disc_distribution
        ]
    }
