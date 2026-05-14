import redis
import os
import json
from fastapi import Request, Response
from dotenv import load_dotenv

load_dotenv()

class ServicoIdempotencia:
    """
    Garante que operações mutáveis não sejam executadas mais de uma vez para o mesmo ID.
    Útil para evitar duplicidade em criação de segredos ou registros.
    """

    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            password=os.getenv("REDIS_PASSWORD", "senha_redis_123"),
            db=1, # Usamos uma DB diferente para não misturar com Rate Limit
            decode_responses=True
        )

    def obter_resposta_salva(self, chave: str):
        """Busca se já existe uma resposta para esta chave de idempotência."""
        cached = self.redis_client.get(f"idempotencia:{chave}")
        if cached:
            return json.loads(cached)
        return None

    def salvar_resposta(self, chave: str, resposta: dict, expira_em: int = 86400):
        """Salva a resposta de sucesso no Redis por 24h."""
        self.redis_client.setex(
            f"idempotencia:{chave}",
            expira_em,
            json.dumps(resposta)
        )
