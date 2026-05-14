import time
import redis
import os
from fastapi import Request, HTTPException
from dotenv import load_dotenv

load_dotenv()

class RateLimiter:
    """
    Implementação de Rate Limiting usando Redis (Fixed Window).
    Controla o número de requisições por IP em um determinado tempo.
    """

    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            password=os.getenv("REDIS_PASSWORD", "senha_redis_123"),
            db=0,
            decode_responses=True
        )

    def verificar_limite(self, ip: str, endpoint: str, limite: int = 10, janela: int = 60):
        """
        Verifica se o IP atingiu o limite de requisições.
        
        Args:
            ip (str): IP do cliente.
            endpoint (str): Rota acessada.
            limite (int): Máximo de requisições permitidas.
            janela (int): Tempo em segundos.
        """
        chave = f"rate_limit:{ip}:{endpoint}"
        
        # Incrementa o contador
        requisicoes = self.redis_client.incr(chave)
        
        # Se for a primeira requisição, define o TTL
        if requisicoes == 1:
            self.redis_client.expire(chave, janela)
            
        if requisicoes > limite:
            tempo_restante = self.redis_client.ttl(chave)
            raise HTTPException(
                status_code=429, 
                detail={
                    "erro": "Muitas requisições",
                    "retry_after": f"{tempo_restante}s"
                }
            )
        
        return True
