# PRD FRONTEND — COFRE DIGITAL UI

## PROJECT COFRE DIGITAL
### The Interface

**Especificação de Experiência, Segurança e Componentes do Cliente**  
*v1.0 — Maio 2026*

---

# 1. Stack Tecnológica
Framework: Next.js 14 com App Router e Server Components — SSR nativo para melhor SEO e segurança.
Linguagem: TypeScript strict mode — tipagem end-to-end com geração automática de tipos da API.
Estilização: Tailwind CSS — dark mode nativo, acessibilidade WCAG 2.1 AA, design tokens consistentes.
State Management: React Context + Custom Hooks — sem Redux; estado mínimo e previsível.
HTTP Client: Axios com interceptors — retry automático, refresh de token transparente.
Testes: Playwright (E2E) + React Testing Library (componentes).

# 2. Arquitetura de Componentes

## 2.1 Secret Creator — Tela de Criação
Interface para criação de segredos com as seguintes características:
Campo de input protegido: tipo password com toggle de visibilidade, sem autocomplete ('off').
Configuração de TTL: Selector com opções pré-definidas (1h, 24h, 7d) e campo customizável.
Opções avançadas: Número máximo de leituras (1-10), notificação por email ao acesso.
URL de compartilhamento: Gerada pelo backend, exibida uma única vez, com botão de cópia.
Feedback visual: Progress indicator durante criptografia, confirmação com animação de destruição.

## 2.2 Access Portal — Tela de Resgate
Tela de consumo do segredo com proteção máxima:
Autenticação do link: Validação do token HMAC antes de qualquer renderização.
Proteção anti-paste acidental: Modal de confirmação com aviso explícito de uso único.
Visualização única: Segredo exibido uma vez com overlay de proteção (sem seleção de texto).
Destruição confirmada: Após visualização, API confirma deleção e exibe estado final imutável.
Fallback gracioso: Mensagens claras para links expirados, já utilizados ou inválidos.

## 2.3 Audit Dashboard — Painel do Proprietário
Disponível apenas para o criador do segredo, autenticado via JWT:
Status em tempo real: WebSocket (ou polling configurável) para atualização do estado dos segredos.
Timeline de acessos: IP anonimizado, timestamp e user-agent de cada tentativa de leitura.
Ações disponíveis: Revogação manual antes do TTL com confirmação e registro em audit log.
Exportação: Download de log em CSV/JSON para fins de conformidade.

## 2.4 Auth Flow
Tela de login/registro com validação em tempo real (zod + react-hook-form).
Refresh token silencioso: Interceptor Axios renova o access token sem interromper a UX.
Logout global: Limpa todos os tokens, redireciona e invalida refresh token no backend.

# 3. Segurança no Cliente

## 3.1 Memory-Only Storage
Access Token: Armazenado em variável de módulo JavaScript (não em localStorage).
Refresh Token: Cookie HttpOnly + SameSite=Strict — inacessível a JavaScript.
Segredos em exibição: Estado React local, destruído ao desmontar o componente.

## 3.2 Sanitização e XSS
DOMPurify: Sanitização de qualquer conteúdo dinâmico antes da renderização.
Content Security Policy (CSP): Header restritivo — sem inline scripts, sem eval().
React por padrão: JSX escapa automaticamente; ausência de dangerouslySetInnerHTML.

## 3.3 CSRF Protection
Tokens CSRF incluídos em todas as requisições mutáveis (POST, PUT, DELETE).
SameSite=Strict nos cookies de sessão previne ataques cross-origin.
Origin validation no backend como segunda linha de defesa.

## 3.4 Outras Proteções
Subresource Integrity (SRI): Hash verificado para todos os scripts externos (se existirem).
Referrer-Policy: strict-origin-when-cross-origin — sem vazamento de URL.
Permissions-Policy: Camera, mic e geolocation desabilitados explicitamente.

# 4. Design System e Acessibilidade
Dark Mode: Implementado via CSS variables + Tailwind dark: prefix; preferência salva no cookie.
Acessibilidade: ARIA labels em todos os componentes interativos; navegação completa por teclado.
Responsividade: Mobile-first; testado em viewports 320px–2560px.
Loading States: Skeletons para todas as cargas assíncronas; sem flash de conteúdo não estilizado.
Error Boundaries: Captura de erros React com fallback UI e report para Sentry.

# 5. Testes Frontend
