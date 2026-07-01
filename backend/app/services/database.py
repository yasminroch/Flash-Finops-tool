import psycopg2
import psycopg2.extras
from datetime import datetime, timezone
from ..config import get_settings
import time


def get_connection():
    """Get a PostgreSQL connection."""
    settings = get_settings()
    return psycopg2.connect(settings.database_url)


def init_db():
    """Initialize database tables. Retries on connection failure."""
    max_retries = 10
    for attempt in range(max_retries):
        try:
            conn = get_connection()
            cur = conn.cursor()

            # Chat history table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id SERIAL PRIMARY KEY,
                    user_email VARCHAR(255) NOT NULL DEFAULT 'admin@flash.com',
                    role VARCHAR(20) NOT NULL,
                    content TEXT NOT NULL,
                    sql_query TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)

            # Uploaded datasets table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS uploaded_datasets (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    table_name VARCHAR(255) NOT NULL,
                    row_count INTEGER DEFAULT 0,
                    columns TEXT,
                    uploaded_by VARCHAR(255) DEFAULT 'admin@flash.com',
                    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)

            conn.commit()
            cur.close()
            conn.close()
            print("[DB] Database initialized successfully")
            return
        except Exception as e:
            print(f"[DB] Connection attempt {attempt+1}/{max_retries} failed: {e}")
            time.sleep(2)

    print("[DB] WARNING: Could not initialize database after retries")


def save_message(user_email: str, role: str, content: str, sql_query: str = None):
    """Save a chat message to history."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO chat_history (user_email, role, content, sql_query) VALUES (%s, %s, %s, %s)",
            (user_email, role, content, sql_query)
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[DB] Error saving message: {e}")


def get_chat_history(user_email: str, limit: int = 50) -> list:
    """Get chat history for a user."""
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            "SELECT role, content, sql_query, created_at FROM chat_history "
            "WHERE user_email = %s ORDER BY created_at ASC LIMIT %s",
            (user_email, limit)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [
            {
                "role": r["role"],
                "content": r["content"],
                "sql": r["sql_query"],
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
            }
            for r in rows
        ]
    except Exception as e:
        print(f"[DB] Error getting history: {e}")
        return []


def clear_chat_history(user_email: str):
    """Clear chat history for a user."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM chat_history WHERE user_email = %s", (user_email,))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[DB] Error clearing history: {e}")


def save_uploaded_dataset(filename: str, table_name: str, row_count: int, columns: str, user_email: str):
    """Record an uploaded dataset."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO uploaded_datasets (filename, table_name, row_count, columns, uploaded_by) "
            "VALUES (%s, %s, %s, %s, %s)",
            (filename, table_name, row_count, columns, user_email)
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[DB] Error saving dataset record: {e}")


def get_uploaded_datasets() -> list:
    """Get list of uploaded datasets."""
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM uploaded_datasets ORDER BY uploaded_at DESC")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [
            {
                "id": r["id"],
                "filename": r["filename"],
                "table_name": r["table_name"],
                "row_count": r["row_count"],
                "columns": r["columns"],
                "uploaded_at": r["uploaded_at"].isoformat() if r["uploaded_at"] else None,
            }
            for r in rows
        ]
    except Exception as e:
        print(f"[DB] Error getting datasets: {e}")
        return []
