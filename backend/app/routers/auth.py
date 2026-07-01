from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from jose import jwt
from ..config import get_settings
from ..models.schemas import LoginRequest, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Users storage POSTGRESQL
USERS = {
    "admin@flash.com": {
        "password": "flash123",
        "name": "Admin Flash",
        "role": "admin",
    },
    "viewer@flash.com": {
        "password": "flash123",
        "name": "Viewer Flash",
        "role": "viewer",
    },
    "yasmin.rocha": {
        "password": "123456",
        "name": "Yasmin Rocha",
        "role": "admin",
    },
}


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
    """Register user"""
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
    """List all registered users without passwords"""
    return {
        "users": [
            {"email": email, "name": u["name"], "role": u["role"]}
            for email, u in USERS.items()
        ]
    }
