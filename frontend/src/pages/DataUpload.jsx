import React, { useState, useEffect } from 'react'
import { uploadCSV, fetchAllTables } from '../api.js'

export default function DataUpload() {
  const [tables, setTables] = useState([])
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    loadTables()
  }, [])

  async function loadTables() {
    try {
      const res = await fetchAllTables()
      setTables(res.tables || [])
    } catch (err) {
      console.error('Error loading tables:', err)
    }
  }

  const handleUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setError('')
    setResult(null)
    setUploading(true)

    try {
      const res = await uploadCSV(file)
      setResult(res)
      loadTables() // Refresh table list
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>📁 Dados & Upload</h1>
        <p>Faça upload de novos CSVs — eles ficam disponíveis pra consulta no chat e no editor SQL</p>
      </div>

      {/* Upload area */}
      <div style={{
        background: 'var(--card)',
        border: '2px dashed var(--line2)',
        borderRadius: 'var(--radius)',
        padding: '2rem',
        textAlign: 'center',
        marginBottom: '2rem',
      }}>
        <p style={{ fontSize: '16px', marginBottom: '1rem', color: 'var(--ink)' }}>
          📤 Arraste um CSV ou clique para selecionar
        </p>
        <input
          type="file"
          accept=".csv"
          onChange={handleUpload}
          disabled={uploading}
          style={{ fontSize: '14px' }}
        />
        {uploading && <p style={{ marginTop: '1rem', color: 'var(--accent)' }}>Processando...</p>}
      </div>

      {/* Upload result */}
      {result && (
        <div style={{
          padding: '1rem 1.25rem',
          background: 'var(--success-bg)',
          border: '1px solid var(--success)',
          borderRadius: 'var(--radius)',
          marginBottom: '2rem',
          fontSize: '13px',
        }}>
          <strong>✅ {result.message}</strong>
          <p style={{ marginTop: '0.5rem' }}>
            Tabela: <code>{result.table_name}</code> · {result.row_count} linhas · 
            Colunas: {result.columns.join(', ')}
          </p>
        </div>
      )}

      {error && (
        <div style={{
          padding: '1rem 1.25rem',
          background: 'var(--danger-bg)',
          border: '1px solid var(--danger)',
          borderRadius: 'var(--radius)',
          marginBottom: '2rem',
          fontSize: '13px',
          color: 'var(--danger)',
        }}>
          ❌ {error}
        </div>
      )}

      {/* Table list */}
      <div className="chart-card">
        <h3>📊 Tabelas Disponíveis</h3>
        <p style={{ fontSize: '12px', color: 'var(--muted)', marginBottom: '1rem' }}>
          Estas tabelas podem ser consultadas no Chat IA e no Editor SQL
        </p>
        <div className="results-table-wrap">
          <table className="results-table">
            <thead>
              <tr>
                <th>Tabela</th>
                <th>Linhas</th>
                <th>Origem</th>
              </tr>
            </thead>
            <tbody>
              {tables.map((t, i) => (
                <tr key={i}>
                  <td><code>{t.name}</code></td>
                  <td>{t.row_count.toLocaleString()}</td>
                  <td>
                    {['contract_costs', 'dim_users', 'user_activity'].includes(t.name)
                      ? <span className="pill pill-blue">Original</span>
                      : <span className="pill pill-green">Upload</span>
                    }
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
