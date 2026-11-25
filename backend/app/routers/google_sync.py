from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from typing import Dict, Any

from backend.app.database import get_db
from backend.app.models import Exam, Document, Question
from backend.app.services.google_service import GoogleWorkspaceService

router = APIRouter(prefix="/api/google", tags=["Integração Google Workspace"])

@router.post("/drive/sync-exam/{exam_id}")
def sync_exam_to_drive(exam_id: str, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada.")

    file_paths = [
        path for path in [exam.pdf_path, exam.student_pdf_path, exam.answer_key_pdf_path, exam.docx_path]
        if path
    ]

    service = GoogleWorkspaceService()
    result = service.sync_to_google_drive(
        exam_id=exam.id,
        exam_title=exam.title,
        academic_period=exam.academic_period,
        file_paths=file_paths
    )
    return result

@router.post("/sheets/export-log")
def export_processing_log_to_sheets(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    records = []
    for d in docs:
        records.append({
            "created_at": d.created_at.strftime("%d/%m/%Y %H:%M"),
            "filename": d.filename,
            "discipline": d.discipline,
            "target_grade": d.target_grade,
            "academic_period": d.academic_period,
            "total_questions_found": d.total_questions_found,
            "status": d.status
        })

    service = GoogleWorkspaceService()
    return service.export_to_google_sheets(
        spreadsheet_title="Relatório de Documentos Recebidos - Ensino Médio",
        records=records,
        sheet_type="received_documents"
    )

@router.post("/sheets/export-answer-key/{exam_id}")
def export_answer_key_to_sheets(exam_id: str, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada.")

    records = []
    for item in exam.items:
        records.append({
            "order_number": item.order_number,
            "discipline": item.question.discipline,
            "teacher_name": item.question.teacher_name,
            "correct_answer": item.question.correct_answer
        })

    service = GoogleWorkspaceService()
    return service.export_to_google_sheets(
        spreadsheet_title=f"Gabarito Oficial — {exam.title}",
        records=records,
        sheet_type="exam_answer_key"
    )

@router.get("/apps-script-template", response_class=PlainTextResponse)
def get_apps_script_code():
    return GoogleWorkspaceService.get_google_apps_script_template()
