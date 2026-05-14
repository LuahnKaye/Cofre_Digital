import os
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

# Configurações de Segurança
SECRET_KEY = os.getenv("JWT_SECRET", "seu_segredo_super_secreto_para_desenvolvimento")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Contexto para hashing de senhas usando Argon2
contexto_senha = CryptContext(schemes=["argon2"], deprecated="auto")

def gerar_hash_senha(senha: str) -> str:
    """Gera o hash de uma senha usando Argon2."""
    return contexto_senha.hash(senha)

def verificar_senha(senha_puro: str, senha_hash: str) -> bool:
    """Verifica se a senha puro corresponde ao hash."""
    return contexto_senha.verify(senha_puro, senha_hash)

def criar_token_acesso(dados: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria um token JWT para autenticação."""
    para_codificar = dados.copy()
    if expires_delta:
        expiracao = datetime.utcnow() + expires_delta
    else:
        expiracao = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    para_codificar.update({"exp": expiracao})
    encoded_jwt = jwt.encode(para_codificar, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
