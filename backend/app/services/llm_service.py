import httpx
from ..config import get_settings

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

SYSTEM_INSTRUCTION = """Você é o assistente de dados da Flash, uma plataforma de BI interna.
Você é simpático, inteligente e responde em português brasileiro.

Você tem acesso a dados de licenças do Metabase da empresa. O schema das tabelas disponíveis é:

{schema_context}

COMO FUNCIONAR:
- Se o usuário fizer uma pergunta que pode ser respondida com dados das tabelas acima, responda com o prefixo EXATO "###SQL###" seguido do SQL na primeira linha, e nada mais. Exemplo:
  ###SQL###
  SELECT department, COUNT(*) as total FROM dim_users GROUP BY department

- Se o usuário fizer uma pergunta casual, saudação, ou qualquer coisa que NÃO precise de consulta aos dados, responda normalmente como um chatbot amigável. NÃO use o prefixo ###SQL### nesse caso.

- IMPORTANTE: Quando gerar SQL, gere APENAS o SQL após ###SQL###. Sem explicações, sem markdown.

Regras para SQL (DuckDB):
- valor_clean = custo em reais (float)
- data_parsed = data do custo (timestamp) na tabela contract_costs
- date_parsed = data de atividade (timestamp) na tabela user_activity
- is_active = 'true'/'false' (string)
- Use STRFTIME(coluna, '%Y-%m') para formatar datas
- Use CAST para conversões
"""

EXPLAIN_PROMPT = """Você é o assistente de dados da Flash. O usuário perguntou: "{question}"

Você executou uma query SQL e obteve estes resultados:
{data_summary}

Agora responda ao usuário de forma clara, em português, explicando o que os dados mostram. 
Seja conciso mas informativo. Use números relevantes dos dados.
Se os dados forem uma tabela grande, destaque os pontos mais importantes.
Não mostre o SQL na resposta — foque na resposta humana.
"""


