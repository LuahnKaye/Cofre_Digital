import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Shield, Lock, Mail, ArrowRight, AlertCircle } from 'lucide-react'
import { motion } from 'framer-motion'
import axios from 'axios'

const API_URL = "http://127.0.0.1:54321"

export default function Login() {
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [erro, setErro] = useState(null)
  const [carregando, setCarregando] = useState(false)
  const navigate = useNavigate()

  const realizarLogin = async (e) => {
    e.preventDefault()
    setCarregando(true)
    setErro(null)
    try {
      const response = await axios.post(`${API_URL}/auth/login`, { email, senha })
      localStorage.setItem('token', response.data.access_token)
      localStorage.setItem('usuario_email', email)
      navigate('/')
    } catch (error) {
      setErro("Credenciais inválidas ou erro no servidor.")
    } finally {
      setCarregando(false)
    }
  }

  return (
    <div className="page-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '80vh' }}>
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card" 
        style={{ width: '100%', maxWidth: '400px' }}
      >
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{ background: 'var(--gradiente-main)', width: '48px', height: '48px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem' }}>
            <Shield size={24} color="white" />
          </div>
          <h2>Acesse sua conta</h2>
          <p style={{ color: 'var(--cor-texto-muted)', fontSize: '0.9rem' }}>Gerencie seus segredos e auditoria</p>
        </div>

        {erro && (
          <div style={{ background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', padding: '1rem', borderRadius: '12px', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem' }}>
            <AlertCircle size={18} /> {erro}
          </div>
        )}

        <form onSubmit={realizarLogin}>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem' }}>E-mail</label>
            <div style={{ position: 'relative' }}>
              <Mail size={18} style={{ position: 'absolute', left: '1rem', top: '1rem', color: 'var(--cor-texto-muted)' }} />
              <input 
                type="email" 
                className="input-field" 
                style={{ paddingLeft: '3rem' }}
                placeholder="seu@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
          </div>

          <div style={{ marginBottom: '2rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem' }}>Senha</label>
            <div style={{ position: 'relative' }}>
              <Lock size={18} style={{ position: 'absolute', left: '1rem', top: '1rem', color: 'var(--cor-texto-muted)' }} />
              <input 
                type="password" 
                className="input-field" 
                style={{ paddingLeft: '3rem' }}
                placeholder="••••••••"
                value={senha}
                onChange={(e) => setSenha(e.target.value)}
                required
              />
            </div>
          </div>

          <button type="submit" className="btn-primary" style={{ width: '100%', justifyContent: 'center' }} disabled={carregando}>
            {carregando ? "Entrando..." : <><ArrowRight size={18} /> Entrar</>}
          </button>
        </form>

        <p style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.875rem', color: 'var(--cor-texto-muted)' }}>
          Não tem uma conta? <Link to="/registrar" style={{ color: 'var(--cor-primaria)', textDecoration: 'none' }}>Cadastre-se</Link>
        </p>
      </motion.div>
    </div>
  )
}
