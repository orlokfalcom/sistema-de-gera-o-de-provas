import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import Document, Question, User
from backend.app.schemas import DocumentResponse
from backend.app.config import UPLOADS_DIR
from backend.app.services.pdf_extractor import PDFExtractionService
from backend.app.services.deduplication import check_duplicate_question

router = APIRouter(prefix="/api/documents", tags=["Recebimento de PDFs"])

@router.post("/upload", response_model=List[DocumentResponse])
async def upload_multiple_documents(
    files: List[UploadFile] = File(...),
    discipline: str = Form(""),
    teacher_name: str = Form("Professor(a) Responsável"),
    target_grade: str = Form("Ensino Médio"),
    academic_period: str = Form("2026 - 1º Bimestre"),
    db: Session = Depends(get_db)
):
    if not files:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado.")

    extractor = PDFExtractionService()
    existing_questions = db.query(Question).all()
    created_docs = []

    for file in files:
        # Validate file extension
        if not file.filename.lower().endswith(".pdf"):
            continue

        file_dest = UPLOADS_DIR / f"{Path(file.filename).stem}_{file.filename}"
        with open(file_dest, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = file_dest.stat().st_size

        doc_record = Document(
            filename=file.filename,
            storage_path=str(file_dest),
            discipline=discipline or "A Definir",
            target_grade=target_grade,
            academic_period=academic_period,
            status="processing",
            file_size_bytes=file_size
        )
        db.add(doc_record)
        db.commit()
        db.refresh(doc_record)

        # Extract questions from PDF
        try:
            extracted_items = extractor.extract_document(
                pdf_path=str(file_dest),
                discipline_hint=discipline,
                teacher_hint=teacher_name
            )

            # Update document discipline if auto-detected and wasn't provided
            if not discipline and extracted_items:
                detected_disc = extracted_items[0].get("discipline", "Multidisciplinar")
                doc_record.discipline = detected_disc

            # Save questions into Question Bank
            for item in extracted_items:
                is_dup, dup_id = check_duplicate_question(item["statement"], existing_questions)

                q_record = Question(
                    document_id=doc_record.id,
                    discipline=item["discipline"],
                    teacher_name=teacher_name,
                    question_type=item["question_type"],
                    statement=item["statement"],
                    options_json=item["options_json"],
                    correct_answer=item["correct_answer"],
                    has_image=item["has_image"],
                    image_paths_json=item["image_paths_json"],
                    page_number=item["page_number"],
                    difficulty=item["difficulty"],
                    validation_status=item["validation_status"],
                    validation_notes=item["validation_notes"],
                    is_duplicate=is_dup,
                    duplicate_of_id=dup_id,
                    source_filename=file.filename
                )
                db.add(q_record)
                existing_questions.append(q_record)

            doc_record.total_questions_found = len(extracted_items)
            doc_record.status = "completed"
            db.commit()
            db.refresh(doc_record)
            created_docs.append(doc_record)

        except Exception as e:
            doc_record.status = "failed"
            db.commit()
            raise HTTPException(status_code=500, detail=f"Erro ao processar '{file.filename}': {str(e)}")

    if not created_docs:
        raise HTTPException(status_code=400, detail="Nenhum arquivo PDF válido foi enviado ou processado.")

    return created_docs

@router.get("", response_model=List[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    return db.query(Document).order_by(Document.created_at.desc()).all()

@router.delete("/{doc_id}")
def delete_document(doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    db.delete(doc)
    db.commit()
    return {"message": "Documento e questões associadas removidos com sucesso."}