class LLMService:
    """Gemini chatbot with data access"""

    def __init__(self):
        settings = get_settings()
        self._api_key = settings.gemini_api_key
        if self._api_key:
            print(f"[LLM] Gemini API key configured (length: {len(self._api_key)})")
        else:
            print("[LLM] WARNING: No Gemini API key configured!")

    def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API directly via HTTP."""
        if not self._api_key:
            print("[LLM] No API key, skipping Gemini call")
            return ""

        url = f"{GEMINI_API_URL}?key={self._api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 2048,
            },
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=payload)

                if response.status_code != 200:
                    print(f"[LLM] Gemini API error {response.status_code}: {response.text[:200]}")
                    return ""

                data = response.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        text = parts[0].get("text", "").strip()
                        print(f"[LLM] Gemini response (first 100 chars): {text[:100]}")
                        return text

                print(f"[LLM] No candidates in response: {data}")
                return ""

        except Exception as e:
            print(f"[LLM] Gemini API exception: {e}")
            return ""

    def process_message(self, question: str, schema_context: str) -> dict:
        """
        Process user message through Gemini
        Should returns: {"type": "chat"|"data", "answer": str, "sql": str|None, "data": dict|None}
        """
        # Step 1- ask Gemini what to do with this message
        prompt = SYSTEM_INSTRUCTION.format(schema_context=schema_context) + f"\n\nUsuário: {question}"
        response = self._call_gemini(prompt)

        if not response:
            # if API failed use smart fallback instead of error message
            return self._smart_fallback(question)

        # Step 2 - check if Gemini wants to query data
        if "###SQL###" in response:
            sql = response.split("###SQL###")[1].strip()
            # Clean any leftover markdown
            sql = sql.replace("```sql", "").replace("```", "").strip()
            return {"type": "data", "sql": sql, "answer": None, "data": None}

        # Step 3 - a conversational response
        return {
            "type": "chat",
            "answer": response,
            "sql": None,
            "data": None,
        }

    def explain_data(self, question: str, data_summary: str) -> str:
        """Ask Gemini to explain query results in natural language NLP"""
        prompt = EXPLAIN_PROMPT.format(question=question, data_summary=data_summary)
        response = self._call_gemini(prompt)
        return response if response else "Aqui estão os dados que encontrei."

    def generate_insights(self, data_summary: str) -> str:
        """Generate insights from data"""
        prompt = (
            "Você é um analista de FinOps da Flash. Analise esses dados de licenças "
            "Metabase e destaque as 3 mudanças mais relevantes. "
            "Responda em português, de forma concisa.\n\n"
            f"Dados:\n{data_summary}"
        )
        result = self._call_gemini(prompt)
        return result if result else "Configure a API key do Gemini para gerar insights automáticos."

    def _smart_fallback(self, question: str) -> dict:
        """Smart fallback when Gemini API is unavailable"""
        q = question.lower().strip()

        # Greetings
        greetings = ["oi", "olá", "ola", "hey", "bom dia", "boa tarde", "boa noite",
                     "tudo bem", "hello", "hi", "e aí", "eai", "fala"]
        if any(q.startswith(g) or q == g for g in greetings):
            return {
                "type": "chat",
                "answer": "Olá! 👋 Sou o assistente da Flash Analytics. No momento estou operando em modo offline (sem conexão com o Gemini), mas ainda posso te ajudar com consultas pré-definidas sobre custos, usuários e atividade. O que precisa?",
                "sql": None,
                "data": None,
            }

        # About itself
        if any(w in q for w in ["que api", "quem é", "o que faz", "como funciona", "que modelo"]):
            return {
                "type": "chat",
                "answer": "Sou o assistente da Flash Analytics, powered by Gemini 2.5 Flash. Consulto dados de licenças Metabase (custos, usuários, atividade) e respondo em linguagem natural. ⚠️ No momento a API do Gemini não está respondendo — verifique se a key está correta no .env (formato: AIzaSy...).",
                "sql": None,
                "data": None,
            }

        # Data queries via fallback
        if any(w in q for w in ["custo", "gasto", "valor", "preço", "pagamento"]):
            return {"type": "data", "sql": "SELECT STRFTIME(data_parsed, '%Y-%m') as mes, valor_clean as custo_reais FROM contract_costs WHERE valor_clean > 0 ORDER BY data_parsed", "answer": None, "data": None}

        if any(w in q for w in ["ativo", "ativos", "quantos usuario"]):
            return {"type": "data", "sql": "SELECT COUNT(*) as usuarios_ativos FROM dim_users WHERE is_active = 'true'", "answer": None, "data": None}

        if any(w in q for w in ["ocioso", "idle", "sem uso", "não usa", "inativos"]):
            return {"type": "data", "sql": "SELECT COUNT(*) as usuarios_inativos FROM dim_users WHERE is_active = 'false'", "answer": None, "data": None}

        if any(w in q for w in ["departamento", "dept", "area"]):
            return {"type": "data", "sql": "SELECT department, COUNT(*) as total FROM dim_users WHERE department != 'N/A' GROUP BY department ORDER BY total DESC LIMIT 15", "answer": None, "data": None}

        if any(w in q for w in ["centro de custo", "cost center", " cc "]):
            return {"type": "data", "sql": "SELECT cost_center, COUNT(*) as total FROM dim_users WHERE cost_center != 'N/A' GROUP BY cost_center ORDER BY total DESC LIMIT 15", "answer": None, "data": None}

        if any(w in q for w in ["atividade", "uso", "acesso", "login"]):
            return {"type": "data", "sql": "SELECT STRFTIME(date_parsed, '%Y-%m') as mes, COUNT(*) as eventos, COUNT(DISTINCT metabase_user_id) as usuarios FROM user_activity GROUP BY 1 ORDER BY 1 DESC LIMIT 12", "answer": None, "data": None}

        # Default: helpful message
        return {
            "type": "chat",
            "answer": "A API do Gemini não está respondendo no momento. Sem ela, só consigo responder perguntas pré-definidas sobre: custos, usuários ativos, usuários ociosos, departamentos e atividade.\n\nPra funcionar 100%, configure uma API key válida do Google AI Studio (formato AIzaSy...) no arquivo .env.",
            "sql": None,
            "data": None,
        }


_llm_service: LLMService | None = None


def get_llm_service() -> LLMService:
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
