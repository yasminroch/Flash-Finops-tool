import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from jose import jwt
from ..config import get_settings

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _load_users() -> dict:
    """Load users from environment variable."""
    settings = get_settings()
    try:
        return json.loads(settings.default_users)
    except (json.JSONDecodeError, TypeError):
        return {"admin@flash.com": {"password": "flash123", "name": "Admin", "role": "admin"}}


# Mutable users dict (loaded from env on startup, new registrations added at runtime)
USERS = _load_users()


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    role: str = "viewer"


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    user = USERS.get(request.email)
    if not user or user["password"] != request.password:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expiration_hours)

    token_data = {
        "sub": request.email,
        "name": user["name"],
        "role": user["role"],
        "exp": expire,
    }

    access_token = jwt.encode(
        token_data, settings.jwt_secret, algorithm=settings.jwt_algorithm
    )

    return TokenResponse(
        access_token=access_token,
        user={"email": request.email, "name": user["name"], "role": user["role"]},
    )


@router.post("/register")
async def register(request: RegisterRequest):
    """Register a new user (runtime only, not persisted to env)."""
    if request.email in USERS:
        raise HTTPException(status_code=400, detail="Usuário já existe")

    USERS[request.email] = {
        "password": request.password,
        "name": request.name,
        "role": request.role,
    }

    return {"message": f"Usuário '{request.name}' criado com sucesso!", "email": request.email}


@router.get("/users")
async def list_users():
    """List all registered users (without passwords)."""
    return {
        "users": [
            {"email": email, "name": u["name"], "role": u["role"]}
            for email, u in USERS.items()
        ]
    }
