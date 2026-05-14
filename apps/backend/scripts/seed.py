import sys
import os
import uuid
from datetime import datetime, timedelta

# Adiciona o diretório src ao path para importar os módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from infrastructure.banco_de_dados import SessionLocal
from infrastructure.modelos import ModeloUsuario, ModeloSegredo
from infrastructure.seguranca import gerar_hash_senha

def popular_banco():
    db = SessionLocal()
    try:
        # 1. Cria Usuário de Teste
        email_teste = "admin@cofre.com"
        usuario_existente = db.query(ModeloUsuario).filter(ModeloUsuario.email == email_teste).first()
        
        if not usuario_existente:
            print(f"[*] Criando usuário: {email_teste}")
            novo_usuario = ModeloUsuario(
                id=uuid.uuid4(),
                email=email_teste,
                senha_hash=gerar_hash_senha("senha123")
            )
            db.add(novo_usuario)
            db.commit()
            db.refresh(novo_usuario)
            usuario = novo_usuario
        else:
            print("[!] Usuário admin já existe.")
            usuario = usuario_existente

        # 2. Cria Segredo de Boas-vindas
        print("[*] Criando segredo de boas-vindas...")
        segredo_demo = ModeloSegredo(
            id=uuid.uuid4(),
            conteudo_cifrado="Conteúdo de Boas-vindas (Cifrado no DB)",
            data_criacao=datetime.now(),
            data_expiracao=datetime.now() + timedelta(days=7),
            acessos_permitidos=10,
            acessos_realizados=0,
            dono_id=usuario.id
        )
        db.add(segredo_demo)
        db.commit()
        
        print("\n[✓] Banco de dados populado com sucesso!")
        print(f"    - Usuário: {email_teste}")
        print(f"    - Senha: senha123")
        
    except Exception as e:
        print(f"[X] Erro ao popular banco: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    popular_banco()
