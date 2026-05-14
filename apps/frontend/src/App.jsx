import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Resgate from './pages/Resgate'
import Login from './pages/Login'
import Registrar from './pages/Registrar'
import Dashboard from './pages/Dashboard'

function App() {
  return (
    <Router>
      <div className="app-main">
        <div className="blob blob-1"></div>
        <div className="blob blob-2"></div>
        
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/resgatar/:id" element={<Resgate />} />
          <Route path="/login" element={<Login />} />
          <Route path="/registrar" element={<Registrar />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>

        <footer className="container" style={{ marginTop: '6rem', paddingBottom: '3rem', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '3rem', textAlign: 'center', color: 'var(--cor-texto-muted)', fontSize: '0.9rem' }}>
          <p>&copy; 2026 Antigravity Cofre Digital - Desenvolvido para Portfólios de Alta Performance</p>
        </footer>
      </div>
    </Router>
  )
}

export default App
