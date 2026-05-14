import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Shield, UserPlus, Mail, Lock, ArrowRight, AlertCircle, CheckCircle } from 'lucide-react'
import { motion } from 'framer-motion'
import axios from 'axios'

const API_URL = "http://127.0.0.1:54321"

export default function Registrar() {
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [erro, setErro] = useState(null)
  const [sucesso, setSucesso] = useState(false)
  const [carregando, setCarregando] = useState(false)
  const navigate = useNavigate()

  const realizarRegistro = async (e) => {
    e.preventDefault()
    setCarregando(true)
    setErro(null)
    try {
      await axios.post(`${API_URL}/auth/register`, { email, senha })
      setSucesso(true)
      setTimeout(() => navigate('/login'), 2000)
    } catch (error) {
      setErro(error.response?.data?.detail || "Erro ao criar conta.")
    } finally {
      setCarregando(false)
    }
  }

  return (
    <div className="page-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '80vh' }}>
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-card" 
        style={{ width: '100%', maxWidth: '400px' }}
      >
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{ background: 'var(--gradiente-main)', width: '48px', height: '48px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem' }}>
            <UserPlus size={24} color="white" />
          </div>
          <h2>Crie sua conta</h2>
          <p style={{ color: 'var(--cor-texto-muted)', fontSize: '0.9rem' }}>Segurança total para seus segredos</p>
        </div>

        {erro && (
          <div style={{ background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', padding: '1rem', borderRadius: '12px', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem' }}>
            <AlertCircle size={18} /> {erro}
          </div>
        )}

        {sucesso && (
          <div style={{ background: 'rgba(34, 197, 94, 0.1)', color: '#22c55e', padding: '1rem', borderRadius: '12px', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem' }}>
            <CheckCircle size={18} /> Conta criada! Redirecionando...
          </div>
        )}

        <form onSubmit={realizarRegistro}>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem' }}>E-mail</label>
            <input 
              type="email" 
              className="input-field" 
              placeholder="seu@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div style={{ marginBottom: '2rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem' }}>Senha</label>
            <input 
              type="password" 
              className="input-field" 
              placeholder="Mínimo 8 caracteres"
              value={senha}
              onChange={(e) => setSenha(e.target.value)}
              required
            />
          </div>

          <button type="submit" className="btn-primary" style={{ width: '100%', justifyContent: 'center' }} disabled={carregando || sucesso}>
            {carregando ? "Criando..." : <><ArrowRight size={18} /> Registrar</>}
          </button>
        </form>

        <p style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.875rem', color: 'var(--cor-texto-muted)' }}>
          Já tem uma conta? <Link to="/login" style={{ color: 'var(--cor-primaria)', textDecoration: 'none' }}>Fazer Login</Link>
        </p>
      </motion.div>
    </div>
  )
}
