-- Criação de extensões necessárias para segurança e UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Comentário para auditoria: Banco de dados inicializado com sucesso
DO $$ 
BEGIN 
    RAISE NOTICE 'Inicializando banco de dados do Cofre Digital...';
END $$;
