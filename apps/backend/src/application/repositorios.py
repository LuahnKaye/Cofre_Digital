from abc import ABC, abstractmethod
from typing import Optional, List
import uuid
from domain.entidades import Segredo, Usuario, LogDeAuditoria

class RepositorioSegredo(ABC):
    """
    Interface (Porta) para o repositório de segredos.
    """

    @abstractmethod
    def salvar(self, segredo: Segredo) -> None:
        """Salva um novo segredo no banco."""
        pass

    @abstractmethod
    def obter_por_id(self, id: uuid.UUID) -> Optional[Segredo]:
        """Recupera um segredo pelo seu ID único."""
        pass

    @abstractmethod
    def deletar(self, id: uuid.UUID) -> None:
        """Remove fisicamente um segredo do banco."""
        pass


class RepositorioUsuario(ABC):
    """
    Interface para o repositório de usuários.
    """

    @abstractmethod
    def salvar(self, usuario: Usuario) -> None:
        pass

    @abstractmethod
    def obter_por_email(self, email: str) -> Optional[Usuario]:
        pass


class RepositorioAuditoria(ABC):
    """
    Interface para o repositório de logs de auditoria.
    """

    @abstractmethod
    def registrar(self, log: LogDeAuditoria) -> None:
        pass

    @abstractmethod
    def listar_por_usuario(self, usuario_id: uuid.UUID) -> List[LogDeAuditoria]:
        pass


class RepositorioOutbox(ABC):
    """
    Interface para persistência de mensagens do Outbox.
    """

    @abstractmethod
    def salvar(self, tipo_evento: str, payload: dict) -> None:
        """Salva a mensagem para envio posterior."""
        pass

    @abstractmethod
    def obter_pendentes(self) -> List[dict]:
        """Recupera mensagens que ainda não foram processadas."""
        pass

    @abstractmethod
    def marcar_como_processado(self, id: uuid.UUID) -> None:
        """Marca a mensagem como enviada com sucesso."""
        pass
