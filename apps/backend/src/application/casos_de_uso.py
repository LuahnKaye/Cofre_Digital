from datetime import datetime, timedelta
from typing import Optional, List
import uuid
from domain.entidades import Segredo, LogDeAuditoria, Usuario
from application.repositorios import RepositorioSegredo, RepositorioAuditoria, RepositorioUsuario
from application.servicos import ServicoDeCriptografia, ServicoDeMensageria

class CriarSegredo:
    """
    Caso de Uso (Command) para a criação de um novo segredo.
    """

    def __init__(
        self,
        repo_segredo: RepositorioSegredo,
        repo_auditoria: RepositorioAuditoria,
        servico_crypto: ServicoDeCriptografia,
        servico_mensageria: ServicoDeMensageria
    ):
        self.repo_segredo = repo_segredo
        self.repo_auditoria = repo_auditoria
        self.servico_crypto = servico_crypto
        self.servico_mensageria = servico_mensageria

    def executar(
        self,
        texto_puro: str,
        horas_validade: int = 24,
        acessos_permitidos: int = 1,
        dono_id: Optional[uuid.UUID] = None,
        ip_origem: Optional[str] = None
    ) -> uuid.UUID:
        """
        Executa a lógica de negócio para criar e persistir um segredo.
        """
        # 1. Criptografa o conteúdo
        conteudo_cifrado = self.servico_crypto.cifrar(texto_puro)

        # 2. Define a data de expiração
        data_expiracao = datetime.now() + timedelta(hours=horas_validade)

        # 3. Instancia a entidade
        novo_segredo = Segredo(
            conteudo_cifrado=conteudo_cifrado,
            data_expiracao=data_expiracao,
            acessos_permitidos=acessos_permitidos,
            dono_id=dono_id
        )

        # 4. Persiste no repositório
        self.repo_segredo.salvar(novo_segredo)

        # 5. Registra log de auditoria
        log = LogDeAuditoria(
            tipo_evento="CRIACAO_SEGREDO",
            detalhes=f"Segredo criado com validade de {horas_validade}h.",
            segredo_id=novo_segredo.id,
            usuario_id=dono_id,
            ip_origem=ip_origem
        )
        self.repo_auditoria.registrar(log)

        # 6. Notifica via EDA (Event-Driven Architecture)
        self.servico_mensageria.publicar_evento("segredo.criado", {
            "id": str(novo_segredo.id),
            "data_expiracao": str(data_expiracao)
        })

        return novo_segredo.id


class ResgatarEDestruirSegredo:
    """
    Caso de Uso (Query/Command) para resgatar um segredo e destruí-lo.
    """

    def __init__(
        self,
        repo_segredo: RepositorioSegredo,
        repo_auditoria: RepositorioAuditoria,
        servico_crypto: ServicoDeCriptografia,
        servico_mensageria: ServicoDeMensageria
    ):
        self.repo_segredo = repo_segredo
        self.repo_auditoria = repo_auditoria
        self.servico_crypto = servico_crypto
        self.servico_mensageria = servico_mensageria

    def executar(self, id: uuid.UUID, ip_origem: Optional[str] = None) -> str:
        """
        Busca o segredo, decifra-o e agenda sua destruição.
        """
        # 1. Recupera o segredo do repositório
        segredo = self.repo_segredo.obter_por_id(id)

        if not segredo:
            raise Exception("Segredo não encontrado ou já destruído.")

        # 2. Valida se pode ser acessado (regras de negócio no domínio)
        if not segredo.pode_ser_acessado():
            # Notifica tentativa de acesso inválida
            self.servico_mensageria.publicar_evento("segredo.acesso_negado", {
                "id": str(id),
                "motivo": "Expirado ou limite de acessos atingido"
            })
            raise Exception("Este segredo não está mais disponível.")

        # 3. Decifra o conteúdo
        texto_puro = self.servico_crypto.decifrar(segredo.conteudo_cifrado)

        # 4. Registra o acesso (muta a entidade)
        segredo.registrar_acesso()
        self.repo_segredo.salvar(segredo)

        # 5. Se atingiu o limite, deleta fisicamente ou marca para deleção assíncrona
        if segredo.acessos_realizados >= segredo.acessos_permitidos:
            # Publica evento para deleção física assíncrona (EDA)
            self.servico_mensageria.publicar_evento("segredo.destruir", {
                "id": str(segredo.id)
            })

        # 6. Registra log de auditoria
        log = LogDeAuditoria(
            tipo_evento="RESGATE_SEGREDO",
            detalhes="Segredo resgatado com sucesso.",
            segredo_id=segredo.id,
            usuario_id=segredo.dono_id, # Vincula ao dono para que ele veja no painel
            ip_origem=ip_origem
        )
        self.repo_auditoria.registrar(log)

        return texto_puro


class RegistrarUsuario:
    """
    Caso de Uso para registrar um novo usuário no sistema.
    """

    def __init__(self, repo_usuario: RepositorioUsuario):
        self.repo_usuario = repo_usuario

    def executar(self, email: str, senha_hash: str) -> uuid.UUID:
        # Verifica se já existe
        existente = self.repo_usuario.obter_por_email(email)
        if existente:
            raise Exception("Este e-mail já está cadastrado.")

        novo_usuario = Usuario(email=email, senha_hash=senha_hash)
        self.repo_usuario.salvar(novo_usuario)
        return novo_usuario.id


class AutenticarUsuario:
    """
    Caso de Uso para validar credenciais de um usuário.
    """

    def __init__(self, repo_usuario: RepositorioUsuario):
        self.repo_usuario = repo_usuario

    def executar(self, email: str) -> Usuario:
        usuario = self.repo_usuario.obter_por_email(email)
        if not usuario:
            raise Exception("Usuário ou senha inválidos.")
        return usuario


class ListarLogsAuditoria:
    """
    Caso de Uso (Query) para listar logs de um usuário específico.
    """

    def __init__(self, repo_auditoria: RepositorioAuditoria):
        self.repo_auditoria = repo_auditoria

    def executar(self, usuario_id: uuid.UUID) -> List[LogDeAuditoria]:
        return self.repo_auditoria.listar_por_usuario(usuario_id)
