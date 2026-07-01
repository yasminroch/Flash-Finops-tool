import React, { useState } from 'react'
import Login from './pages/Login.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Chat from './pages/Chat.jsx'
import SQLEditor from './pages/SQLEditor.jsx'
import DataUpload from './pages/DataUpload.jsx'
import { isAuthenticated, logout, getUser } from './api.js'

function App() {
  const [page, setPage] = useState('dashboard')
  const [loggedIn, setLoggedIn] = useState(isAuthenticated())

  if (!loggedIn) {
    return <Login onLogin={() => setLoggedIn(true)} />
  }

  const user = getUser()

  const handleLogout = () => {
    logout()
    setLoggedIn(false)
  }

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <svg viewBox="0 0 32 32" fill="none">
            <rect width="32" height="32" rx="6" fill="#1a5fb4"/>
            <path d="M10 6h12l-4 10h6L12 26l2-10H8l2-10z" fill="#fff"/>
          </svg>
          <span>Flash Analytics</span>
        </div>
        <nav className="sidebar-nav">
          <button
            className={page === 'dashboard' ? 'active' : ''}
            onClick={() => setPage('dashboard')}
          >
            📊 Dashboard FinOps
          </button>
          <button
            className={page === 'chat' ? 'active' : ''}
            onClick={() => setPage('chat')}
          >
            🤖 Chat IA
          </button>
          <button
            className={page === 'sql' ? 'active' : ''}
            onClick={() => setPage('sql')}
          >
            💻 Editor SQL
          </button>
          <button
            className={page === 'data' ? 'active' : ''}
            onClick={() => setPage('data')}
          >
            📁 Dados & Upload
          </button>
          <button onClick={handleLogout} style={{marginTop: 'auto'}}>
            🚪 Sair ({user?.name || 'Usuário'})
          </button>
        </nav>
      </aside>

      <main className="main-content">
        {page === 'dashboard' && <Dashboard />}
        {page === 'chat' && <Chat />}
        {page === 'sql' && <SQLEditor />}
        {page === 'data' && <DataUpload />}
      </main>
    </div>
  )
}

export default App
