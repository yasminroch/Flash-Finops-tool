const API_BASE = import.meta.env.VITE_API_URL || '/api';

function getToken() {
  return localStorage.getItem('flash_token');
}

function getHeaders() {
  const headers = { 'Content-Type': 'application/json' };
  const token = getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return headers;
}

export async function login(email, password) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error('Credenciais inválidas');
  const data = await res.json();
  localStorage.setItem('flash_token', data.access_token);
  localStorage.setItem('flash_user', JSON.stringify(data.user));
  return data;
}

export function logout() {
  localStorage.removeItem('flash_token');
  localStorage.removeItem('flash_user');
}

export function getUser() {
  const user = localStorage.getItem('flash_user');
  return user ? JSON.parse(user) : null;
}

export function isAuthenticated() {
  return !!getToken();
}

export async function fetchMetrics() {
  const res = await fetch(`${API_BASE}/dashboard/metrics`, { headers: getHeaders() });
  return res.json();
}

export async function fetchCostTrend() {
  const res = await fetch(`${API_BASE}/dashboard/cost-trend`, { headers: getHeaders() });
  return res.json();
}

export async function fetchUsersByDepartment() {
  const res = await fetch(`${API_BASE}/dashboard/users-by-department`, { headers: getHeaders() });
  return res.json();
}

export async function fetchUsersByCostCenter() {
  const res = await fetch(`${API_BASE}/dashboard/users-by-cost-center`, { headers: getHeaders() });
  return res.json();
}

export async function fetchActivityTimeline() {
  const res = await fetch(`${API_BASE}/dashboard/activity-timeline`, { headers: getHeaders() });
  return res.json();
}

export async function fetchIdleUsers() {
  const res = await fetch(`${API_BASE}/dashboard/idle-users`, { headers: getHeaders() });
  return res.json();
}

export async function fetchTopActiveUsers() {
  const res = await fetch(`${API_BASE}/dashboard/top-active-users`, { headers: getHeaders() });
  return res.json();
}

export async function executeQuery(sql) {
  const res = await fetch(`${API_BASE}/queries/execute`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ sql }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Erro ao executar query');
  }
  return res.json();
}

export async function chatWithAI(question) {
  const res = await fetch(`${API_BASE}/ai/chat`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ question }),
  });
  return res.json();
}

export async function fetchChatHistory() {
  const res = await fetch(`${API_BASE}/ai/history`, { headers: getHeaders() });
  return res.json();
}

export async function clearChatHistory() {
  const res = await fetch(`${API_BASE}/ai/history`, {
    method: 'DELETE',
    headers: getHeaders(),
  });
  return res.json();
}

export async function fetchInsights() {
  const res = await fetch(`${API_BASE}/ai/insights`, { headers: getHeaders() });
  return res.json();
}

export async function uploadCSV(file) {
  const formData = new FormData();
  formData.append('file', file);
  const token = getToken();
  const headers = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}/data/upload`, {
    method: 'POST',
    headers,
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Erro ao fazer upload');
  }
  return res.json();
}

export async function fetchDatasets() {
  const res = await fetch(`${API_BASE}/data/datasets`, { headers: getHeaders() });
  return res.json();
}

export async function fetchAllTables() {
  const res = await fetch(`${API_BASE}/data/tables`, { headers: getHeaders() });
  return res.json();
}
