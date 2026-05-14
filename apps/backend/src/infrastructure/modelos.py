from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
import uuid
from datetime import datetime

Base = declarative_base()

class ModeloUsuario(Base):
    """Modelo de banco de dados para a tabela de usuários."""
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    data_criacao = Column(DateTime, default=datetime.now)

    segredos = relationship("ModeloSegredo", back_populates="dono")


class ModeloSegredo(Base):
    """Modelo de banco de dados para a tabela de segredos."""
    __tablename__ = "segredos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conteudo_cifrado = Column(Text, nullable=False)
    data_criacao = Column(DateTime, default=datetime.now)
    data_expiracao = Column(DateTime, nullable=False)
    acessos_permitidos = Column(Integer, default=1)
    acessos_realizados = Column(Integer, default=0)
    
    dono_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    dono = relationship("ModeloUsuario", back_populates="segredos")


class ModeloLogDeAuditoria(Base):
    """Modelo de banco de dados para a tabela de logs de auditoria."""
    __tablename__ = "logs_auditoria"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tipo_evento = Column(String(50), nullable=False)
    detalhes = Column(Text)
    data_evento = Column(DateTime, default=datetime.now)
    
    segredo_id = Column(UUID(as_uuid=True), nullable=True)
    usuario_id = Column(UUID(as_uuid=True), nullable=True)
    ip_origem = Column(String(45)) # Suporte a IPv6


class ModeloOutbox(Base):
    """
    Tabela de Outbox para garantir a entrega atômica de mensagens (Transactional Outbox Pattern).
    """
    __tablename__ = "outbox_mensagens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tipo_evento = Column(String(100), nullable=False)
    payload = Column(Text, nullable=False) # JSON
    processado = Column(Boolean, default=False)
    data_criacao = Column(DateTime, default=datetime.now)
    data_processamento = Column(DateTime, nullable=True)
