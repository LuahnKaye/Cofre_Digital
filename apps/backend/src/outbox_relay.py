import time
import os
import sys
from infrastructure.banco_de_dados import SessionLocal
from infrastructure.repositorios_sql import RepositorioOutboxSQL
from infrastructure.mensageria import PublicadorRabbitMQ
from dotenv import load_dotenv

load_dotenv()

def iniciar_relay():
    """
    O Relay fica em loop buscando mensagens não processadas na tabela Outbox
    e enviando-as para o Broker de Mensagens (RabbitMQ).
    """
    print(" [*] Outbox Relay iniciado. Monitorando tabela 'outbox_mensagens'...")
    
    # Instanciamos o publicador real do RabbitMQ
    publicador_real = PublicadorRabbitMQ()

    while True:
        db = SessionLocal()
        try:
            repo_outbox = RepositorioOutboxSQL(db)
            
            # 1. Busca mensagens pendentes
            mensagens = repo_outbox.obter_pendentes()
            
            if mensagens:
                print(f" [outbox] Processando {len(mensagens)} mensagens pendentes...")
                
                for msg in mensagens:
                    try:
                        # 2. Tenta publicar no RabbitMQ
                        publicador_real.publicar_evento(
                            tipo_evento=msg["tipo_evento"],
                            dados=msg["payload"]
                        )
                        
                        # 3. Marca como processado se deu certo
                        repo_outbox.marcar_como_processado(msg["id"])
                        print(f" [outbox] Mensagem {msg['id']} enviada e marcada como processada.")
                    except Exception as e:
                        print(f" [!] Falha ao enviar mensagem {msg['id']}: {str(e)}")
                        # Se falhar o envio para o RabbitMQ, não marcamos como processado.
                        # Ela será tentada novamente no próximo ciclo.
            
        except Exception as e:
            print(f" [ERRO CRÍTICO] Falha no ciclo do Relay: {str(e)}")
        finally:
            db.close()
        
        # Intervalo entre as buscas (polling)
        time.sleep(5)

if __name__ == "__main__":
    iniciar_relay()
