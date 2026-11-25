import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.database import Base, engine, SessionLocal
from backend.app.models import User, Question, Document, Exam

client = TestClient(app)

def test_api_full_suite():
    print("==================================================")
    print("INICIANDO SUÍTE COMPLETA DE TESTES DE INTEGRAÇÃO DA API")
    print("==================================================")

    # 1. Test Root & Static Endpoints
    print("\n[TESTE 1] Endpoints Estáticos e PWA:")
    res_root = client.get("/")
    assert res_root.status_code == 200, f"Falha no root: {res_root.status_code}"
    print("  ✓ GET / (Root PWA HTML) -> 200 OK")

    res_manifest = client.get("/manifest.json")
    assert res_manifest.status_code == 200 and "application/manifest+json" in res_manifest.headers.get("content-type", "")
    print("  ✓ GET /manifest.json -> 200 OK")

    res_sw = client.get("/sw.js")
    assert res_sw.status_code == 200
    print("  ✓ GET /sw.js -> 200 OK")

    # 2. Test Auth Endpoints
    print("\n[TESTE 2] Módulo de Autenticação e Usuários:")
    res_login_admin = client.post("/api/auth/google", json={"token": "mock-google-token-admin", "role": "admin"})
    assert res_login_admin.status_code == 200
    admin_data = res_login_admin.json()
    assert admin_data["role"] == "admin"
    print(f"  ✓ POST /api/auth/google (Admin: {admin_data['email']}) -> 200 OK")

    res_login_prof = client.post("/api/auth/google", json={"token": "mock-google-token-prof", "role": "professor"})
    assert res_login_prof.status_code == 200
    prof_data = res_login_prof.json()
    assert prof_data["role"] == "professor"
    print(f"  ✓ POST /api/auth/google (Professor: {prof_data['email']}) -> 200 OK")

    res_users = client.get("/api/auth/users")
    assert res_users.status_code == 200 and len(res_users.json()) >= 2
    print(f"  ✓ GET /api/auth/users -> 200 OK ({len(res_users.json())} usuários)")

    # 3. Test Documents Upload with Real Sample PDFs
    print("\n[TESTE 3] Recebimento e Leitura de PDFs:")
    sample_files = [
        ("1_matematica.pdf", "Matemática"),
        ("2_portugues.pdf", "Português"),
        ("3_biologia.pdf", "Biologia"),
        ("4_historia.pdf", "História"),
        ("5_fisica.pdf", "Física")
    ]
    
    files_payload = []
    sample_dir = ROOT_DIR / "tests" / "sample_files"
    opened_files = []
    for fn, disc in sample_files:
        f_path = sample_dir / fn
        fp = open(f_path, "rb")
        opened_files.append(fp)
        files_payload.append(("files", (fn, fp, "application/pdf")))

    res_upload = client.post(
        "/api/documents/upload",
        files=files_payload,
        data={
            "teacher_name": "Professores Integrados",
            "academic_period": "2026 - 1º Bimestre",
            "target_grade": "3º Ano EM"
        }
    )
    for fp in opened_files:
        fp.close()

    assert res_upload.status_code == 200, f"Erro upload: {res_upload.text}"
    uploaded_docs = res_upload.json()
    assert len(uploaded_docs) == 5, f"Esperava 5 docs, veio {len(uploaded_docs)}"
    print(f"  ✓ POST /api/documents/upload -> 200 OK ({len(uploaded_docs)} documentos processados)")

    res_docs_list = client.get("/api/documents")
    assert res_docs_list.status_code == 200 and len(res_docs_list.json()) >= 5
    print(f"  ✓ GET /api/documents -> 200 OK ({len(res_docs_list.json())} cadastrados)")

    # 4. Test Question Bank & Pending Review
    print("\n[TESTE 4] Banco de Questões e Conferência:")
    res_questions = client.get("/api/questions")
    assert res_questions.status_code == 200
    q_list = res_questions.json()
    assert len(q_list) >= 10, f"Esperava >= 10 questões, veio {len(q_list)}"
    print(f"  ✓ GET /api/questions -> 200 OK ({len(q_list)} questões no banco)")

    # Filter by discipline
    res_mat = client.get("/api/questions?discipline=Matemática")
    assert res_mat.status_code == 200 and len(res_mat.json()) >= 2
    print(f"  ✓ GET /api/questions?discipline=Matemática -> 200 OK ({len(res_mat.json())} questões)")

    # Test pending questions endpoint
    res_pending = client.get("/api/questions/pending-review")
    assert res_pending.status_code == 200
    print(f"  ✓ GET /api/questions/pending-review -> 200 OK ({len(res_pending.json())} pendências)")

    # Test Question Patch & Approve
    first_q_id = q_list[0]["id"]
    res_patch = client.patch(f"/api/questions/{first_q_id}", json={"difficulty": "facil"})
    assert res_patch.status_code == 200
    print("  ✓ PATCH /api/questions/{id} -> 200 OK")

    res_approve = client.post(f"/api/questions/{first_q_id}/approve?correct_answer=A")
    assert res_approve.status_code == 200 and res_approve.json()["validation_status"] == "approved"
    print("  ✓ POST /api/questions/{id}/approve -> 200 OK")

    # 5. Test Exam Assembly & Generation (PDF/DOCX)
    print("\n[TESTE 5] Montagem Multidisciplinar e Geração de Provas:")
    exam_payload = {
        "title": "Avaliação Multidisciplinar Integrada Oficial",
        "academic_period": "2026 - 1º Bimestre",
        "institution_name": "Colégio Integrado de Ensino Médio",
        "organization_mode": "by_discipline",
        "show_discipline_header": True
    }
    res_build = client.post("/api/exams/build", json=exam_payload)
    assert res_build.status_code == 200, f"Erro ao montar prova: {res_build.text}"
    exam_data = res_build.json()
    exam_id = exam_data["id"]
    assert exam_data["total_questions"] >= 10
    print(f"  ✓ POST /api/exams/build -> 200 OK (Prova ID: {exam_id}, {exam_data['total_questions']} questões)")

    # Test Items list
    res_items = client.get(f"/api/exams/{exam_id}/items")
    assert res_items.status_code == 200
    items_data = res_items.json()
    assert len(items_data) == exam_data["total_questions"]
    # Check continuous numbering: 1, 2, ... N
    for idx, it in enumerate(items_data, start=1):
        assert it["order_number"] == idx, f"Ordem quebrada no item {idx}: {it['order_number']}"
    print(f"  ✓ GET /api/exams/{{id}}/items -> 200 OK (Numeração sequencial 01 a {len(items_data):02d} verificada)")

    # Test Downloads (Complete PDF, Student PDF, Answer Key PDF, DOCX)
    for file_type in ["pdf", "student_pdf", "answer_key_pdf", "docx"]:
        res_dl = client.get(f"/api/exams/{exam_id}/download/{file_type}")
        assert res_dl.status_code == 200, f"Falha download {file_type}: {res_dl.status_code}"
        assert len(res_dl.content) > 1000, f"Arquivo {file_type} gerado muito pequeno ({len(res_dl.content)} bytes)"
        print(f"  ✓ GET /api/exams/{{id}}/download/{file_type} -> 200 OK ({len(res_dl.content)} bytes)")

    # 6. Test Google Workspace Integration Endpoints
    print("\n[TESTE 6] Sincronização Google Workspace:")
    res_drive = client.post(f"/api/google/drive/sync-exam/{exam_id}")
    assert res_drive.status_code == 200 and res_drive.json()["status"] == "success"
    print(f"  ✓ POST /api/google/drive/sync-exam -> 200 OK (Pasta: {res_drive.json()['folder']})")

    res_sheets_log = client.post("/api/google/sheets/export-log")
    assert res_sheets_log.status_code == 200 and res_sheets_log.json()["status"] == "success"
    print("  ✓ POST /api/google/sheets/export-log -> 200 OK")

    res_sheets_ak = client.post(f"/api/google/sheets/export-answer-key/{exam_id}")
    assert res_sheets_ak.status_code == 200 and res_sheets_ak.json()["status"] == "success"
    print("  ✓ POST /api/google/sheets/export-answer-key -> 200 OK")

    res_gas = client.get("/api/google/apps-script-template")
    assert res_gas.status_code == 200 and "DriveApp" in res_gas.text
    print("  ✓ GET /api/google/apps-script-template -> 200 OK")

    # 7. Test Dashboard Metrics
    print("\n[TESTE 7] Dashboard & Métricas:")
    res_dash = client.get("/api/dashboard/metrics")
    assert res_dash.status_code == 200
    metrics = res_dash.json()
    assert metrics["total_documents"] >= 5
    assert metrics["total_questions"] >= 10
    assert metrics["total_disciplines"] >= 5
    assert metrics["total_exams"] >= 1
    print(f"  ✓ GET /api/dashboard/metrics -> 200 OK (Docs: {metrics['total_documents']}, Questões: {metrics['total_questions']}, Disciplinas: {metrics['total_disciplines']}, Provas: {metrics['total_exams']})")

    print("\n==================================================")
    print("TODOS OS 7 MÓDULOS DA API TESTADOS E 100% OPERACIONAIS!")
    print("==================================================")

if __name__ == "__main__":
    test_api_full_suite()
