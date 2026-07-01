import React, { useState, useEffect } from 'react'
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts'
import {
  fetchMetrics, fetchCostTrend, fetchUsersByDepartment,
  fetchActivityTimeline, fetchUsersByCostCenter
} from '../api.js'

const COLORS = ['#1a5fb4', '#0f6e56', '#4a2d8b', '#7a4a00', '#8b1a1a', '#2d6a2d', '#5b5b58']

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null)
  const [costTrend, setCostTrend] = useState([])
  const [departments, setDepartments] = useState([])
  const [costCenters, setCostCenters] = useState([])
  const [activity, setActivity] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const [m, ct, dept, cc, act] = await Promise.all([
          fetchMetrics(),
          fetchCostTrend(),
          fetchUsersByDepartment(),
          fetchUsersByCostCenter(),
          fetchActivityTimeline(),
        ])
        setMetrics(m)
        setCostTrend(ct.data || [])
        setDepartments((dept.data || []).slice(0, 8))
        setCostCenters((cc.data || []).slice(0, 10))
        setActivity(act.data || [])
      } catch (err) {
        console.error('Error loading dashboard:', err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) return <div className="loading">Carregando dashboard...</div>

  return (
    <div>
      <div className="page-header">
        <h1>Dashboard FinOps — Metabase</h1>
        <p>Visão geral de licenças, custos e utilização</p>
      </div>

      {/* Metrics */}
      {metrics && (
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="label">Licenças Contratadas</div>
            <div className="value">{metrics.licenses_contracted}</div>
            <div className="sub">Contrato Nov/2025</div>
          </div>
          <div className="metric-card">
            <div className="label">Usuários Totais</div>
            <div className="value">{metrics.total_users}</div>
            <div className="sub">{metrics.active_users} ativos</div>
          </div>
          <div className="metric-card">
            <div className="label">Usuários Ociosos</div>
            <div className="value" style={{color: 'var(--danger)'}}>{metrics.idle_users}</div>
            <div className="sub">Inativos na plataforma</div>
          </div>
          <div className="metric-card">
            <div className="label">Custo Mensal Atual</div>
            <div className="value" style={{fontSize: '1.3rem'}}>{metrics.total_cost_current_month}</div>
            <div className="sub">Último mês disponível</div>
          </div>
        </div>
      )}

      {/* Charts */}
      <div className="chart-grid">
        {/* Cost Trend */}
        <div className="chart-card">
          <h3>📈 Evolução de Custo Mensal (R$)</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={costTrend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0ddd5" />
              <XAxis dataKey="month" fontSize={11} />
              <YAxis fontSize={11} />
              <Tooltip formatter={(v) => [`R$ ${Number(v).toFixed(2)}`, 'Custo']} />
              <Line
                type="monotone"
                dataKey="cost"
                stroke="#1a5fb4"
                strokeWidth={2}
                dot={{ r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Activity Timeline */}
        <div className="chart-card">
          <h3>📊 Atividade Mensal (Eventos)</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={activity}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0ddd5" />
              <XAxis dataKey="month" fontSize={11} />
              <YAxis fontSize={11} />
              <Tooltip />
              <Bar dataKey="total_events" fill="#1a5fb4" name="Eventos" radius={[3,3,0,0]} />
              <Bar dataKey="unique_users" fill="#0f6e56" name="Usuários únicos" radius={[3,3,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Users by Department */}
        <div className="chart-card">
          <h3>👥 Usuários por Departamento (Top 8)</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={departments} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#e0ddd5" />
              <XAxis type="number" fontSize={11} />
              <YAxis type="category" dataKey="department" fontSize={10} width={140} />
              <Tooltip />
              <Bar dataKey="user_count" fill="#4a2d8b" name="Total" radius={[0,3,3,0]} />
              <Bar dataKey="active_count" fill="#2d6a2d" name="Ativos" radius={[0,3,3,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Cost Centers */}
        <div className="chart-card">
          <h3>🏢 Usuários por Centro de Custo (Top 10)</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={costCenters} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#e0ddd5" />
              <XAxis type="number" fontSize={11} />
              <YAxis type="category" dataKey="cost_center" fontSize={10} width={160} />
              <Tooltip />
              <Bar dataKey="user_count" fill="#0f6e56" name="Total" radius={[0,3,3,0]} />
              <Bar dataKey="active_count" fill="#1a5fb4" name="Ativos" radius={[0,3,3,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
