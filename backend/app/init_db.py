from backend.app.database import engine, Base, SessionLocal
from backend.app.models import User, Document, Question, Exam, ExamItem, AuditLog

def init_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Check if admin exists
    admin = db.query(User).filter(User.email == "admin@escola.gov.br").first()
    if not admin:
        admin = User(
            id="admin-001",
            email="admin@escola.gov.br",
            full_name="Coordenador Pedagógico (Admin)",
            role="admin",
            picture_url="https://ui-avatars.com/api/?name=Admin+Escolar&background=0284c7&color=fff"
        )
        db.add(admin)
    # Check if a sample teacher exists
    teacher = db.query(User).filter(User.email == "professor@escola.gov.br").first()
    if not teacher:
        teacher = User(
            id="teacher-001",
            email="professor@escola.gov.br",
            full_name="Prof. Carlos Silva",
            role="professor",
            picture_url="https://ui-avatars.com/api/?name=Carlos+Silva&background=10b981&color=fff"
        )
        db.add(teacher)
    db.commit()
    db.close()
    print("Database initialized successfully with default admin and teacher accounts.")

if __name__ == "__main__":
    init_database()
