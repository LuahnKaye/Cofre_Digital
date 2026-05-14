import httpx
import time
import uuid

BASE_URL = "http://127.0.0.1:54321"

def testar_fluxo_completo():
    print("Iniciando teste de fluxo completo...")
    
    email = f"teste_{int(time.time())}@exemplo.com"
    senha = "senha_super_segura_123"

    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        # 1. Registro de Usuário
        print("--- Passo 1: Registrando usuário...")
        res = client.post("/auth/register", json={"email": email, "senha": senha})
        assert res.status_code == 201, f"Falha no registro: {res.text}"
        print("OK: Usuario registrado.")

        # 2. Login
        print("--- Passo 2: Realizando login...")
        res = client.post("/auth/login", json={"email": email, "senha": senha})
        assert res.status_code == 200, f"Falha no login: {res.text}"
        token = res.json()["access_token"]
        print("OK: Login realizado, token obtido.")

        # 3. Criar Segredo (Protegido)
        print("--- Passo 3: Criando um segredo...")
        headers = {"Authorization": f"Bearer {token}"}
        segredo_original = "Este é um segredo de teste " + str(uuid.uuid4())
        res = client.post("/segredos", 
                         json={"texto_puro": segredo_original, "horas_validade": 1, "acessos_permitidos": 1},
                         headers=headers)
        assert res.status_code == 201, f"Falha ao criar segredo: {res.text}"
        id_segredo = res.json()["id"]
        print(f"OK: Segredo criado com ID: {id_segredo}")

        # 4. Resgatar Segredo (Público)
        print("--- Passo 4: Resgatando o segredo...")
        res = client.get(f"/segredos/{id_segredo}")
        assert res.status_code == 200, f"Falha ao resgatar segredo: {res.text}"
        assert res.json()["texto_puro"] == segredo_original
        print("OK: Conteudo resgatado confere com o original.")

        # 5. Tentar resgatar novamente (Deve falhar - Destruição)
        print("--- Passo 5: Verificando destruicao automatica...")
        res = client.get(f"/segredos/{id_segredo}")
        assert res.status_code == 404, "ERRO: O segredo deveria ter sido destruido mas ainda esta acessivel."
        print("OK: Segredo destruido com sucesso apos o primeiro acesso.")

        # 6. Verificar Logs de Auditoria
        print("--- Passo 6: Verificando painel de auditoria...")
        res = client.get("/auditoria", headers=headers)
        assert res.status_code == 200, f"Falha ao buscar auditoria: {res.text}"
        logs = res.json()
        print(f"DEBUG: Logs recebidos: {len(logs)}")
        for log in logs:
            print(f"  - Evento: {log['tipo_evento']}")
        
        assert len(logs) >= 2, f"Esperava pelo menos 2 logs, recebi {len(logs)}"
        print(f"OK: Auditoria registrou {len(logs)} eventos para este usuario.")

    print("\nSUCESSO: TODOS OS TESTES PASSARAM!")

if __name__ == "__main__":
    try:
        testar_fluxo_completo()
    except Exception as e:
        print(f"ERRO: TESTE FALHOU: {str(e)}")
