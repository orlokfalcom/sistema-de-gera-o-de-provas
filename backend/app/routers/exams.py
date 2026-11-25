import os
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import Exam, ExamItem, Question, User
from backend.app.schemas import ExamBuildRequest, ExamResponse
from backend.app.services.exam_builder import ExamBuilderService
from backend.app.services.pdf_generator import PDFGeneratorService
from backend.app.services.docx_generator import DocxGeneratorService
from backend.app.routers.auth import require_admin

router = APIRouter(prefix="/api/exams", tags=["Montagem e Geração da Prova Única"])

@router.post("/build", response_model=ExamResponse)
def build_multidisciplinary_exam(
    req: ExamBuildRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    # 1. Fetch questions to include: either specified list or all approved questions
    if req.question_ids:
        questions = db.query(Question).filter(Question.id.in_(req.question_ids)).all()
    else:
        # Default pedagogical rule: use all approved questions
        questions = db.query(Question).filter(Question.validation_status == "approved").all()

    # 1.1 Custom questions per discipline count if provided
    if req.questions_per_discipline:
        for disc, count in req.questions_per_discipline.items():
            if count > 10:
                raise HTTPException(
                    status_code=400,
                    detail=f"O número máximo permitido de questões por matéria é 10. A matéria '{disc}' foi configurada com {count} questões."
                )
        questions = ExamBuilderService.select_questions_by_discipline_counts(
            questions, req.questions_per_discipline
        )

    if not questions:
        raise HTTPException(
            status_code=400,
            detail="Nenhuma questão aprovada encontrada para montar a avaliação com os critérios selecionados."
        )

    # 2. Organize questions according to rule (by_discipline, interleaved, or random)
    ordered_questions = ExamBuilderService.organize_questions(questions, mode=req.organization_mode)

    # 3. Create Exam record
    exam = Exam(
        title=req.title,
        academic_period=req.academic_period,
        institution_name=req.institution_name,
        school_modality=req.school_modality or "integral",
        organization_mode=req.organization_mode,
        show_discipline_header=req.show_discipline_header,
        total_questions=len(ordered_questions),
        created_by=current_user.id
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)

    # 4. Associate sequential ExamItems (1..N)
    exam_items = []
    for seq_num, q in enumerate(ordered_questions, start=1):
        item = ExamItem(
            exam_id=exam.id,
            question_id=q.id,
            order_number=seq_num,
            discipline_override=q.discipline
        )
        db.add(item)
        exam_items.append(item)

    db.commit()
    db.refresh(exam)

    # 5. Generate Output Files:
    # a) Complete PDF with Answer Key at the end
    complete_pdf_path = PDFGeneratorService.generate_exam_pdf(
        exam=exam,
        items=exam_items,
        include_answer_key=True,
        output_filename=f"prova_{exam.id[:8]}_completa.pdf"
    )
    # b) Student PDF without Answer Key
    student_pdf_path = PDFGeneratorService.generate_exam_pdf(
        exam=exam,
        items=exam_items,
        include_answer_key=False,
        output_filename=f"prova_{exam.id[:8]}_estudante.pdf"
    )
    # c) Separate Answer Key PDF for Teachers
    answer_key_pdf_path = PDFGeneratorService.generate_exam_pdf(
        exam=exam,
        items=exam_items,
        include_answer_key=True,
        only_answer_key=True,
        output_filename=f"prova_{exam.id[:8]}_gabarito_oficial.pdf"
    )
    # d) DOCX editable document
    docx_path = DocxGeneratorService.generate_exam_docx(
        exam=exam,
        items=exam_items,
        include_answer_key=True,
        output_filename=f"prova_{exam.id[:8]}.docx"
    )

    exam.pdf_path = str(complete_pdf_path)
    exam.student_pdf_path = str(student_pdf_path)
    exam.answer_key_pdf_path = str(answer_key_pdf_path)
    exam.docx_path = str(docx_path)
    db.commit()
    db.refresh(exam)

    return exam

@router.get("", response_model=List[ExamResponse])
def list_exams(db: Session = Depends(get_db)):
    return db.query(Exam).order_by(Exam.created_at.desc()).all()

@router.get("/{exam_id}", response_model=ExamResponse)
def get_exam(exam_id: str, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada.")
    return exam

@router.get("/{exam_id}/items")
def get_exam_items(exam_id: str, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada.")
    
    result = []
    for item in exam.items:
        result.append({
            "order_number": item.order_number,
            "discipline": item.question.discipline,
            "teacher_name": item.question.teacher_name,
            "statement": item.question.statement,
            "options": item.question.options_json,
            "correct_answer": item.question.correct_answer,
            "question_type": item.question.question_type
        })
    return result

@router.get("/{exam_id}/download/{file_type}")
def download_exam_file(exam_id: str, file_type: str, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada.")

    file_mapping = {
        "pdf": exam.pdf_path,
        "student_pdf": exam.student_pdf_path,
        "answer_key_pdf": exam.answer_key_pdf_path,
        "docx": exam.docx_path
    }

    target_path = file_mapping.get(file_type)
    if not target_path or not Path(target_path).exists():
        raise HTTPException(status_code=404, detail="Arquivo solicitado não localizado.")

    media_types = {
        "pdf": "application/pdf",
        "student_pdf": "application/pdf",
        "answer_key_pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    }

    return FileResponse(
        path=target_path,
        filename=Path(target_path).name,
        media_type=media_types.get(file_type, "application/octet-stream")
    )
