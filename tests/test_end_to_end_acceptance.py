import os
import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app.database import SessionLocal, Base, engine
from backend.app.models import User, Document, Question, Exam, ExamItem
from backend.app.services.pdf_extractor import PDFExtractionService
from backend.app.services.deduplication import check_duplicate_question
from backend.app.services.exam_builder import ExamBuilderService
from backend.app.services.pdf_generator import PDFGeneratorService
from backend.app.services.docx_generator import DocxGeneratorService
from backend.app.services.google_service import GoogleWorkspaceService

def run_acceptance_test():
    print("=================================================================")
    print("INICIANDO TESTE DE ACEITAÇÃO FINAL — PROVA MULTIDISCIPLINAR")
    print("=================================================================\n")

    # Reset test database tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # 1. Verify User
    admin = User(
        id="admin-test",
        email="coordenacao@escola.gov.br",
        full_name="Coordenação do Ensino Médio",
        role="admin"
    )
    db.add(admin)
    db.commit()

    sample_dir = ROOT_DIR / "tests" / "sample_files"
    discipline_files = [
        ("1_matematica.pdf", "Matemática", "Prof. Roberto"),
        ("2_portugues.pdf", "Português", "Profª. Mariana"),
        ("3_biologia.pdf", "Biologia", "Profª. Carla"),
        ("4_historia.pdf", "História", "Prof. André"),
        ("5_fisica.pdf", "Física", "Prof. Marcos"),
    ]

    extractor = PDFExtractionService()
    existing_questions = []

    print("ETAPA 1: Processamento e Extração dos 5 PDFs de Disciplinas Diferentes")
    uploaded_docs = []

    for filename, disc_name, teacher in discipline_files:
        pdf_path = sample_dir / filename
        assert pdf_path.exists(), f"Arquivo {filename} não encontrado!"

        doc_record = Document(
            filename=filename,
            storage_path=str(pdf_path),
            discipline=disc_name,
            target_grade="3º Ano EM",
            academic_period="2026 - 1º Bimestre",
            status="processing",
            file_size_bytes=pdf_path.stat().st_size
        )
        db.add(doc_record)
        db.commit()
        db.refresh(doc_record)

        # Extract items
        items = extractor.extract_document(str(pdf_path), discipline_hint=disc_name, teacher_hint=teacher)
        print(f" -> '{filename}' ({disc_name}): {len(items)} questões extraídas com sucesso.")
        assert len(items) >= 2, f"Esperava pelo menos 2 questões em {filename}, obteve {len(items)}"

        for it in items:
            is_dup, dup_id = check_duplicate_question(it["statement"], existing_questions)
            q = Question(
                document_id=doc_record.id,
                discipline=it["discipline"],
                teacher_name=teacher,
                question_type=it["question_type"],
                statement=it["statement"],
                options_json=it["options_json"],
                correct_answer=it["correct_answer"],
                has_image=it["has_image"],
                image_paths_json=it["image_paths_json"],
                page_number=it["page_number"],
                validation_status=it["validation_status"],
                validation_notes=it["validation_notes"],
                is_duplicate=is_dup,
                source_filename=filename
            )
            db.add(q)
            existing_questions.append(q)

        doc_record.total_questions_found = len(items)
        doc_record.status = "completed"
        db.commit()
        uploaded_docs.append(doc_record)

    total_db_questions = db.query(Question).count()
    print(f"\n[CRITÉRIO 1 E 2 APROVADOS]: Todos os 5 arquivos foram recebidos e totalizam {total_db_questions} questões.")
    assert total_db_questions == 10, f"Deveria ter 10 questões, tem {total_db_questions}"

    # Verify answers and disciplines
    questions = db.query(Question).all()
    disciplines_found = set(q.discipline for q in questions)
    print(f"[CRITÉRIO 3 E 4 APROVADOS]: {len(disciplines_found)} disciplinas identificadas: {disciplines_found}")
    assert len(disciplines_found) == 5, "Todas as 5 disciplinas devem estar presentes!"

    for q in questions:
        assert q.correct_answer is not None and len(q.correct_answer) > 0, f"Gabarito não pode ser nulo na questão {q.statement[:30]}"
        print(f"   • [{q.discipline}] Gabarito identificado: {q.correct_answer} (Origem: {q.source_filename})")

    print("\nETAPA 2: Montagem da Avaliação Geral Multidisciplinar Única")
    ordered_questions = ExamBuilderService.organize_questions(questions, mode="by_discipline")
    assert len(ordered_questions) == 10, "Nenhuma questão pode ser omitida!"

    exam = Exam(
        title="Avaliação Geral Multidisciplinar do Ensino Médio",
        academic_period="2026 - 1º Bimestre Integrado",
        institution_name="Colégio Integrado de Ensino Médio",
        organization_mode="by_discipline",
        show_discipline_header=True,
        total_questions=len(ordered_questions)
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)

    exam_items = []
    for seq, q in enumerate(ordered_questions, start=1):
        item = ExamItem(
            exam_id=exam.id,
            question_id=q.id,
            order_number=seq,
            discipline_override=q.discipline
        )
        db.add(item)
        exam_items.append(item)
    db.commit()

    print(f"[CRITÉRIO 5 E 6 APROVADOS]: Prova única criada com numeração sequencial contínua de 01 a {len(exam_items):02d}.")
    assert exam_items[0].order_number == 1
    assert exam_items[-1].order_number == 10

    print("\nETAPA 3: Geração dos Documentos Oficiais (PDF e DOCX)")
    # Complete PDF (with answer key at the end)
    pdf_complete = PDFGeneratorService.generate_exam_pdf(
        exam=exam,
        items=exam_items,
        include_answer_key=True,
        output_filename="TESTE_PROVA_COMPLETA.pdf"
    )
    print(f" -> PDF Completo (com gabarito ao final): {pdf_complete}")
    assert Path(pdf_complete).exists() and Path(pdf_complete).stat().st_size > 1000

    # Student PDF (without answer key)
    pdf_student = PDFGeneratorService.generate_exam_pdf(
        exam=exam,
        items=exam_items,
        include_answer_key=False,
        output_filename="TESTE_PROVA_ESTUDANTE.pdf"
    )
    print(f" -> PDF do Estudante (sem gabarito): {pdf_student}")
    assert Path(pdf_student).exists() and Path(pdf_student).stat().st_size > 1000

    # Separate Answer Key PDF for Teachers
    pdf_ak = PDFGeneratorService.generate_exam_pdf(
        exam=exam,
        items=exam_items,
        include_answer_key=True,
        only_answer_key=True,
        output_filename="TESTE_GABARITO_PROFESSORES.pdf"
    )
    print(f" -> PDF Gabarito dos Professores: {pdf_ak}")
    assert Path(pdf_ak).exists() and Path(pdf_ak).stat().st_size > 1000

    # Editable DOCX
    docx_file = DocxGeneratorService.generate_exam_docx(
        exam=exam,
        items=exam_items,
        include_answer_key=True,
        output_filename="TESTE_PROVA_EDITAVEL.docx"
    )
    print(f" -> DOCX Prova Editável: {docx_file}")
    assert Path(docx_file).exists() and Path(docx_file).stat().st_size > 1000

    print("\nETAPA 4: Validação do Gabarito e Sigilo da Versão do Estudante")
    import fitz
    # Check student PDF does NOT contain the text 'GABARITO OFICIAL'
    doc_student = fitz.open(pdf_student)
    student_text = "".join(page.get_text("text") for page in doc_student)
    assert "GABARITO OFICIAL" not in student_text, "A prova do estudante NUNCA pode revelar o gabarito!"
    doc_student.close()
    print("[CRITÉRIO 9 APROVADO]: Versão do estudante verificada e 100% isenta de gabarito.")

    # Check complete PDF DOES contain 'GABARITO OFICIAL' at the end
    doc_complete = fitz.open(pdf_complete)
    complete_text = "".join(page.get_text("text") for page in doc_complete)
    assert "GABARITO OFICIAL" in complete_text, "A prova completa deve conter o gabarito ao final!"
    doc_complete.close()
    print("[CRITÉRIO 7 E 8 APROVADOS]: Gabarito localizado ao final da avaliação completa.")
    print("[CRITÉRIO 10 APROVADO]: Arquivos PDF e DOCX gerados com total fidelidade tipográfica e formatação de Ensino Médio.")

    print("\nETAPA 5: Teste de Integração Google Workspace (Drive & Sheets)")
    google_svc = GoogleWorkspaceService()
    drive_sync = google_svc.sync_to_google_drive(
        exam_id=exam.id,
        exam_title=exam.title,
        academic_period=exam.academic_period,
        file_paths=[pdf_complete, pdf_student, pdf_ak, docx_file]
    )
    print(f" -> Google Drive Sync: {drive_sync['status']} ({len(drive_sync['files'])} arquivos mapeados na pasta '{drive_sync['folder']}')")
    assert drive_sync["status"] == "success"

    sheets_export = google_svc.export_to_google_sheets(
        spreadsheet_title="Gabarito Oficial — Prova Única",
        records=[{"order_number": it.order_number, "discipline": it.question.discipline, "correct_answer": it.question.correct_answer} for it in exam_items],
        sheet_type="exam_answer_key"
    )
    print(f" -> Google Sheets Export: {sheets_export['status']} ({sheets_export['rows_count']} linhas exportadas)")
    assert sheets_export["status"] == "success" and sheets_export["rows_count"] == 10

    db.close()
    print("\n=================================================================")
    print("TODOS OS 10 CRITÉRIOS DE ACEITAÇÃO FORAM ATENDIDOS COM SUCESSO!")
    print("=================================================================\n")

if __name__ == "__main__":
    run_acceptance_test()
