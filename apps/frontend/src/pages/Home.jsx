import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Shield, Lock, Copy, Check, Info, LayoutDashboard, User } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import { gerarChaveAleatoria, cifrarNoCliente } from '../utils/crypto'

const API_URL = "http://127.0.0.1:54321"

export default function Home() {
  const [texto, setTexto] = useState('')
  const [validade, setValidade] = useState(24)
  const [acessos, setAcessos] = useState(1)
  const [resultado, setResultado] = useState(null)
  const [carregando, setCarregando] = useState(false)
  const [copiado, setCopiado] = useState(false)
  const [logado, setLogado] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    setLogado(!!localStorage.getItem('token'))
  }, [])

  const criarSegredo = async (e) => {
    e.preventDefault()
    setCarregando(true)
    try {
      // 1. Gera uma chave aleatória no navegador
      const chaveCliente = gerarChaveAleatoria()
      
      // 2. Cifra o segredo localmente ANTES de enviar
      const textoCifradoNoCliente = cifrarNoCliente(texto, chaveCliente)

      // 3. Envia o conteúdo já cifrado para o servidor
      // Se estiver logado, enviamos o token para vincular o segredo ao usuário
      const token = localStorage.getItem('token')
      const headers = token ? { Authorization: `Bearer ${token}` } : {}

      const response = await axios.post(`${API_URL}/segredos`, {
        texto_puro: textoCifradoNoCliente,
        horas_validade: parseInt(validade),
        acessos_permitidos: parseInt(acessos)
      }, { headers })
      
      // 4. Constrói o link com a chave no fragmento (#)
      // O fragmento nunca é enviado ao servidor em futuras requisições HTTP.
      const link = `${window.location.origin}/resgatar/${response.data.id}#${chaveCliente}`
      setResultado(link)
      setTexto('')
    } catch (error) {
      alert("Falha ao criar segredo. Verifique se o backend está online.")
    } finally {
      setCarregando(false)
    }
  }

  const copiarLink = () => {
    navigator.clipboard.writeText(resultado)
    setCopiado(true)
    setTimeout(() => setCopiado(false), 2000)
  }

  return (
    <div className="page-container">
      <nav className="container" style={{ padding: '2rem 0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontWeight: 'bold', fontSize: '1.25rem' }}>
          <div style={{ background: 'var(--gradiente-main)', padding: '0.5rem', borderRadius: '10px' }}>
            <Shield size={24} color="white" />
          </div>
          Cofre Digital
        </div>
        <div style={{ display: 'flex', gap: '2rem', color: 'var(--cor-texto-muted)', alignItems: 'center' }}>
          {logado ? (
            <Link to="/dashboard" className="btn-primary" style={{ background: 'rgba(255,255,255,0.05)', color: 'white' }}>
              <LayoutDashboard size={18} /> Dashboard
            </Link>
          ) : (
            <Link to="/login" className="btn-primary" style={{ padding: '0.6rem 1.2rem', fontSize: '0.9rem' }}>
              <User size={18} /> Entrar
            </Link>
          )}
        </div>
      </nav>

      <main className="container" style={{ marginTop: '4rem', textAlign: 'center' }}>
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <span className="badge">Criptografia de Ponta-a-Ponta Ativada</span>
          <h1>Proteja seus dados sensíveis</h1>
          <p style={{ color: 'var(--cor-texto-muted)', fontSize: '1.1rem', maxWidth: '600px', margin: '0 auto 3rem' }}>
            Crie links criptografados que se auto-destroem após serem lidos. 
          </p>
        </motion.div>

        <div style={{ maxWidth: '800px', margin: '0 auto' }}>
          <AnimatePresence mode='wait'>
            {!resultado ? (
              <motion.form 
                key="form"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                onSubmit={criarSegredo} 
                className="glass-card" 
                style={{ textAlign: 'left' }}
              >
                <div style={{ marginBottom: '1.5rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>Seu Segredo</label>
                  <textarea 
                    className="input-field" 
                    rows="4" 
                    placeholder="Cole aqui senhas, chaves API ou mensagens privadas..."
                    value={texto}
                    onChange={(e) => setTexto(e.target.value)}
                    required
                    style={{ resize: 'none' }}
                  ></textarea>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '2rem' }}>
                  <div>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>Expira em (Horas)</label>
                    <input type="number" className="input-field" value={validade} onChange={(e) => setValidade(e.target.value)} />
                  </div>
                  <div>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>Limite de Acessos</label>
                    <input type="number" className="input-field" value={acessos} onChange={(e) => setAcessos(e.target.value)} />
                  </div>
                </div>

                <button type="submit" className="btn-primary" style={{ width: '100%', justifyContent: 'center' }} disabled={carregando}>
                  {carregando ? "Criptografando..." : <><Lock size={18} /> Gerar Link Seguro</>}
                </button>
              </motion.form>
            ) : (
              <motion.div 
                key="result"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-card"
                style={{ border: '1px solid rgba(139, 92, 246, 0.5)' }}
              >
                <div style={{ background: 'rgba(34, 197, 94, 0.1)', color: '#22c55e', padding: '1rem', borderRadius: '12px', marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '0.75rem', justifyContent: 'center' }}>
                  <Check size={20} /> Segredo Criptografado com Sucesso!
                </div>
                
                <p style={{ marginBottom: '1rem', textAlign: 'left', color: 'var(--cor-texto-muted)' }}>Compartilhe este link único:</p>
                <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '2rem' }}>
                  <input type="text" className="input-field" value={resultado} readOnly />
                  <button onClick={copiarLink} className="btn-primary" style={{ background: copiado ? '#22c55e' : 'var(--gradiente-main)' }}>
                    {copiado ? <Check size={18} /> : <Copy size={18} />}
                  </button>
                </div>

                <div style={{ display: 'flex', gap: '1rem', padding: '1rem', background: 'rgba(255,255,255,0.02)', borderRadius: '12px', textAlign: 'left', fontSize: '0.9rem' }}>
                  <Info size={24} color="var(--cor-primaria)" />
                  <p>Atenção: Este link só pode ser acessado {acessos} vez(es) ou expirará em {validade} horas.</p>
                </div>

                <button onClick={() => setResultado(null)} style={{ marginTop: '2rem', background: 'transparent', border: 'none', color: 'var(--cor-texto-muted)', cursor: 'pointer', textDecoration: 'underline' }}>
                  Criar outro segredo
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>
    </div>
  )
}
