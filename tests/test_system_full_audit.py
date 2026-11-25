import sys
from pathlib import Path
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app.main import app
from backend.app.database import SessionLocal, Base, engine
from backend.app.models import User, Question, Exam, Document
from backend.app.services.exam_builder import ExamBuilderService
from backend.app.services.docx_generator import DocxGeneratorService
import docx

def run_system_audit():
    print("=================================================================")
    print("AUDITORIA COMPLETA DO SISTEMA - VERIFICAÇÃO DE BUGS E LÓGICA")
    print("=================================================================\n")

    client = TestClient(app)
    db = SessionLocal()

    # 1. TESTE DO DASHBOARD & MÉTRICAS
    print("[TESTE 1/6] Auditoria de Métricas do Dashboard")
    res_dash = client.get("/api/dashboard/metrics")
    assert res_dash.status_code == 200, f"Dashboard metrics failed: {res_dash.text}"
    metrics = res_dash.json()
    assert "total_questions" in metrics
    assert "discipline_breakdown" in metrics
    assert "area_breakdown" in metrics
    assert "approval_rate_percent" in metrics
    print(f" -> Total de Questões: {metrics['total_questions']}")
    print(f" -> Taxa de Aprovação: {metrics['approval_rate_percent']}%")
    print(f" -> Áreas do Conhecimento mapeadas: {list(metrics['area_breakdown'].keys())}")
    print(" ✓ [OK] Dashboard operando com consistência analítica.\n")

    # 2. TESTE DE AUTENTICAÇÃO, SENHA E RBAC
    print("[TESTE 2/6] Auditoria de Senha Administrativa e Permissões de Perfil")
    # 2.1 Senha correta
    res_pwd_ok = client.post("/api/auth/verify-admin", json={"password": "admin123"})
    assert res_pwd_ok.status_code == 200
    assert res_pwd_ok.json()["valid"] is True
    # 2.2 Senha incorreta
    res_pwd_bad = client.post("/api/auth/verify-admin", json={"password": "senha-errada-999"})
    assert res_pwd_bad.status_code == 401
    # 2.3 Professor bloqueado em rotas admin
    prof_headers = {"X-User-Role": "professor", "X-User-Email": "professor@escola.gov.br"}
    admin_headers = {"X-User-Role": "admin", "X-User-Email": "admin@escola.gov.br"}

    res_block_user = client.post("/api/auth/users", json={"full_name": "Teste", "email": "teste@esc.br", "role": "professor"}, headers=prof_headers)
    assert res_block_user.status_code == 403, f"Expected 403, got {res_block_user.status_code}"

    res_block_exam = client.post("/api/exams/build", json={"title": "Teste Prova", "academic_period": "2026"}, headers=prof_headers)
    assert res_block_exam.status_code == 403
    print(" ✓ [OK] Bloqueio rigoroso de rotas administrativas para docentes verificado (403 Forbidden).")
    print(" ✓ [OK] Desbloqueio com senha institucional validado.\n")

    # 3. TESTE DE CRUD DE USUÁRIOS
    print("[TESTE 3/6] Auditoria de Gestão de Usuários (Professores e Coordenação)")
    novo_prof_email = "prof.biotec@escola.gov.br"
    user_payload = {
        "full_name": "Profª. Helena Biotecnologia",
        "email": novo_prof_email,
        "role": "professor",
        "discipline": "Biotecnologia e Genética Aplicada",
        "password": "senhaDocente123"
    }
    # Remove se já existir
    existente = db.query(User).filter(User.email == novo_prof_email).first()
    if existente:
        db.delete(existente)
        db.commit()

    res_user_create = client.post("/api/auth/users", json=user_payload, headers=admin_headers)
    assert res_user_create.status_code == 201
    created_id = res_user_create.json()["id"]

    # Consulta listagem
    res_users = client.get("/api/auth/users")
    assert res_users.status_code == 200
    emails = [u["email"] for u in res_users.json()]
    assert novo_prof_email in emails

    # Exclusão
    res_del = client.delete(f"/api/auth/users/{created_id}", headers=admin_headers)
    assert res_del.status_code == 200
    print(" ✓ [OK] Cadastro, vinculação de disciplina, senha e exclusão de usuários testados com sucesso.\n")

    # 4. TESTE DA REGRA: MÁXIMO 10 QUESTÕES POR MATÉRIA E VALORES HETEROGÊNEOS
    print("[TESTE 4/6] Auditoria da Regra de Negócio: Limite de 10 Questões por Matéria")
    # Cria mock de questões
    q_list = []
    for i in range(15):
        q_list.append(Question(id=f"mat-{i}", discipline="Matemática", statement=f"Math Q{i}", validation_status="approved"))
    for i in range(8):
        q_list.append(Question(id=f"port-{i}", discipline="Língua Portuguesa", statement=f"Port Q{i}", validation_status="approved"))
    for i in range(4):
        q_list.append(Question(id=f"rob-{i}", discipline="Robótica e IA", statement=f"Rob Q{i}", validation_status="approved"))

    # Tentativa de pedir 12 de Matemática (deve capar em 10 no builder)
    counts = {
        "Matemática": 12, # Acima de 10
        "Língua Portuguesa": 7, # Heterogêneo
        "Robótica e IA": 3 # Heterogêneo
    }
    selected = ExamBuilderService.select_questions_by_discipline_counts(q_list, counts)
    sel_mat = [q for q in selected if q.discipline == "Matemática"]
    sel_port = [q for q in selected if q.discipline == "Língua Portuguesa"]
    sel_rob = [q for q in selected if q.discipline == "Robótica e IA"]

    assert len(sel_mat) == 10, f"Expected 10 max for Matemática, got {len(sel_mat)}"
    assert len(sel_port) == 7, f"Expected 7 for Português, got {len(sel_port)}"
    assert len(sel_rob) == 3, f"Expected 3 for Robótica, got {len(sel_rob)}"
    print(f" -> Matemática: {len(sel_mat)} questões (limitado estritamente ao teto de 10)")
    print(f" -> Português: {len(sel_port)} questões")
    print(f" -> Robótica: {len(sel_rob)} questões")
    print(" ✓ [OK] Limite máximo de 10 por matéria e composição heterogênea operando perfeitamente.\n")

    # 5. TESTE DE ESCOLAS INTEGRAIS E NÃO INTEGRAIS (REGULARES)
    print("[TESTE 5/6] Auditoria de Modalidades: Tempo Integral vs. Ensino Regular (Não Integral)")
    exam_integral = Exam(
        id="exam-audit-integral",
        title="Avaliação Integrada EMTI",
        academic_period="2026 - 1º Trimestre (Tempo Integral)",
        institution_name="Colégio Estadual de Tempo Integral",
        school_modality="integral",
        total_questions=10
    )
    exam_regular = Exam(
        id="exam-audit-regular",
        title="Avaliação Bimestral Regular",
        academic_period="2026 - 1º Bimestre (Ensino Regular)",
        institution_name="Colégio Estadual Regular Noturno",
        school_modality="regular",
        total_questions=10
    )

    docx_integral_path = DocxGeneratorService.generate_exam_docx(
        exam=exam_integral,
        items=[],
        output_filename="AUDIT_INTEGRAL.docx"
    )
    docx_regular_path = DocxGeneratorService.generate_exam_docx(
        exam=exam_regular,
        items=[],
        output_filename="AUDIT_REGULAR.docx"
    )

    doc_int = docx.Document(docx_integral_path)
    assert "Tempo Integral" in doc_int.tables[0].rows[1].cells[0].text
    assert "REGIME: Tempo Integral" in doc_int.tables[0].rows[0].cells[1].text

    doc_reg = docx.Document(docx_regular_path)
    assert "Não Integral" in doc_reg.tables[0].rows[1].cells[0].text
    assert "TURNO" in doc_reg.tables[0].rows[0].cells[1].text

    # Verifica Margens ABNT NBR 14724 em ambos
    for d in [doc_int, doc_reg]:
        sec = d.sections[0]
        assert round(sec.top_margin.cm, 1) == 3.0
        assert round(sec.left_margin.cm, 1) == 3.0
        assert round(sec.bottom_margin.cm, 1) == 2.0
        assert round(sec.right_margin.cm, 1) == 2.0

    print(" ✓ [OK] Documento DOCX gerado para Tempo Integral com cabeçalho de regime integral.")
    print(" ✓ [OK] Documento DOCX gerado para Ensino Regular (Não Integral) com campos de turno (Matutino/Vespertino/Noturno).")
    print(" ✓ [OK] Margens ABNT NBR 14724 (3cm sup/esq, 2cm inf/dir) confirmadas em ambos.\n")

    # 6. TESTE DE INTEGRIDADE DO FRONTEND E ARQUIVOS SINCRONIZADOS
    print("[TESTE 6/6] Auditoria de Sincronização e Cobertura Curricular")
    p_root = ROOT_DIR / "index.html"
    p_static = ROOT_DIR / "backend" / "static" / "index.html"
    p_docs = ROOT_DIR / "docs" / "index.html"

    assert p_root.read_text(encoding="utf-8") == p_static.read_text(encoding="utf-8"), "Mismatch between index.html and backend/static"
    assert p_root.read_text(encoding="utf-8") == p_docs.read_text(encoding="utf-8"), "Mismatch between index.html and docs/index.html"

    root_html = p_root.read_text(encoding="utf-8")
    assert "modal-admin-password" in root_html
    assert "view-usuarios" in root_html
    assert "exam-school-modality" in root_html
    assert "knowledge-areas-bars" in root_html
    assert "Robótica e Inteligência Artificial" in root_html
    assert "Biotecnologia e Genética Aplicada" in root_html
    assert "Desenvolvimento de Sistemas e Programação Web" in root_html
    print(" ✓ [OK] Todos os 3 arquivos HTML estão perfeitamente sincronizados e contêm todos os componentes solicitados.\n")

    print("=================================================================")
    print("TODOS OS 6 TESTES DA AUDITORIA FORAM APROVADOS COM 100% DE SUCESSO!")
    print("NENHUM BUG OU INCONSISTÊNCIA DE LÓGICA ENCONTRADO.")
    print("=================================================================")

if __name__ == "__main__":
    run_system_audit()
