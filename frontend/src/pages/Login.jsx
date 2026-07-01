import React, { useState } from 'react'
import { login } from '../api.js'

export default function Login({ onLogin }) {
  const [email, setEmail] = useState('admin@flash.com')
  const [password, setPassword] = useState('flash123')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      onLogin()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={handleSubmit}>
        <h1>⚡ Flash Analytics</h1>
        <p>Faça login para acessar a plataforma</p>

        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="admin@flash.com"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="password">Senha</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••"
            required
          />
        </div>

        <button className="login-btn" type="submit" disabled={loading}>
          {loading ? 'Entrando...' : 'Entrar'}
        </button>

        {error && <p className="error-msg">{error}</p>}

        <p style={{marginTop: '1rem', fontSize: '11px', color: '#9c9a93'}}>
          MVP: admin@flash.com / flash123
        </p>
      </form>
    </div>
  )
}
