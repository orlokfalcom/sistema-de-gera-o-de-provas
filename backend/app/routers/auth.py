from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from backend.app.database import get_db
from backend.app.models import User
from backend.app.schemas import UserResponse
from backend.app.services.google_service import GoogleWorkspaceService

router = APIRouter(prefix="/api/auth", tags=["Autenticação & Usuários"])

def get_current_user_from_headers(
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
    x_user_email: Optional[str] = Header(None, alias="X-User-Email"),
    db: Session = Depends(get_db)
) -> User:
    """Resolves active user from HTTP headers or defaults gracefully to admin."""
    if x_user_email:
        user = db.query(User).filter(User.email == x_user_email).first()
        if user:
            return user
        role = x_user_role if x_user_role in ["admin", "professor"] else "professor"
        return User(id=f"user-{role}", email=x_user_email, full_name="Usuário", role=role)

    if x_user_role:
        user = db.query(User).filter(User.role == x_user_role).first()
        if user:
            return user
        return User(id=f"user-{x_user_role}", email=f"{x_user_role}@escola.gov.br", full_name="Usuário", role=x_user_role)

    # Fallback default admin
    admin = db.query(User).filter(User.role == "admin").first()
    if admin:
        return admin
    user = db.query(User).first()
    if user:
        return user
    return User(id="admin-default", email="admin@escola.gov.br", full_name="Coordenador Pedagógico", role="admin")

def require_admin(
    current_user: User = Depends(get_current_user_from_headers)
) -> User:
    """Enforces Admin role for operations restricted to pedagogical direction."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito: Esta operação requer privilégios de Administrador / Coordenação Pedagógica."
        )
    return current_user

class GoogleLoginRequest(BaseModel):
    token: str
    role: Optional[str] = None

@router.post("/google", response_model=UserResponse)
def login_with_google(req: GoogleLoginRequest, db: Session = Depends(get_db)):
    service = GoogleWorkspaceService()
    profile = service.verify_google_token_or_mock(req.token)
    
    # Override role if requested during testing/demo
    role = req.role if req.role in ["admin", "professor"] else profile.get("role", "professor")
    
    user = db.query(User).filter(User.email == profile["email"]).first()
    if not user:
        user = User(
            email=profile["email"],
            full_name=profile["name"],
            picture_url=profile.get("picture"),
            role=role,
            google_id=profile.get("sub")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Update role if changed
        if req.role and user.role != req.role:
            user.role = req.role
            db.commit()
            db.refresh(user)
            
    return user

@router.get("/me", response_model=UserResponse)
def get_current_user(email: str = "admin@escola.gov.br", db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return user

@router.get("/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()
