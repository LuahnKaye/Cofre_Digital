from datetime import datetime
from typing import Optional
import uuid

class Segredo:
    """
    Representa a entidade principal de um segredo efêmero no sistema.

    Atributos:
        id (uuid.UUID): Identificador único do segredo.
        conteudo_cifrado (str): O conteúdo do segredo já criptografado.
        data_criacao (datetime): Momento em que o segredo foi gerado.
        data_expiracao (datetime): Data limite para o resgate do segredo.
        acessos_permitidos (int): Quantidade de vezes que pode ser lido antes de ser destruído.
        acessos_realizados (int): Contador de quantas vezes o segredo já foi acessado.
        dono_id (Optional[uuid.UUID]): ID do usuário que criou o segredo (opcional).
    """

    def __init__(
        self,
        conteudo_cifrado: str,
        data_expiracao: datetime,
        acessos_permitidos: int = 1,
        id: Optional[uuid.UUID] = None,
        dono_id: Optional[uuid.UUID] = None
    ):
        self.id = id or uuid.uuid4()
        self.conteudo_cifrado = conteudo_cifrado
        self.data_criacao = datetime.now()
        self.data_expiracao = data_expiracao
        self.acessos_permitidos = acessos_permitidos
        self.acessos_realizados = 0
        self.dono_id = dono_id

    def esta_expirado(self) -> bool:
        """
        Verifica se o segredo já ultrapassou a data de validade.

        Returns:
            bool: Verdadeiro se estiver expirado.
        """
        return datetime.now() > self.data_expiracao

    def pode_ser_acessado(self) -> bool:
        """
        Verifica se o segredo ainda possui acessos disponíveis e não expirou.

        Returns:
            bool: Verdadeiro se o acesso for permitido.
        """
        return not self.esta_expirado() and self.acessos_realizados < self.acessos_permitidos

    def registrar_acesso(self):
        """
        Incrementa o contador de acessos realizados.
        """
        self.acessos_realizados += 1


class Usuario:
    """
    Representa um usuário autenticado no sistema.
    """

    def __init__(
        self,
        email: str,
        senha_hash: str,
        id: Optional[uuid.UUID] = None
    ):
        self.id = id or uuid.uuid4()
        self.email = email
        self.senha_hash = senha_hash
        self.data_criacao = datetime.now()


class LogDeAuditoria:
    """
    Representa um registro de evento para fins de auditoria e segurança.
    """

    def __init__(
        self,
        tipo_evento: str,
        detalhes: str,
        segredo_id: Optional[uuid.UUID] = None,
        usuario_id: Optional[uuid.UUID] = None,
        ip_origem: Optional[str] = None,
        id: Optional[uuid.UUID] = None
    ):
        self.id = id or uuid.uuid4()
        self.tipo_evento = tipo_evento
        self.detalhes = detalhes
        self.segredo_id = segredo_id
        self.usuario_id = usuario_id
        self.ip_origem = ip_origem
        self.data_evento = datetime.now()
