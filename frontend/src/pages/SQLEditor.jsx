import React, { useState } from 'react'
import { executeQuery } from '../api.js'

const EXAMPLE_QUERIES = [
  {
    label: 'Custos mensais',
    sql: "SELECT STRFTIME(data_parsed, '%Y-%m') as mes, valor_clean as custo_reais\nFROM contract_costs\nWHERE valor_clean > 0\nORDER BY data_parsed",
  },
  {
    label: 'Usuários ativos por departamento',
    sql: "SELECT department, COUNT(*) as total\nFROM dim_users\nWHERE is_active = 'true' AND department != 'N/A'\nGROUP BY department\nORDER BY total DESC",
  },
  {
    label: 'Atividade diária (últimos 30 dias)',
    sql: "SELECT date_parsed, COUNT(*) as eventos, SUM(CAST(viewed_dashboard AS INTEGER)) as dashboards\nFROM user_activity\nGROUP BY date_parsed\nORDER BY date_parsed DESC\nLIMIT 30",
  },
  {
    label: 'Top 10 usuários mais ativos',
    sql: "SELECT metabase_user_id, COUNT(*) as dias_ativos,\n  SUM(CAST(viewed_dashboard AS INTEGER)) as dashboards,\n  SUM(CAST(viewed_card AS INTEGER)) as cards\nFROM user_activity\nGROUP BY metabase_user_id\nORDER BY dias_ativos DESC\nLIMIT 10",
  },
]

export default function SQLEditor() {
  const [sql, setSql] = useState(EXAMPLE_QUERIES[0].sql)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleExecute = async () => {
    if (!sql.trim()) return
    setError('')
    setResult(null)
    setLoading(true)

    try {
      const data = await executeQuery(sql)
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault()
      handleExecute()
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>💻 Editor SQL</h1>
        <p>Execute queries diretamente no DuckDB (Ctrl+Enter para executar)</p>
      </div>

      {/* Example queries */}
      <div style={{marginBottom: '1rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap'}}>
        {EXAMPLE_QUERIES.map((q, i) => (
          <button
            key={i}
            className="btn btn-secondary"
            onClick={() => setSql(q.sql)}
            style={{fontSize: '11px'}}
          >
            {q.label}
          </button>
        ))}
      </div>

      <div className="sql-editor">
        <textarea
          value={sql}
          onChange={(e) => setSql(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="SELECT * FROM contract_costs LIMIT 10"
          spellCheck={false}
        />
        <div className="actions">
          <button className="btn btn-primary" onClick={handleExecute} disabled={loading}>
            {loading ? 'Executando...' : '▶ Executar'}
          </button>
          <button className="btn btn-secondary" onClick={() => { setSql(''); setResult(null); setError(''); }}>
            Limpar
          </button>
        </div>
      </div>

      {error && (
        <div style={{
          marginTop: '1rem',
          padding: '0.75rem 1rem',
          background: 'var(--danger-bg)',
          border: '1px solid var(--danger)',
          borderRadius: 'var(--radius)',
          color: 'var(--danger)',
          fontSize: '13px',
        }}>
          {error}
        </div>
      )}

      {result && (
        <div>
          <p style={{marginTop: '1rem', fontSize: '12px', color: 'var(--muted)'}}>
            {result.row_count} resultado(s) retornado(s)
          </p>
          <div className="results-table-wrap">
            <table className="results-table">
              <thead>
                <tr>
                  {result.columns.map((col, i) => (
                    <th key={i}>{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {result.rows.map((row, i) => (
                  <tr key={i}>
                    {row.map((cell, j) => (
                      <td key={j}>{cell != null ? String(cell) : '—'}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
