import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Shield, Eye, Lock, AlertTriangle, ArrowLeft, Copy, Check } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import { decifrarNoCliente } from '../utils/crypto'

const API_URL = "http://127.0.0.1:54321"

export default function Resgate() {
  const { id } = useParams()
  const [segredo, setSegredo] = useState(null)
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState(null)
  const [copiado, setCopiado] = useState(false)

  const obterSegredo = async () => {
    setCarregando(true)
    setErro(null)
    try {
      // 1. Busca o conteúdo cifrado do servidor
      const response = await axios.get(`${API_URL}/segredos/${id}`)
      const conteudoCifradoDoServidor = response.data.texto_puro
      
      // 2. Obtém a chave do fragmento da URL (#)
      const chave = window.location.hash.substring(1)
      
      if (!chave) {
        throw new Error("Chave de decodificação ausente no link.")
      }

      // 3. Decifra localmente
      const textoOriginal = decifrarNoCliente(conteudoCifradoDoServidor, chave)
      setSegredo(textoOriginal)
    } catch (error) {
      setErro(error.message || "Este segredo não existe mais ou expirou.")
    } finally {
      setCarregando(false)
    }
  }

  const copiarTexto = () => {
    navigator.clipboard.writeText(segredo)
    setCopiado(true)
    setTimeout(() => setCopiado(false), 2000)
  }

  return (
    <div className="page-container">
      <nav className="container" style={{ padding: '2rem 0' }}>
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--cor-texto-muted)', textDecoration: 'none' }}>
          <ArrowLeft size={18} /> Voltar ao Início
        </Link>
      </nav>

      <main className="container" style={{ marginTop: '2rem', textAlign: 'center' }}>
        <div style={{ maxWidth: '600px', margin: '0 auto' }}>
          <AnimatePresence mode='wait'>
            {!segredo && !erro ? (
              <motion.div 
                key="warning"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="glass-card"
              >
                <div style={{ color: '#f59e0b', marginBottom: '1.5rem' }}>
                  <AlertTriangle size={48} style={{ margin: '0 auto' }} />
                </div>
                <h2>Atenção: Leitura Única</h2>
                <p style={{ color: 'var(--cor-texto-muted)', margin: '1rem 0 2rem' }}>
                  Você está prestes a visualizar um segredo criptografado. 
                  Dependendo das configurações, ele poderá ser **destruído permanentemente** após esta visualização.
                </p>
                <button onClick={obterSegredo} className="btn-primary" style={{ width: '100%', justifyContent: 'center' }} disabled={carregando}>
                  {carregando ? "Descriptografando..." : <><Eye size={18} /> Revelar Segredo</>}
                </button>
              </motion.div>
            ) : erro ? (
              <motion.div 
                key="error"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-card"
                style={{ borderColor: 'rgba(239, 68, 68, 0.3)' }}
              >
                <Lock size={48} color="#ef4444" style={{ margin: '0 auto 1.5rem' }} />
                <h2 style={{ color: '#ef4444' }}>Acesso Negado</h2>
                <p style={{ color: 'var(--cor-texto-muted)', marginTop: '1rem' }}>{erro}</p>
                <Link to="/" className="btn-primary" style={{ marginTop: '2rem', width: '100%', justifyContent: 'center', background: 'rgba(255,255,255,0.05)', color: 'white' }}>
                  Criar um novo cofre
                </Link>
              </motion.div>
            ) : (
              <motion.div 
                key="secret"
                initial={{ opacity: 0, rotateY: 90 }}
                animate={{ opacity: 1, rotateY: 0 }}
                transition={{ type: 'spring', damping: 12 }}
                className="glass-card"
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                  <span className="badge" style={{ margin: 0 }}>Segredo Revelado</span>
                  <button onClick={copiarTexto} style={{ background: 'transparent', border: 'none', color: copiado ? '#22c55e' : 'var(--cor-texto-muted)', cursor: 'pointer' }}>
                    {copiado ? <Check size={20} /> : <Copy size={20} />}
                  </button>
                </div>
                <div style={{ background: 'rgba(0,0,0,0.2)', padding: '1.5rem', borderRadius: '12px', textAlign: 'left', wordBreak: 'break-all', fontSize: '1.1rem', border: '1px inset rgba(255,255,255,0.05)' }}>
                  <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>{segredo}</pre>
                </div>
                <p style={{ marginTop: '2rem', color: '#ef4444', fontSize: '0.875rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                  <Lock size={14} /> Este conteúdo foi marcado para destruição.
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>
    </div>
  )
}
