from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: str
    full_name: str
    picture_url: Optional[str] = None
    role: str = "professor"
    discipline: Optional[str] = "Geral"

class UserCreate(UserBase):
    password: Optional[str] = "admin123"

class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    discipline: Optional[str] = None
    picture_url: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: str
    created_at: datetime
    class Config:
        from_attributes = True

class QuestionBase(BaseModel):
    discipline: str
    teacher_name: Optional[str] = "Professor(a)"
    question_type: str = "multiple_choice"
    statement: str
    options_json: Optional[Dict[str, str]] = None
    correct_answer: Optional[str] = None
    has_image: bool = False
    image_paths_json: List[str] = []
    page_number: int = 1
    difficulty: str = "medio"
    validation_status: str = "approved"
    validation_notes: Optional[str] = None
    source_filename: Optional[str] = None

class QuestionCreate(QuestionBase):
    document_id: Optional[str] = None

class QuestionUpdate(BaseModel):
    discipline: Optional[str] = None
    statement: Optional[str] = None
    options_json: Optional[Dict[str, str]] = None
    correct_answer: Optional[str] = None
    validation_status: Optional[str] = None
    validation_notes: Optional[str] = None

class QuestionResponse(QuestionBase):
    id: str
    document_id: Optional[str]
    created_by: Optional[str]
    is_duplicate: bool
    created_at: datetime
    class Config:
        from_attributes = True

class DocumentResponse(BaseModel):
    id: str
    filename: str
    discipline: str
    target_grade: Optional[str]
    academic_period: Optional[str]
    status: str
    total_questions_found: int
    file_size_bytes: int
    created_at: datetime
    class Config:
        from_attributes = True

class ExamBuildRequest(BaseModel):
    title: str = "Avaliação Geral Multidisciplinar do Ensino Médio"
    academic_period: str = "2026 - Ensino Médio"
    institution_name: str = "Colégio Integrado de Ensino Médio"
    organization_mode: str = "by_discipline" # by_discipline, interleaved, random
    show_discipline_header: bool = True
    question_ids: Optional[List[str]] = None # If None, uses all approved questions
    questions_per_discipline: Optional[Dict[str, int]] = None # Optional custom count per discipline

class ExamResponse(BaseModel):
    id: str
    title: str
    academic_period: str
    institution_name: str
    organization_mode: str
    show_discipline_header: bool
    total_questions: int
    pdf_path: Optional[str]
    student_pdf_path: Optional[str]
    docx_path: Optional[str]
    answer_key_pdf_path: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True
