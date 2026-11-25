import sys
from pathlib import Path
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app.main import app
from backend.app.models import Question, User
from backend.app.database import SessionLocal, Base, engine
from backend.app.services.exam_builder import ExamBuilderService

def test_questions_per_discipline_selection():
    # Setup sample questions
    q_math1 = Question(id="m1", discipline="Matemática", statement="Math 1", validation_status="approved")
    q_math2 = Question(id="m2", discipline="Matemática", statement="Math 2", validation_status="approved")
    q_port1 = Question(id="p1", discipline="Português", statement="Port 1", validation_status="approved")
    q_port2 = Question(id="p2", discipline="Português", statement="Port 2", validation_status="approved")
    q_bio1 = Question(id="b1", discipline="Biologia", statement="Bio 1", validation_status="approved")

    questions = [q_math1, q_math2, q_port1, q_port2, q_bio1]

    # Select 1 from Math, 2 from Portuguese, 0 from Bio
    counts = {"Matemática": 1, "Português": 2, "Biologia": 0}
    selected = ExamBuilderService.select_questions_by_discipline_counts(questions, counts)

    # Assertions
    selected_math = [q for q in selected if q.discipline == "Matemática"]
    selected_port = [q for q in selected if q.discipline == "Português"]
    selected_bio = [q for q in selected if q.discipline == "Biologia"]

    assert len(selected_math) == 1
    assert len(selected_port) == 2
    assert len(selected_bio) == 0
    assert len(selected) == 3

    # Organize questions
    ordered = ExamBuilderService.organize_questions(selected, mode="by_discipline")
    assert len(ordered) == 3
    print("test_questions_per_discipline_selection: PASSED")

def test_rbac_roles_permissions():
    client = TestClient(app)

    # 1. Admin can build exam
    admin_headers = {"X-User-Role": "admin", "X-User-Email": "admin@escola.gov.br"}
    # Professor headers
    prof_headers = {"X-User-Role": "professor", "X-User-Email": "professor@escola.gov.br"}

    # Attempt to build exam as professor -> should be 403 Forbidden
    payload = {
        "title": "Avaliação Teste",
        "academic_period": "2026",
        "institution_name": "Colégio Teste",
        "organization_mode": "by_discipline",
        "show_discipline_header": True
    }

    res_prof = client.post("/api/exams/build", json=payload, headers=prof_headers)
    assert res_prof.status_code == 403, f"Expected 403 for professor, got {res_prof.status_code}: {res_prof.text}"
    print("test_rbac_professor_forbidden: PASSED")

    # Attempt drive sync as professor -> should be 403 Forbidden
    res_drive_prof = client.post("/api/google/drive/sync-exam/exam-123", headers=prof_headers)
    assert res_drive_prof.status_code == 403
    print("test_rbac_drive_professor_forbidden: PASSED")

    # Attempt sheets export as professor -> should be 403 Forbidden
    res_sheets_prof = client.post("/api/google/sheets/export-log", headers=prof_headers)
    assert res_sheets_prof.status_code == 403
    print("test_rbac_sheets_professor_forbidden: PASSED")

if __name__ == "__main__":
    test_questions_per_discipline_selection()
    test_rbac_roles_permissions()
    print("\nALL ROLE & QUESTION COUNT TESTS PASSED!")
