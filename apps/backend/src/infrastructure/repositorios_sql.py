import uuid
import json
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from application.repositorios import RepositorioSegredo, RepositorioUsuario, RepositorioAuditoria, RepositorioOutbox
from domain.entidades import Segredo, Usuario, LogDeAuditoria
from infrastructure.modelos import ModeloSegredo, ModeloUsuario, ModeloLogDeAuditoria, ModeloOutbox

class RepositorioSegredoSQL(RepositorioSegredo):
    """Implementação SQL do repositório de segredos."""

    def __init__(self, sessao: Session):
        self.sessao = sessao

    def salvar(self, segredo: Segredo) -> None:
        # Tenta encontrar se já existe (para update) ou cria novo
        modelo = self.sessao.query(ModeloSegredo).filter(ModeloSegredo.id == segredo.id).first()
        
        if not modelo:
            modelo = ModeloSegredo(
                id=segredo.id,
                conteudo_cifrado=segredo.conteudo_cifrado,
                data_criacao=segredo.data_criacao,
                data_expiracao=segredo.data_expiracao,
                acessos_permitidos=segredo.acessos_permitidos,
                acessos_realizados=segredo.acessos_realizados,
                dono_id=segredo.dono_id
            )
            self.sessao.add(modelo)
        else:
            modelo.acessos_realizados = segredo.acessos_realizados
        
        self.sessao.commit()

    def obter_por_id(self, id: uuid.UUID) -> Optional[Segredo]:
        modelo = self.sessao.query(ModeloSegredo).filter(ModeloSegredo.id == id).first()
        if not modelo:
            return None
            
        # Converte modelo DB para entidade de domínio
        segredo = Segredo(
            conteudo_cifrado=modelo.conteudo_cifrado,
            data_expiracao=modelo.data_expiracao,
            acessos_permitidos=modelo.acessos_permitidos,
            id=modelo.id,
            dono_id=modelo.dono_id
        )
        segredo.acessos_realizados = modelo.acessos_realizados
        segredo.data_criacao = modelo.data_criacao
        return segredo

    def deletar(self, id: uuid.UUID) -> None:
        self.sessao.query(ModeloSegredo).filter(ModeloSegredo.id == id).delete()
        self.sessao.commit()


class RepositorioAuditoriaSQL(RepositorioAuditoria):
    """Implementação SQL do repositório de logs de auditoria."""

    def __init__(self, sessao: Session):
        self.sessao = sessao

    def registrar(self, log: LogDeAuditoria) -> None:
        modelo = ModeloLogDeAuditoria(
            id=log.id,
            tipo_evento=log.tipo_evento,
            detalhes=log.detalhes,
            data_evento=log.data_evento,
            segredo_id=log.segredo_id,
            usuario_id=log.usuario_id,
            ip_origem=log.ip_origem
        )
        self.sessao.add(modelo)
        self.sessao.commit()

    def listar_por_usuario(self, usuario_id: uuid.UUID) -> List[LogDeAuditoria]:
        modelos = self.sessao.query(ModeloLogDeAuditoria).filter(ModeloLogDeAuditoria.usuario_id == usuario_id).all()
        return [
            LogDeAuditoria(
                tipo_evento=m.tipo_evento,
                detalhes=m.detalhes,
                segredo_id=m.segredo_id,
                usuario_id=m.usuario_id,
                ip_origem=m.ip_origem,
                id=m.id
            ) for m in modelos
        ]


class RepositorioUsuarioSQL(RepositorioUsuario):
    """Implementação SQL do repositório de usuários."""

    def __init__(self, sessao: Session):
        self.sessao = sessao

    def salvar(self, usuario: Usuario) -> None:
        modelo = ModeloUsuario(
            id=usuario.id,
            email=usuario.email,
            senha_hash=usuario.senha_hash,
            data_criacao=usuario.data_criacao
        )
        self.sessao.add(modelo)
        self.sessao.commit()

    def obter_por_email(self, email: str) -> Optional[Usuario]:
        modelo = self.sessao.query(ModeloUsuario).filter(ModeloUsuario.email == email).first()
        if not modelo:
            return None
        
        return Usuario(
            email=modelo.email,
            senha_hash=modelo.senha_hash,
            id=modelo.id
        )


class RepositorioOutboxSQL(RepositorioOutbox):
    """Implementação SQL do repositório de Outbox."""

    def __init__(self, sessao: Session):
        self.sessao = sessao

    def salvar(self, tipo_evento: str, payload: dict) -> None:
        modelo = ModeloOutbox(
            tipo_evento=tipo_evento,
            payload=json.dumps(payload)
        )
        self.sessao.add(modelo)
        # O commit aqui geralmente é controlado pelo Use Case ou Unit of Work
        # Mas para simplificar as interfaces atuais, faremos aqui.
        self.sessao.commit()

    def obter_pendentes(self) -> List[dict]:
        modelos = self.sessao.query(ModeloOutbox).filter(ModeloOutbox.processado == False).all()
        return [
            {
                "id": m.id,
                "tipo_evento": m.tipo_evento,
                "payload": json.loads(m.payload)
            } for m in modelos
        ]

    def marcar_como_processado(self, id: uuid.UUID) -> None:
        modelo = self.sessao.query(ModeloOutbox).filter(ModeloOutbox.id == id).first()
        if modelo:
            modelo.processado = True
            modelo.data_processamento = datetime.now()
            self.sessao.commit()
