from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import Question
from backend.app.schemas import QuestionResponse, QuestionUpdate

router = APIRouter(prefix="/api/questions", tags=["Banco de Questões & Conferência"])

@router.get("", response_model=List[QuestionResponse])
def list_questions(
    discipline: Optional[str] = None,
    target_grade: Optional[str] = None,
    school_modality: Optional[str] = None,
    validation_status: Optional[str] = None,
    is_duplicate: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Question)

    if discipline:
        query = query.filter(Question.discipline.ilike(f"%{discipline}%"))
    if target_grade and not target_grade.lower().startswith("todos"):
        query = query.filter(Question.target_grade.ilike(f"%{target_grade[:6]}%"))
    if school_modality and school_modality in ("regular", "integral"):
        allowed = ["regular", "ambos"] if school_modality == "regular" else ["integral", "regular", "ambos"]
        query = query.filter(Question.school_modality.in_(allowed))
    if validation_status:
        query = query.filter(Question.validation_status == validation_status)
    if is_duplicate is not None:
        query = query.filter(Question.is_duplicate == is_duplicate)
    if search:
        query = query.filter(Question.statement.ilike(f"%{search}%"))

    return query.order_by(Question.created_at.desc()).all()

@router.get("/pending-review", response_model=List[QuestionResponse])
def get_pending_review_questions(db: Session = Depends(get_db)):
    """Returns questions flagged for verification (missing answers, incomplete alternatives, etc)."""
    return db.query(Question).filter(Question.validation_status == "pending_review").all()

@router.get("/{q_id}", response_model=QuestionResponse)
def get_question(q_id: str, db: Session = Depends(get_db)):
    q = db.query(Question).filter(Question.id == q_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Questão não encontrada.")
    return q

@router.patch("/{q_id}", response_model=QuestionResponse)
def update_question(q_id: str, payload: QuestionUpdate, db: Session = Depends(get_db)):
    q = db.query(Question).filter(Question.id == q_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Questão não encontrada.")

    if payload.discipline is not None:
        q.discipline = payload.discipline
    if payload.statement is not None:
        q.statement = payload.statement
    if payload.options_json is not None:
        q.options_json = payload.options_json
    if payload.correct_answer is not None:
        q.correct_answer = payload.correct_answer
    if payload.validation_status is not None:
        q.validation_status = payload.validation_status
    if payload.validation_notes is not None:
        q.validation_notes = payload.validation_notes

    db.commit()
    db.refresh(q)
    return q

@router.post("/{q_id}/approve", response_model=QuestionResponse)
def approve_question(q_id: str, correct_answer: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Question).filter(Question.id == q_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Questão não encontrada.")

    if correct_answer:
        q.correct_answer = correct_answer.strip().upper()
    q.validation_status = "approved"
    q.validation_notes = "Aprovada manualmente pela coordenação pedagógica."
    db.commit()
    db.refresh(q)
    return q

@router.delete("/{q_id}")
def delete_question(q_id: str, db: Session = Depends(get_db)):
    q = db.query(Question).filter(Question.id == q_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Questão não encontrada.")
    db.delete(q)
    db.commit()
    return {"message": "Questão excluída com sucesso."}
