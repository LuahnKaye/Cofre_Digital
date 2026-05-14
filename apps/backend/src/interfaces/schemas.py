from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
import uuid

class EsquemaCriarSegredoRequest(BaseModel):
    """Dados necessários para criar um novo segredo."""
    texto_puro: str = Field(..., min_length=1, description="O conteúdo sensível a ser guardado.")
    horas_validade: int = Field(24, ge=1, le=168, description="Tempo de vida do segredo em horas.")
    acessos_permitidos: int = Field(1, ge=1, le=10, description="Número máximo de leituras antes da destruição.")

class EsquemaCriarSegredoResponse(BaseModel):
    """Resposta após a criação bem-sucedida de um segredo."""
    id: uuid.UUID
    url_acesso: str

class EsquemaResgatarSegredoResponse(BaseModel):
    """Dados retornados ao resgatar um segredo."""
    texto_puro: str
    data_expiracao: datetime
    acessos_restantes: int

class EsquemaMensagemErro(BaseModel):
    """Modelo padrão para mensagens de erro."""
    detalhe: str


class EsquemaUsuarioRegistro(BaseModel):
    """Dados para registrar um novo usuário."""
    email: EmailStr
    senha: str = Field(..., min_length=8)


class EsquemaUsuarioLogin(BaseModel):
    """Dados para realizar login."""
    email: EmailStr
    senha: str


class EsquemaToken(BaseModel):
    """Token de acesso retornado após login."""
    access_token: str
    token_type: str = "bearer"


class EsquemaLogAuditoria(BaseModel):
    """Registro individual de auditoria."""
    tipo_evento: str
    detalhes: str
    data_evento: datetime
    segredo_id: Optional[uuid.UUID]
    ip_origem: Optional[str]
