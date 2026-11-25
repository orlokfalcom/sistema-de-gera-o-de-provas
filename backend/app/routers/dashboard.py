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

    # Classify by knowledge area
    knowledge_areas = {
        "Linguagens": ["português", "língua portuguesa", "literatura", "redação", "inglês", "língua inglesa", "espanhol", "arte", "educação física"],
        "Matemática": ["matemática", "matemática financeira", "estatística"],
        "Ciências da Natureza": ["física", "química", "biologia", "biotecnologia", "astronomia"],
        "Ciências Humanas": ["história", "geografia", "filosofia", "sociologia", "geopolítica"],
        "Itinerários Formativos": ["robótica", "educação financeira", "empreendedorismo", "projeto de vida", "sistemas", "programação", "administração", "logística", "inteligência artificial"]
    }

    area_counts = {area: 0 for area in knowledge_areas}
    for disc_name, count in disc_distribution:
        disc_lower = disc_name.lower()
        categorized = False
        for area, keywords in knowledge_areas.items():
            if any(k in disc_lower for k in keywords):
                area_counts[area] += count
                categorized = True
                break
        if not categorized:
            area_counts["Itinerários Formativos"] += count

    approval_rate = round((total_approved / total_questions * 100), 1) if total_questions > 0 else 0.0

    # Recent exams
    recent_exams = (
        db.query(Exam)
        .order_by(Exam.created_at.desc())
        .limit(5)
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
        "approval_rate_percent": approval_rate,
        "area_breakdown": area_counts,
        "discipline_breakdown": [
            {"discipline": d[0], "count": d[1]} for d in disc_distribution
        ],
        "recent_exams": [
            {
                "id": ex.id,
                "title": ex.title,
                "academic_period": ex.academic_period,
                "total_questions": ex.total_questions,
                "school_modality": getattr(ex, "school_modality", "integral"),
                "created_at": ex.created_at.isoformat() if ex.created_at else None
            }
            for ex in recent_exams
        ]
    }
