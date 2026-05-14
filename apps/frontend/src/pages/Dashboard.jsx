import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Shield, Clock, FileText, User, ArrowLeft, LogOut, Search } from 'lucide-react'
import { motion } from 'framer-motion'
import axios from 'axios'

const API_URL = "http://127.0.0.1:54321"

export default function Dashboard() {
  const [logs, setLogs] = useState([])
  const [carregando, setCarregando] = useState(true)
  const navigate = useNavigate()
  const email = localStorage.getItem('usuario_email')

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      navigate('/login')
      return
    }

    const buscarLogs = async () => {
      try {
        const response = await axios.get(`${API_URL}/auditoria`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        setLogs(response.data)
      } catch (error) {
        if (error.response?.status === 401) {
          localStorage.clear()
          navigate('/login')
        }
      } finally {
        setCarregando(false)
      }
    }

    buscarLogs()
  }, [navigate])

  const logout = () => {
    localStorage.clear()
    navigate('/')
  }

  return (
    <div className="page-container">
      <nav className="container" style={{ padding: '2rem 0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--cor-texto-muted)', textDecoration: 'none' }}>
          <ArrowLeft size={18} /> Voltar ao Início
        </Link>
        <button onClick={logout} className="btn-primary" style={{ background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444' }}>
          <LogOut size={18} /> Sair
        </button>
      </nav>

      <main className="container" style={{ marginTop: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '3rem' }}>
          <div>
            <span className="badge">Painel de Auditoria</span>
            <h2 style={{ fontSize: '2rem' }}>Seus Segredos</h2>
            <p style={{ color: 'var(--cor-texto-muted)' }}>Logado como: {email}</p>
          </div>
        </div>

        <div className="glass-card" style={{ padding: '0' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                <th style={{ padding: '1.5rem', color: 'var(--cor-texto-muted)', fontWeight: '500' }}>Evento</th>
                <th style={{ padding: '1.5rem', color: 'var(--cor-texto-muted)', fontWeight: '500' }}>Data</th>
                <th style={{ padding: '1.5rem', color: 'var(--cor-texto-muted)', fontWeight: '500' }}>ID do Segredo</th>
                <th style={{ padding: '1.5rem', color: 'var(--cor-texto-muted)', fontWeight: '500' }}>IP</th>
              </tr>
            </thead>
            <tbody>
              {carregando ? (
                <tr><td colSpan="4" style={{ padding: '3rem', textAlign: 'center' }}>Carregando histórico...</td></tr>
              ) : logs.length === 0 ? (
                <tr><td colSpan="4" style={{ padding: '3rem', textAlign: 'center', color: 'var(--cor-texto-muted)' }}>Nenhum evento registrado ainda.</td></tr>
              ) : logs.map((log) => (
                <tr key={log.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.02)' }}>
                  <td style={{ padding: '1.2rem 1.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <div style={{ background: log.tipo_evento === 'CRIACAO_SEGREDO' ? 'rgba(34, 197, 94, 0.1)' : 'rgba(139, 92, 246, 0.1)', color: log.tipo_evento === 'CRIACAO_SEGREDO' ? '#22c55e' : 'var(--cor-primaria)', padding: '0.4rem', borderRadius: '8px' }}>
                        {log.tipo_evento === 'CRIACAO_SEGREDO' ? <FileText size={16} /> : <Search size={16} />}
                      </div>
                      <span style={{ fontSize: '0.9rem', fontWeight: '500' }}>{log.tipo_evento.replace('_', ' ')}</span>
                    </div>
                  </td>
                  <td style={{ padding: '1.2rem 1.5rem', fontSize: '0.85rem', color: 'var(--cor-texto-muted)' }}>
                    {new Date(log.data_evento).toLocaleString('pt-BR')}
                  </td>
                  <td style={{ padding: '1.2rem 1.5rem', fontSize: '0.85rem', fontFamily: 'monospace' }}>
                    {log.segredo_id.substring(0, 8)}...
                  </td>
                  <td style={{ padding: '1.2rem 1.5rem', fontSize: '0.85rem' }}>
                    {log.ip_origem || 'Interno'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  )
}
