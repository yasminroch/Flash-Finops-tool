from pydantic import BaseModel
from typing import Optional, Any


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class QueryRequest(BaseModel):
    sql: str


class QueryResponse(BaseModel):
    columns: list[str]
    rows: list[list[Any]]
    row_count: int


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    sql: Optional[str] = None
    data: Optional[dict] = None


class DashboardMetrics(BaseModel):
    total_users: int
    active_users: int
    idle_users: int
    total_cost_current_month: str
    cost_trend: list[dict]
    users_by_department: list[dict]
    activity_timeline: list[dict]
    idle_users_detail: list[dict]
