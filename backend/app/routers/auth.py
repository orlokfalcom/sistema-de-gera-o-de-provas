import hashlib
import hmac
import secrets
from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from backend.app.database import get_db
from backend.app.models import User
from backend.app.schemas import UserResponse, UserCreate, UserUpdate
from backend.app.services.google_service import GoogleWorkspaceService

router = APIRouter(prefix="/api/auth", tags=["Autenticação & Usuários"])

PBKDF2_ITERATIONS = 100_000


def hash_password_pbkdf2(password: str, salt_hex: Optional[str] = None) -> str:
    salt = bytes.fromhex(salt_hex) if salt_hex else secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return f"pbkdf2${PBKDF2_ITERATIONS}${salt.hex()}${dk.hex()}"


def verify_password_record(candidate: str, stored_value: Optional[str]) -> bool:
    if not stored_value:
        return False
    if stored_value.startswith("pbkdf2$"):
        parts = stored_value.split("$")
        if len(parts) != 4:
            return False
        iters = int(parts[1])
        salt = bytes.fromhex(parts[2])
        expected_hex = parts[3]
        dk = hashlib.pbkdf2_hmac("sha256", candidate.encode("utf-8"), salt, iters)
        return hmac.compare_digest(dk.hex(), expected_hex)
    # Legacy fallback before automatic upgrade on login
    return hmac.compare_digest(candidate, stored_value)

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

class AdminPasswordRequest(BaseModel):
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str
    role: str = "professor"
    discipline: Optional[str] = "Geral"
    admin_key: Optional[str] = None

@router.post("/login", response_model=UserResponse)
def login_with_credentials(req: LoginRequest, db: Session = Depends(get_db)):
    """Authenticates a user by email and PBKDF2-SHA256 password hash (auto-upgrading legacy records)."""
    email_clean = req.email.strip().lower()
    user = db.query(User).filter(User.email == email_clean).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos. Verifique suas credenciais."
        )

    if not verify_password_record(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos. Verifique suas credenciais."
        )

    # Auto-upgrade legacy non-PBKDF2 hash on successful login
    if user.password_hash and not user.password_hash.startswith("pbkdf2$"):
        user.password_hash = hash_password_pbkdf2(req.password)
        db.commit()
    return user

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_account(req: RegisterRequest, db: Session = Depends(get_db)):
    """Public self-registration for teachers and (with institutional key) coordinators."""
    email_clean = req.email.strip().lower()
    existing = db.query(User).filter(User.email == email_clean).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Já existe uma conta cadastrada com o e-mail '{email_clean}'."
        )

    role = req.role if req.role in ["admin", "professor"] else "professor"
    if role == "admin":
        admin_user = db.query(User).filter(User.role == "admin").first()
        valid_key = bool(req.admin_key) and (
            (admin_user and verify_password_record(req.admin_key, admin_user.password_hash))
            or verify_password_record(req.admin_key, hash_password_pbkdf2("admin123", "a1f09c4e7b2841d39e5c6082b47d1a9f"))
        )
        if not valid_key:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chave institucional administrativa inválida. Apenas a Coordenação pode criar contas Admin."
            )

    bg_color = "0284c7" if role == "admin" else "10b981"
    avatar_name = req.full_name.strip().replace(" ", "+")
    new_user = User(
        email=email_clean,
        full_name=req.full_name.strip(),
        role=role,
        discipline="Todas" if role == "admin" else (req.discipline or "Geral"),
        password_hash=hash_password_pbkdf2(req.password),
        picture_url=f"https://ui-avatars.com/api/?name={avatar_name}&background={bg_color}&color=fff"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/verify-admin")
def verify_admin_password(req: AdminPasswordRequest, db: Session = Depends(get_db)):
    """Validates administrative password via PBKDF2-SHA256."""
    admins = db.query(User).filter(User.role == "admin").all()
    bootstrap_admin_hash = hash_password_pbkdf2("admin123", "a1f09c4e7b2841d39e5c6082b47d1a9f")

    matched_admin = None
    for adm in admins:
        if verify_password_record(req.password, adm.password_hash):
            matched_admin = adm
            break

    if matched_admin or verify_password_record(req.password, bootstrap_admin_hash):
        primary = matched_admin or (admins[0] if admins else None)
        return {
            "valid": True,
            "role": "admin",
            "message": "Acesso administrativo concedido com sucesso.",
            "user": {
                "name": primary.full_name if primary else "Coordenador Pedagógico",
                "email": primary.email if primary else "admin@escola.gov.br",
                "role": "admin"
            }
        }
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Senha administrativa incorreta. O acesso de coordenação é restrito."
    )

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
    return db.query(User).order_by(User.created_at.asc()).all()

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Já existe um usuário cadastrado com o e-mail '{payload.email}'."
        )

    # Generate avatar if not provided
    avatar_url = payload.picture_url
    if not avatar_url:
        bg_color = "0284c7" if payload.role == "admin" else "10b981"
        encoded_name = payload.full_name.replace(" ", "+")
        avatar_url = f"https://ui-avatars.com/api/?name={encoded_name}&background={bg_color}&color=fff"

    raw_pwd = payload.password or ("admin123" if payload.role == "admin" else "prof123")
    hashed_pwd = raw_pwd if raw_pwd.startswith("pbkdf2$") else hash_password_pbkdf2(raw_pwd)

    new_user = User(
        email=payload.email,
        full_name=payload.full_name,
        role=payload.role if payload.role in ["admin", "professor"] else "professor",
        discipline=payload.discipline or "Geral",
        password_hash=hashed_pwd,
        picture_url=avatar_url
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    if payload.email and payload.email != target.email:
        conflict = db.query(User).filter(User.email == payload.email).first()
        if conflict:
            raise HTTPException(status_code=400, detail="Este e-mail já está em uso por outro usuário.")
        target.email = payload.email

    if payload.full_name is not None:
        target.full_name = payload.full_name
    if payload.role is not None and payload.role in ["admin", "professor"]:
        target.role = payload.role
    if payload.discipline is not None:
        target.discipline = payload.discipline
    if payload.picture_url is not None:
        target.picture_url = payload.picture_url
    if payload.password is not None:
        target.password_hash = payload.password if payload.password.startswith("pbkdf2$") else hash_password_pbkdf2(payload.password)

    db.commit()
    db.refresh(target)
    return target

@router.delete("/users/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    if target.id == current_user.id:
        raise HTTPException(status_code=400, detail="Você não pode excluir sua própria conta enquanto estiver conectado.")

    db.delete(target)
    db.commit()
    return {"status": "success", "message": f"Usuário '{target.full_name}' excluído com sucesso."}
