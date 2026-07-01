from fastapi import APIRouter
from ..models.schemas import ChatRequest, ChatResponse
from ..services.duckdb_service import get_db_service
from ..services.llm_service import get_llm_service
from ..services.database import save_message, get_chat_history, clear_chat_history
import math

router = APIRouter(prefix="/api/ai", tags=["ai"])


def sanitize_value(val):
    if val is None:
        return None
    if isinstance(val, float):
        if math.isnan(val) or math.isinf(val):
            return None
    return val


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Full chatbot flow:
    1. Save user message to history
    2. Send to Gemini
    3. If needs data → execute SQL → Gemini explains result
    4. Save assistant response to history
    """
    db = get_db_service()
    llm = get_llm_service()
    user_email = "admin@flash.com"  # MVP: hardcoded user

    # Save user message
    save_message(user_email, "user", request.question)

    # Get schema context
    schema_context = db.get_schema_info()

    # Let Gemini process the message
    result = llm.process_message(request.question, schema_context)

    # If it's just chat
    if result["type"] == "chat":
        save_message(user_email, "assistant", result["answer"])
        return ChatResponse(
            answer=result["answer"],
            sql=None,
            data=None,
        )

    # It's a data query — execute the SQL
    sql = result["sql"]
    try:
        df = db.execute_query(sql)
        columns = df.columns.tolist()
        rows = [
            [sanitize_value(cell) for cell in row]
            for row in df.head(50).values.tolist()
        ]

        # Create summary for Gemini to explain
        if len(df) <= 20:
            data_summary = df.to_string(index=False)
        else:
            data_summary = (
                f"Total de {len(df)} linhas. Primeiras 10:\n"
                + df.head(10).to_string(index=False)
            )

        # Get natural language explanation from Gemini
        explanation = llm.explain_data(request.question, data_summary)

        # Save assistant response
        save_message(user_email, "assistant", explanation, sql)

        return ChatResponse(
            answer=explanation,
            sql=sql,
            data={"columns": columns, "rows": rows},
        )

    except Exception as e:
        error_msg = f"Tentei buscar os dados mas encontrei um erro: {str(e)}. Pode reformular a pergunta?"
        save_message(user_email, "assistant", error_msg, sql)
        return ChatResponse(
            answer=error_msg,
            sql=sql,
            data=None,
        )


@router.get("/history")
async def get_history():
    """Get chat history for current user."""
    user_email = "admin@flash.com"
    history = get_chat_history(user_email)
    return {"messages": history}


@router.delete("/history")
async def delete_history():
    """Clear chat history for current user."""
    user_email = "admin@flash.com"
    clear_chat_history(user_email)
    return {"message": "Histórico limpo"}


@router.get("/insights")
async def get_insights():
    """Generate AI-powered insights from the data."""
    db = get_db_service()
    llm = get_llm_service()

    try:
        costs = db.execute_query(
            "SELECT STRFTIME(data_parsed, '%Y-%m') as mes, valor_clean as custo "
            "FROM contract_costs "
            "WHERE valor_clean > 0 ORDER BY data_parsed DESC LIMIT 6"
        )
        users = db.execute_query(
            "SELECT COUNT(*) as total, "
            "SUM(CASE WHEN is_active = 'true' THEN 1 ELSE 0 END) as active "
            "FROM dim_users"
        )

        summary = f"Custos recentes:\n{costs.to_string()}\n\nUsuários:\n{users.to_string()}"
        insights = llm.generate_insights(summary)

        return {"insights": insights}
    except Exception as e:
        return {"insights": f"Erro ao gerar insights: {str(e)}"}
