from fastapi import APIRouter, HTTPException
from ..models.schemas import QueryRequest, QueryResponse
from ..services.duckdb_service import get_db_service
import math

router = APIRouter(prefix="/api/queries", tags=["queries"])


def sanitize_value(val):
    """Convert NaN/Inf values to None for JSON serialization."""
    if val is None:
        return None
    if isinstance(val, float):
        if math.isnan(val) or math.isinf(val):
            return None
    return val


@router.post("/execute", response_model=QueryResponse)
async def execute_query(request: QueryRequest):
    """Execute a SQL query against duckdb"""
    db = get_db_service()

    # Basic SQL injection prevention for MVP
    dangerous_keywords = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE"]
    sql_upper = request.sql.upper().strip()
    for keyword in dangerous_keywords:
        if sql_upper.startswith(keyword):
            raise HTTPException(
                status_code=400,
                detail=f"Operação '{keyword}' não permitida. Apenas SELECT é aceito.",
            )

    try:
        df = db.execute_query(request.sql)
        columns = df.columns.tolist()
        rows = [
            [sanitize_value(cell) for cell in row]
            for row in df.values.tolist()
        ]
        return QueryResponse(columns=columns, rows=rows, row_count=len(rows))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/tables")
async def list_tables():
    """List all available tables"""
    db = get_db_service()
    df = db.execute_query("SHOW TABLES")
    return {"tables": df["name"].tolist()}


@router.get("/schema/{table_name}")
async def get_table_schema(table_name: str):
    """Get schema for a specific table"""
    db = get_db_service()
    try:
        df = db.execute_query(f"DESCRIBE {table_name}")
        return {
            "table": table_name,
            "columns": [
                {"name": row["column_name"], "type": row["column_type"]}
                for _, row in df.iterrows()
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Tabela não encontrada: {table_name}")
