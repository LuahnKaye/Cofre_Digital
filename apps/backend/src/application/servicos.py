from abc import ABC, abstractmethod

class ServicoDeCriptografia(ABC):
    """
    Interface para o motor de criptografia do sistema.
    """

    @abstractmethod
    def cifrar(self, texto_puro: str) -> str:
        """Cifra o texto usando a estratégia de envelope (DEK/KEK)."""
        pass

    @abstractmethod
    def decifrar(self, texto_cifrado: str) -> str:
        """Decifra o conteúdo usando a estratégia de envelope."""
        pass


class ServicoDeMensageria(ABC):
    """
    Interface para publicação de eventos (EDA).
    """

    @abstractmethod
    def publicar_evento(self, tipo_evento: str, dados: dict) -> None:
        """Publica um evento assíncrono para o broker (RabbitMQ)."""
        pass
