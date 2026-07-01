from fastapi import APIRouter, UploadFile, File, HTTPException
from ..services.duckdb_service import get_db_service
from ..services.database import save_uploaded_dataset, get_uploaded_datasets
import pandas as pd
import io
import re

router = APIRouter(prefix="/api/data", tags=["data"])


def sanitize_table_name(filename: str) -> str:
    """Convert filename to a valid SQL table name."""
    name = filename.rsplit(".", 1)[0]  # Remove extension
    name = re.sub(r'[^a-zA-Z0-9_]', '_', name)  # Replace special chars
    name = re.sub(r'_+', '_', name)  # Collapse multiple underscores
    name = name.strip('_').lower()
    if name[0].isdigit():
        name = "t_" + name
    return name


@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Upload a CSV file and make it available as a DuckDB table."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Apenas arquivos .csv são aceitos")

    try:
        # Read the CSV
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        if df.empty:
            raise HTTPException(status_code=400, detail="O arquivo CSV está vazio")

        # Create table name from filename
        table_name = sanitize_table_name(file.filename)

        # Load into DuckDB
        db = get_db_service()
        db.load_dataframe(table_name, df)

        # Record in PostgreSQL
        columns_str = ", ".join(df.columns.tolist())
        save_uploaded_dataset(
            filename=file.filename,
            table_name=table_name,
            row_count=len(df),
            columns=columns_str,
            user_email="admin@flash.com"
        )

        return {
            "message": f"Arquivo '{file.filename}' carregado com sucesso!",
            "table_name": table_name,
            "row_count": len(df),
            "columns": df.columns.tolist(),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")


@router.get("/datasets")
async def list_datasets():
    """List all uploaded datasets."""
    datasets = get_uploaded_datasets()
    return {"datasets": datasets}


@router.get("/tables")
async def list_all_tables():
    """List all tables available in DuckDB (original + uploaded)."""
    db = get_db_service()
    df = db.execute_query("SHOW TABLES")
    tables = []
    for table_name in df["name"].tolist():
        try:
            count_df = db.execute_query(f"SELECT COUNT(*) as cnt FROM {table_name}")
            count = int(count_df.iloc[0]["cnt"])
        except:
            count = 0
        tables.append({"name": table_name, "row_count": count})
    return {"tables": tables}
