from sqlalchemy import text
from backend.app.database import engine, Base, SessionLocal
from backend.app.models import User, Document, Question, Exam, ExamItem, AuditLog

def run_migrations():
    """Ensures SQLite tables have newly added columns dynamically."""
    with engine.connect() as conn:
        try:
            res = conn.execute(text("PRAGMA table_info(users)"))
            cols = [row[1] for row in res.fetchall()]
            if "discipline" not in cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN discipline VARCHAR(100) DEFAULT 'Geral'"))
            if "password_hash" not in cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) DEFAULT 'admin123'"))

            # Check exams columns
            res_exams = conn.execute(text("PRAGMA table_info(exams)"))
            exam_cols = [row[1] for row in res_exams.fetchall()]
            if "school_modality" not in exam_cols:
                conn.execute(text("ALTER TABLE exams ADD COLUMN school_modality VARCHAR(50) DEFAULT 'integral'"))
            conn.commit()
        except Exception:
            pass

def init_database():
    Base.metadata.create_all(bind=engine)
    run_migrations()
    db = SessionLocal()
    # Check if admin exists
    admin = db.query(User).filter(User.email == "admin@escola.gov.br").first()
    if not admin:
        admin = User(
            id="admin-001",
            email="admin@escola.gov.br",
            full_name="Coordenador Pedagógico (Admin)",
            role="admin",
            discipline="Todas",
            picture_url="https://ui-avatars.com/api/?name=Admin+Escolar&background=0284c7&color=fff"
        )
        db.add(admin)
    # Check if sample teachers exist
    teacher = db.query(User).filter(User.email == "professor@escola.gov.br").first()
    if not teacher:
        teacher = User(
            id="teacher-001",
            email="professor@escola.gov.br",
            full_name="Prof. Carlos Silva",
            role="professor",
            discipline="Matemática",
            picture_url="https://ui-avatars.com/api/?name=Carlos+Silva&background=10b981&color=fff"
        )
        db.add(teacher)

    teacher2 = db.query(User).filter(User.email == "mariana@escola.gov.br").first()
    if not teacher2:
        teacher2 = User(
            id="teacher-002",
            email="mariana@escola.gov.br",
            full_name="Profª. Mariana Santos",
            role="professor",
            discipline="Português",
            picture_url="https://ui-avatars.com/api/?name=Mariana+Santos&background=6366f1&color=fff"
        )
        db.add(teacher2)

    teacher3 = db.query(User).filter(User.email == "henrique@escola.gov.br").first()
    if not teacher3:
        teacher3 = User(
            id="teacher-003",
            email="henrique@escola.gov.br",
            full_name="Prof. Henrique Lima",
            role="professor",
            discipline="Robótica e Inteligência Artificial",
            picture_url="https://ui-avatars.com/api/?name=Henrique+Lima&background=f59e0b&color=fff"
        )
        db.add(teacher3)
    db.commit()
    db.close()
    print("Database initialized successfully with default admin and teacher accounts.")

if __name__ == "__main__":
    init_database()
