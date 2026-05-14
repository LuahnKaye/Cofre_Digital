from application.servicos import ServicoDeMensageria
from application.repositorios import RepositorioOutbox

class PublicadorViaOutbox(ServicoDeMensageria):
    """
    Implementação do ServicoDeMensageria que salva as mensagens no banco de dados
    (tabela Outbox) em vez de enviar diretamente para o Broker.
    
    Isso garante que a mensagem só será enviada se a transação do banco for persistida.
    """

    def __init__(self, repo_outbox: RepositorioOutbox):
        self.repo_outbox = repo_outbox

    def publicar_evento(self, tipo_evento: str, dados: dict) -> None:
        """Persiste o evento no banco de dados."""
        self.repo_outbox.salvar(tipo_evento, dados)
