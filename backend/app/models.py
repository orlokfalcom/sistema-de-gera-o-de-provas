import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, Integer, BigInteger, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base

def gen_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    picture_url = Column(Text, nullable=True)
    role = Column(String(50), nullable=False, default="professor")  # 'admin' or 'professor'
    discipline = Column(String(100), nullable=True, default="Geral")
    password_hash = Column(String(255), nullable=True, default="admin123")
    google_id = Column(String(255), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    documents = relationship("Document", back_populates="uploader")
    questions = relationship("Question", back_populates="creator")
    exams = relationship("Exam", back_populates="creator")

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    filename = Column(String(255), nullable=False)
    storage_path = Column(Text, nullable=False)
    uploaded_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    discipline = Column(String(100), nullable=False)
    target_grade = Column(String(50), default="Ensino Médio")
    academic_period = Column(String(50), default="Ano Letivo Corrente")
    status = Column(String(50), default="completed")  # uploaded, processing, completed, failed
    total_questions_found = Column(Integer, default=0)
    file_size_bytes = Column(BigInteger, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    uploader = relationship("User", back_populates="documents")
    questions = relationship("Question", back_populates="source_document", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = "questions"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    discipline = Column(String(100), nullable=False)
    target_grade = Column(String(50), default="3º Ano do Ensino Médio")  # '1º Ano do Ensino Médio', '2º Ano do Ensino Médio', '3º Ano do Ensino Médio'
    school_modality = Column(String(30), default="ambos")  # 'regular', 'integral', 'ambos'
    teacher_name = Column(String(255), nullable=True)
    question_type = Column(String(20), nullable=False, default="multiple_choice")  # 'multiple_choice' or 'discursive'
    statement = Column(Text, nullable=False)
    options_json = Column(JSON, nullable=True)  # {"A": "...", "B": "...", "C": "...", "D": "...", "E": "..."}
    correct_answer = Column(Text, nullable=True)  # "A", "B", ... or discursive rubric
    has_image = Column(Boolean, default=False)
    image_paths_json = Column(JSON, default=list)  # list of relative paths
    page_number = Column(Integer, default=1)
    difficulty = Column(String(20), default="medio")
    validation_status = Column(String(30), default="approved")  # 'approved', 'pending_review', 'rejected'
    validation_notes = Column(Text, nullable=True)
    is_duplicate = Column(Boolean, default=False)
    duplicate_of_id = Column(String(36), ForeignKey("questions.id"), nullable=True)
    source_filename = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    source_document = relationship("Document", back_populates="questions")
    creator = relationship("User", back_populates="questions")
    exam_items = relationship("ExamItem", back_populates="question")

class Exam(Base):
    __tablename__ = "exams"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    title = Column(String(255), nullable=False, default="Avaliação Geral Multidisciplinar")
    academic_period = Column(String(100), default="Ensino Médio")
    institution_name = Column(String(255), default="Colégio Integrado de Ensino Médio")
    organization_mode = Column(String(50), default="by_discipline")  # 'by_discipline', 'interleaved', 'random'
    school_modality = Column(String(50), default="integral")  # 'integral', 'regular', 'noturno'
    show_discipline_header = Column(Boolean, default=True)
    total_questions = Column(Integer, default=0)
    pdf_path = Column(Text, nullable=True)
    student_pdf_path = Column(Text, nullable=True)
    docx_path = Column(Text, nullable=True)
    answer_key_pdf_path = Column(Text, nullable=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User", back_populates="exams")
    items = relationship("ExamItem", back_populates="exam", cascade="all, delete-orphan", order_by="ExamItem.order_number")

class ExamItem(Base):
    __tablename__ = "exam_items"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    exam_id = Column(String(36), ForeignKey("exams.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(String(36), ForeignKey("questions.id"), nullable=False)
    order_number = Column(Integer, nullable=False)
    discipline_override = Column(String(100), nullable=True)

    exam = relationship("Exam", back_populates="items")
    question = relationship("Question", back_populates="exam_items")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
