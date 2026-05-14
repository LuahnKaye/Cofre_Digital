import pika
import json
import os
from application.servicos import ServicoDeMensageria
from dotenv import load_dotenv

load_dotenv()

class PublicadorRabbitMQ(ServicoDeMensageria):
    """
    Implementação real de mensageria usando RabbitMQ.
    
    Responsável por publicar eventos que serão consumidos de forma assíncrona.
    """

    def __init__(self):
        # Configurações do RabbitMQ
        self.host = os.getenv("RABBITMQ_HOST", "localhost")
        self.port = int(os.getenv("RABBITMQ_PORT", "5672"))
        self.usuario = os.getenv("RABBITMQ_USER", "guest")
        self.senha = os.getenv("RABBITMQ_PASSWORD", "guest")
        
        self.exchange_nome = "cofre_digital_events"
        self.credenciais = pika.PlainCredentials(self.usuario, self.senha)
        self.parametros = pika.ConnectionParameters(
            host=self.host, 
            port=self.port, 
            credentials=self.credenciais,
            heartbeat=600,
            blocked_connection_timeout=300
        )

    def _obter_conexao(self):
        """Cria uma conexão e um canal temporário para publicação."""
        conexao = pika.BlockingConnection(self.parametros)
        canal = conexao.channel()
        
        # Declara o exchange para garantir que ele exista
        canal.exchange_declare(
            exchange=self.exchange_nome, 
            exchange_type='topic', 
            durable=True
        )
        return conexao, canal

    def publicar_evento(self, tipo_evento: str, dados: dict) -> None:
        """
        Publica um evento JSON no RabbitMQ usando o padrão Topic.
        """
        try:
            conexao, canal = self._obter_conexao()
            
            mensagem = json.dumps(dados)
            canal.basic_publish(
                exchange=self.exchange_nome,
                routing_key=tipo_evento, # Ex: segredo.destruir
                body=mensagem,
                properties=pika.BasicProperties(
                    delivery_mode=2, # Torna a mensagem persistente
                    content_type='application/json'
                )
            )
            
            print(f"[RABBITMQ] Evento publicado: {tipo_evento}")
            conexao.close()
        except Exception as e:
            print(f"[RABBITMQ ERROR] Falha ao publicar evento: {str(e)}")
            # Em produção, aqui implementaríamos o Transactional Outbox 
            # para salvar no banco se o RabbitMQ falhar.
            raise e
