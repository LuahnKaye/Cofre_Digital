import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

load_dotenv()

# URL de conexão montada a partir das variáveis de ambiente
DB_USER = os.getenv("POSTGRES_USER", "usuario_cofre")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "senha_cofre_123")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "cofre_digital_db")

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Engine do SQLAlchemy
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True # Garante que a conexão está viva antes de usar
)

# Fábrica de Sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def obter_sessao():
    """
    Gera uma nova sessão do banco de dados e garante seu fechamento após o uso.
    Utilizado principalmente como dependência no FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
