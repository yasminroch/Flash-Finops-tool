# ⚡ Flash FinOps Tool

Plataforma interna de análise de custos e licenças do Metabase, construída como alternativa ao BI tradicional. Combina um backend em **FastAPI**, frontend em **React + Vite** e IA generativa via **Gemini 2.5 Flash** para análise conversacional dos dados.

> Case técnico de FinOps — avaliação de viabilidade de substituição do Metabase por solução interna escalável.

---

## 📋 Sumário

- [Visão Geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Arquitetura](#arquitetura)
- [Bases de Dados](#bases-de-dados)
- [Pré-requisitos](#pré-requisitos)
- [Como Rodar](#como-rodar)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Deploy](#deploy)
- [Estrutura do Projeto](#estrutura-do-projeto)

---

## Visão Geral

O Flash FinOps Tool responde às perguntas que o Metabase não consegue responder sobre ele mesmo: quanto custa por usuário, quem está ocioso, como o uso evoluiu mês a mês e como o custo se distribui por centro de custo.

Os dados analisados cobrem **Set/2024 → Jun/2026** e incluem:

- **R$ 154.434** em faturas registradas (21 pagamentos)
- **1.614 usuários** cadastrados, 693 ativos em 84 centros de custo
- **710.903 registros** de atividade diária

A plataforma permite explorar tudo isso via dashboards interativos e um chat com IA que responde perguntas em linguagem natural, gerando SQL diretamente contra as tabelas reais.

---

## Funcionalidades

- **Dashboard de Visão Geral** — KPIs de custo, usuários ativos/inativos e evolução mensal
- **Análise de Custos** — histórico completo de faturas com classificação automática (mensal, renovação anual, pós-contrato)
- **Análise de Usuários** — distribuição por grupo Metabase, centro de custo e departamento
- **Análise de Ociosidade** — gap mensal entre licenças pagas e uso real, com evolução histórica
- **Chat Analytics com IA** — perguntas em linguagem natural respondidas com dados reais via Gemini 2.5 Flash
- **Autenticação JWT** — controle de acesso com roles (admin / viewer)

---

## Arquitetura

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│    Backend       │────▶│   PostgreSQL    │
│  React + Vite   │     │   FastAPI        │     │  (metadados)    │
│  porta :5173    │     │   porta :8000    │     │  porta :5432    │
└─────────────────┘     └────────┬─────────┘     └─────────────────┘
                                 │
                         ┌───────▼────────┐
                         │  Data/ (CSV)   │
                         │  DuckDB (OLAP) │
                         └───────┬────────┘
                                 │
                         ┌───────▼────────┐
                         │ Gemini 2.5     │
                         │ Flash (IA)     │
                         └────────────────┘
```

**Stack:**

| Camada | Tecnologia |
|---|---|
| Frontend | React 18, Vite, Chart.js |
| Backend | Python 3.11, FastAPI, DuckDB |
| Banco (metadados) | PostgreSQL 16 |
| IA | Gemini 2.5 Flash (`gemini-2.5-flash`) |
| Infra local | Docker Compose |
| Deploy | Render.com |

---

## Bases de Dados

Os CSVs ficam em `Data/` e são lidos diretamente pelo backend via DuckDB. Três tabelas compõem o modelo:

### `contract_metabase_costs`
Histórico de faturas pagas ao Metabase.

| Coluna | Tipo | Descrição |
|---|---|---|
| `date` | string | Data do pagamento (formato `DD/MM/YYYY`) |
| `value` | string | Valor total da fatura em BRL (ex: `5.744,33`) |

> Atenção: novembro/2025 possui dois registros — dia 07 (fatura mensal) e dia 12 (renovação anual de R$ 64.837 por 610 licenças).

### `dim_metabase_users`
Cadastro de todos os usuários do Metabase.

| Coluna | Tipo | Descrição |
|---|---|---|
| `metabase_user_id` | float | Identificador único do usuário |
| `email` | string | E-mail associado |
| `name` | string | Nome completo |
| `is_active` | bool | Se o usuário está ativo no sistema |
| `is_admin` | bool | Se é administrador do Metabase |
| `metabase_group` | string | Grupo de permissão (ex: `CS | EQUIPE`, `TECH`) |
| `department` | string | Departamento vinculado |
| `job_title` | string | Cargo/função |
| `cost_center` | string | Centro de custo para rateio |
| `owner` | string | Líder responsável pelo centro de custo |
| `last_login` | string | Data/hora do último login |
| `joined_at` | string | Data/hora de criação do usuário |
| `deactivated_at` | string | Data/hora de desativação (nulo se ativo) |
| `updated_at` | string | Última atualização do registro |

### `flat_metabase_user_activity_daily`
Atividade diária de cada usuário — 710.903 registros de Jan/2025 a Jun/2026.

| Coluna | Tipo | Descrição |
|---|---|---|
| `date` | string | Data de referência (`D/M/YYYY`) |
| `metabase_user_id` | float | FK para `dim_metabase_users` |
| `is_active` | int (0/1) | Se o usuário estava ativo naquele dia |
| `viewed_card` | int (0/1) | Visualizou pelo menos um card/consulta |
| `viewed_dashboard` | int (0/1) | Visualizou pelo menos um dashboard |
| `viewed_collection` | int (0/1) | Acessou pelo menos uma collection |

---

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/) instalados
- Chave de API do Gemini 2.5 Flash — gratuita em [ai.google.dev](https://ai.google.dev)

---

## Como Rodar

### 1. Clone o repositório

```bash
git clone https://github.com/yasminroch/Flash-Finops-tool.git
cd Flash-Finops-tool
```

### 2. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Edite `.env` e preencha pelo menos a chave do Gemini:

```env
GEMINI_API_KEY=sua_chave_aqui
JWT_SECRET=flash-analytics-secret
```

### 3. Suba com Docker Compose

```bash
docker compose up --build
```

### 4. Acesse

| Serviço | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend (API) | http://localhost:8000 |
| Docs da API | http://localhost:8000/docs |

**Login padrão:** `admin@flash.com` / `flash123`

---

## Variáveis de Ambiente

| Variável | Obrigatória | Descrição |
|---|---|---|
| `GEMINI_API_KEY` | ✅ | Chave da API Google Gemini 2.5 Flash |
| `JWT_SECRET` | ✅ | Secret para assinar tokens JWT |
| `DATABASE_URL` | ✅ | URL do PostgreSQL (preenchida pelo Compose) |
| `DATA_PATH` | ✅ | Caminho para a pasta com os CSVs |
| `VITE_API_URL` | Frontend | URL do backend (em produção) |

---

## Deploy

O repositório inclui `render.yaml` pronto para deploy no [Render.com](https://render.com) com dois serviços web (backend e frontend) via Dockerfile.

```bash
# Após conectar o repo no Render, configure as env vars:
# GEMINI_API_KEY  →  sua chave
# JWT_SECRET      →  secret seguro
# DATABASE_URL    →  string do banco (Render PostgreSQL)
# VITE_API_URL    →  URL pública do backend
```

Os serviços são configurados como `web_service` com Docker no plano `starter`. O backend expõe a porta `8000` e o frontend a porta `80`.

---

## Estrutura do Projeto

```
Flash-Finops-tool/
├── Data/                          # CSVs com os dados de FinOps
│   ├── contract_metabase_costs.csv
│   ├── dim_metabase_users.csv
│   └── flat_metabase_user_activity_daily.csv
├── backend/                       # API FastAPI + DuckDB
│   ├── app/
│   │   ├── main.py                # Entrypoint FastAPI
│   │   ├── routers/
│   │   │   ├── auth.py            # Login e JWT
│   │   │   ├── queries.py         # Execução de SQL
│   │   │   ├── ai.py              # Chat com Gemini
│   │   │   └── dashboards.py      # Dados dos dashboards
│   │   └── services/
│   │       ├── duckdb.py          # Conector DuckDB → CSVs
│   │       └── llm.py             # Wrapper Gemini 2.5 Flash
│   └── Dockerfile
├── frontend/                      # App React + Vite
│   ├── src/
│   │   ├── pages/                 # Visão Geral, Custos, Usuários, Ociosidade, Chat
│   │   └── components/            # Gráficos, tabelas, filtros
│   └── Dockerfile
├── flash-bi-platform.html         # Documento técnico da proposta
├── docker-compose.yml             # Orquestração local
├── render.yaml                    # Configuração de deploy (Render.com)
└── .gitignore
```

---

## Contexto do Case

Este repositório é o MVP funcional de uma proposta de substituição do Metabase por plataforma interna. O argumento central:

- **Custo unitário real**: R$ 8,86/usuário/mês (R$ 64.837 ÷ 610 licenças ÷ 12 meses)
- **Taxa de uso em Jun/2026**: 93% dos usuários ativos usaram a ferramenta no mês — evolução de 70,7% em Jan/2025
- **Gap de ociosidade**: caiu de 172 usuários sem uso em Jan/2025 para apenas 6 em Jun/2026 (-96,5%)
- **Rateio real por CC**: CS ONBOARDING (49 usuários → R$ 434/mês), AGM (48 → R$ 425/mês)

O documento técnico completo está em [`flash-bi-platform.html`](./flash-bi-platform.html).
