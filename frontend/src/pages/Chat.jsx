import React, { useState, useRef, useEffect } from 'react'
import { chatWithAI, fetchChatHistory, clearChatHistory } from '../api.js'

export default function Chat() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [historyLoaded, setHistoryLoaded] = useState(false)
  const messagesEndRef = useRef(null)

  // Load history on mount
  useEffect(() => {
    async function loadHistory() {
      try {
        const res = await fetchChatHistory()
        if (res.messages && res.messages.length > 0) {
          setMessages(res.messages.map(m => ({
            role: m.role,
            content: m.content,
            sql: m.sql,
          })))
        } else {
          setMessages([{
            role: 'assistant',
            content: 'Olá! 👋 Sou o assistente de dados da Flash, powered by Gemini 2.5 Flash.\n\nPode me perguntar qualquer coisa:\n• Sobre os dados (custos, usuários, licenças)\n• Explicações sobre conceitos\n• Ou só bater um papo!\n\nO que posso te ajudar?',
          }])
        }
      } catch {
        setMessages([{
          role: 'assistant',
          content: 'Olá! 👋 Sou o assistente de dados da Flash. O que posso te ajudar?',
        }])
      }
      setHistoryLoaded(true)
    }
    loadHistory()
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const question = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: question }])
    setLoading(true)

    try {
      const response = await chatWithAI(question)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.answer,
        sql: response.sql,
        data: response.data,
      }])
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Erro ao processar: ${err.message}`,
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleClear = async () => {
    await clearChatHistory()
    setMessages([{
      role: 'assistant',
      content: 'Histórico limpo! 🧹 Em que posso te ajudar?',
    }])
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  if (!historyLoaded) return <div className="loading">Carregando histórico...</div>

  return (
    <div className="chat-container">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1>🤖 Assistente de Dados</h1>
          <p>Chatbot com Gemini 2.5 Flash — converse sobre dados ou qualquer assunto</p>
        </div>
        <button className="btn btn-secondary" onClick={handleClear} style={{ fontSize: '11px' }}>
          🗑️ Limpar histórico
        </button>
      </div>

      <div className="chat-messages">
        {messages.map((msg, i) => (
          <div key={i} className={`chat-message ${msg.role}`}>
            <MessageContent message={msg} />
          </div>
        ))}
        {loading && (
          <div className="chat-message assistant">
            <em>⏳ Consultando o Gemini...</em>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-row">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Digite sua pergunta..."
          disabled={loading}
        />
        <button onClick={handleSend} disabled={loading || !input.trim()}>
          Enviar
        </button>
      </div>
    </div>
  )
}

function MessageContent({ message }) {
  const { content, sql, data } = message
  const [showSql, setShowSql] = useState(false)

  return (
    <div>
      <div style={{ whiteSpace: 'pre-wrap' }}>{content}</div>

      {sql && (
        <div style={{ marginTop: '0.5rem' }}>
          <button
            onClick={() => setShowSql(!showSql)}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--accent)',
              fontSize: '11px',
              cursor: 'pointer',
              textDecoration: 'underline',
            }}
          >
            {showSql ? '🔽 Ocultar SQL' : '▶ Ver SQL gerado'}
          </button>
          {showSql && (
            <pre style={{
              marginTop: '0.4rem',
              background: 'rgba(0,0,0,0.05)',
              padding: '0.5rem',
              borderRadius: '4px',
              fontSize: '11px',
              overflow: 'auto',
            }}>
              {sql}
            </pre>
          )}
        </div>
      )}

      {data && data.columns && data.rows && data.rows.length > 0 && (
        <div className="results-table-wrap" style={{ marginTop: '0.75rem' }}>
          <table className="results-table">
            <thead>
              <tr>
                {data.columns.map((col, i) => (
                  <th key={i}>{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.rows.slice(0, 15).map((row, i) => (
                <tr key={i}>
                  {row.map((cell, j) => (
                    <td key={j}>{cell != null ? String(cell) : '—'}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          {data.rows.length > 15 && (
            <p style={{ padding: '0.5rem 0.75rem', fontSize: '11px', color: 'var(--muted)' }}>
              Mostrando 15 de {data.rows.length} linhas
            </p>
          )}
        </div>
      )}
    </div>
  )
}
