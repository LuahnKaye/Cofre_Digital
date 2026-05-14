import pika
import json
import os
import uuid
import sys
from infrastructure.banco_de_dados import SessionLocal
from infrastructure.repositorios_sql import RepositorioSegredoSQL
from dotenv import load_dotenv

load_dotenv()

def processar_destruicao(ch, method, properties, body):
    """
    Callback executado quando um evento de destruição é recebido.
    """
    print(f" [x] Recebido evento para destruição: {body}")
    dados = json.loads(body)
    segredo_id = uuid.UUID(dados['id'])

    # Criamos uma sessão de banco exclusiva para este processamento
    db = SessionLocal()
    try:
        repo = RepositorioSegredoSQL(db)
        repo.deletar(segredo_id)
        print(f" [ok] Segredo {segredo_id} deletado fisicamente do banco.")
        
        # Confirma o processamento para o RabbitMQ
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f" [!] Erro ao processar destruição: {str(e)}")
        # Em caso de erro, a mensagem volta para a fila para ser processada novamente (requeue)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    finally:
        db.close()

def iniciar_worker():
    """
    Inicia o consumidor RabbitMQ.
    """
    host = os.getenv("RABBITMQ_HOST", "localhost")
    port = int(os.getenv("RABBITMQ_PORT", "5672"))
    usuario = os.getenv("RABBITMQ_USER", "guest")
    senha = os.getenv("RABBITMQ_PASSWORD", "guest")
    
    credenciais = pika.PlainCredentials(usuario, senha)
    parametros = pika.ConnectionParameters(host=host, port=port, credentials=credenciais)
    
    try:
        conexao = pika.BlockingConnection(parametros)
        canal = conexao.channel()

        # Garante que o exchange e a fila existam
        canal.exchange_declare(exchange='cofre_digital_events', exchange_type='topic', durable=True)
        
        resultado = canal.queue_declare(queue='fila_destruicao', durable=True)
        nome_fila = resultado.method.queue
        
        # Faz o bind da fila para ouvir o evento específico
        canal.queue_bind(exchange='cofre_digital_events', queue=nome_fila, routing_key='segredo.destruir')

        print(' [*] Worker aguardando eventos de destruição. Para sair pressione CTRL+C')
        
        canal.basic_qos(prefetch_count=1) # Processa um por vez
        canal.basic_consume(queue=nome_fila, on_message_callback=processar_destruicao)

        canal.start_consuming()
    except Exception as e:
        print(f" [FATAL] Worker interrompido: {str(e)}")

if __name__ == "__main__":
    iniciar_worker()
