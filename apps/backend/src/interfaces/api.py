from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import uuid
import os
from datetime import datetime

from infrastructure.banco_de_dados import obter_sessao
from infrastructure.repositorios_sql import RepositorioSegredoSQL, RepositorioAuditoriaSQL, RepositorioUsuarioSQL, RepositorioOutboxSQL
from infrastructure.criptografia import MotorDeCriptografia
from infrastructure.seguranca import gerar_hash_senha, verificar_senha, criar_token_acesso, SECRET_KEY, ALGORITHM
from infrastructure.mensageria_outbox import PublicadorViaOutbox
from infrastructure.rate_limit import RateLimiter
from infrastructure.idempotencia import ServicoIdempotencia
from jose import JWTError, jwt
from application.casos_de_uso import CriarSegredo, ResgatarEDestruirSegredo, RegistrarUsuario, AutenticarUsuario, ListarLogsAuditoria
from application.servicos import ServicoDeMensageria
from interfaces.schemas import (
    EsquemaCriarSegredoRequest, 
    EsquemaCriarSegredoResponse, 
    EsquemaResgatarSegredoResponse,
    EsquemaUsuarioRegistro,
    EsquemaUsuarioLogin,
    EsquemaToken,
    EsquemaLogAuditoria
)
from typing import List

router = APIRouter()
limiter = RateLimiter()
idempotencia = ServicoIdempotencia()

def obter_servicos_e_repos(db: Session = Depends(obter_sessao)):
    """
    Fábrica para instanciar repositórios e serviços.
    Em uma aplicação maior, usaríamos um container de DI.
    """
    repo_segredo = RepositorioSegredoSQL(db)
    repo_auditoria = RepositorioAuditoriaSQL(db)
    repo_usuario = RepositorioUsuarioSQL(db)
    repo_outbox = RepositorioOutboxSQL(db)
    
    # KEK vem do ambiente
    kek = os.getenv("CHAVE_MESTRA_KEK", "chave_mestra_padrao_muito_secreta_123")
    servico_crypto = MotorDeCriptografia(kek)
    
    # Em vez de RabbitMQ direto, usamos o Outbox
    servico_mensageria = PublicadorViaOutbox(repo_outbox)
    
    return {
        "criar_segredo": CriarSegredo(repo_segredo, repo_auditoria, servico_crypto, servico_mensageria),
        "resgatar_segredo": ResgatarEDestruirSegredo(repo_segredo, repo_auditoria, servico_crypto, servico_mensageria),
        "registrar_usuario": RegistrarUsuario(repo_usuario),
        "autenticar_usuario": AutenticarUsuario(repo_usuario),
        "listar_auditoria": ListarLogsAuditoria(repo_auditoria)
    }


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def obter_usuario_atual(
    token: str = Depends(oauth2_scheme),
    componentes: dict = Depends(obter_servicos_e_repos)
) -> uuid.UUID:
    """
    Extrai e valida o ID do usuário a partir do token JWT.
    """
    credenciais_excecao = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id: str = payload.get("id")
        if usuario_id is None:
            raise credenciais_excecao
        return uuid.UUID(usuario_id)
    except (JWTError, ValueError):
        raise credenciais_excecao


@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
def api_registrar_usuario(
    dados: EsquemaUsuarioRegistro,
    requisicao: Request,
    componentes: dict = Depends(obter_servicos_e_repos)
):
    """Registra um novo usuário no sistema."""
    # Rate limit rigoroso para registro (3 por hora por IP)
    limiter.verificar_limite(requisicao.client.host, "/auth/register", limite=3, janela=3600)
    
    try:
        hash_senha = gerar_hash_senha(dados.senha)
        componentes["registrar_usuario"].executar(dados.email, hash_senha)
        return {"mensagem": "Usuário registrado com sucesso."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/auth/login", response_model=EsquemaToken)
def api_login(
    dados: EsquemaUsuarioLogin,
    requisicao: Request,
    componentes: dict = Depends(obter_servicos_e_repos)
):
    """Autentica o usuário e retorna um token JWT."""
    # Rate limit para login (5 por minuto por IP)
    limiter.verificar_limite(requisicao.client.host, "/auth/login", limite=5, janela=60)
    
    try:
        usuario = componentes["autenticar_usuario"].executar(dados.email)
        
        if not verificar_senha(dados.senha, usuario.senha_hash):
            raise HTTPException(status_code=401, detail="Usuário ou senha inválidos.")
        
        token = criar_token_acesso(dados={"sub": usuario.email, "id": str(usuario.id)})
        return EsquemaToken(access_token=token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/auditoria", response_model=List[EsquemaLogAuditoria])
def api_listar_auditoria(
    usuario_id: uuid.UUID = Depends(obter_usuario_atual),
    componentes: dict = Depends(obter_servicos_e_repos)
):
    """Retorna os logs de auditoria do usuário autenticado."""
    return componentes["listar_auditoria"].executar(usuario_id)

@router.post("/segredos", response_model=EsquemaCriarSegredoResponse, status_code=status.HTTP_201_CREATED)
def api_criar_segredo(
    dados: EsquemaCriarSegredoRequest,
    requisicao: Request,
    usuario_id: uuid.UUID = Depends(obter_usuario_atual),
    componentes: dict = Depends(obter_servicos_e_repos)
):
    """
    Cria um novo segredo e retorna a URL de acesso. Exige autenticação.
    """
    # 1. Rate Limit (Máximo 10 segredos por minuto por IP)
    limiter.verificar_limite(requisicao.client.host, "/segredos", limite=10, janela=60)

    # 2. Verificar Idempotência
    idem_key = requisicao.headers.get("X-Idempotency-Key")
    if idem_key:
        cached = idempotencia.obter_resposta_salva(idem_key)
        if cached:
            return cached

    try:
        id_segredo = componentes["criar_segredo"].executar(
            texto_puro=dados.texto_puro,
            horas_validade=dados.horas_validade,
            acessos_permitidos=dados.acessos_permitidos,
            dono_id=usuario_id,
            ip_origem=requisicao.client.host
        )
        
        url_base = f"{requisicao.base_url}segredos/{id_segredo}"
        resposta = {"id": str(id_segredo), "url_acesso": url_base}

        # 3. Salvar para idempotência
        if idem_key:
            idempotencia.salvar_resposta(idem_key, resposta)
            
        return resposta
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/segredos/{id_segredo}", response_model=EsquemaResgatarSegredoResponse)
def api_resgatar_segredo(
    id_segredo: uuid.UUID,
    requisicao: Request,
    componentes: dict = Depends(obter_servicos_e_repos)
):
    """
    Resgata o conteúdo de um segredo e diminui o contador de acessos.
    """
    try:
        texto = componentes["resgatar_segredo"].executar(
            id=id_segredo,
            ip_origem=requisicao.client.host
        )
        
        return EsquemaResgatarSegredoResponse(
            texto_puro=texto,
            data_expiracao=datetime.now(), # Simplificado para o exemplo
            acessos_restantes=0
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
