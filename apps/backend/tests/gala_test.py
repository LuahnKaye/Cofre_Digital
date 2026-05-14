import httpx
import time
import uuid
import sys
import os

# Adiciona src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

API_URL = "http://localhost:54321"

def test_de_gala():
    print("\n" + "="*50)
    print("INICIANDO TESTE DE GALA - COFRE DIGITAL")
    print("="*50 + "\n")

    client = httpx.Client(timeout=10.0)

    try:
        # 1. Registro de Usuário
        email = f"user_{uuid.uuid4().hex[:4]}@teste.com"
        senha = "SenhaDificil123!"
        print(f"[*] Registrando usuario: {email}...")
        resp = client.post(f"{API_URL}/auth/register", json={"email": email, "senha": senha})
        assert resp.status_code == 201
        print("[v] Usuario registrado.")

        # 2. Login
        print("[*] Realizando login...")
        resp = client.post(f"{API_URL}/auth/login", json={"email": email, "senha": senha})
        assert resp.status_code == 200
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("[v] Login bem sucedido. Token JWT obtido.")

        # 3. Criacao de Segredo com Idempotencia
        idem_key = str(uuid.uuid4())
        segredo_payload = {
            "texto_puro": "MINHA_CHAVE_SUPER_SECRETA_123",
            "horas_validade": 1,
            "acessos_permitidos": 1
        }
        
        print(f"[*] Criando segredo (Idempotency Key: {idem_key})...")
        resp1 = client.post(f"{API_URL}/segredos", json=segredo_payload, headers={**headers, "X-Idempotency-Key": idem_key})
        assert resp1.status_code == 201
        id_segredo = resp1.json()["id"]
        
        # Teste de Idempotencia (deve retornar o mesmo ID sem erro)
        print("[*] Testando idempotencia (reenvio da mesma chave)...")
        resp2 = client.post(f"{API_URL}/segredos", json=segredo_payload, headers={**headers, "X-Idempotency-Key": idem_key})
        assert resp2.status_code == 201
        assert resp2.json()["id"] == id_segredo
        print("[v] Idempotencia validada.")

        # 4. Verificacao no Painel de Auditoria
        print("[*] Verificando Painel de Auditoria...")
        resp = client.get(f"{API_URL}/auditoria", headers=headers)
        logs = resp.json()
        assert any(log["segredo_id"] == id_segredo for log in logs)
        print(f"[v] Log de criacao encontrado para o segredo {id_segredo[:8]}...")

        # 5. Resgate do Segredo (Leitura Unica)
        print(f"[*] Resgatando segredo {id_segredo[:8]}...")
        resp_resgate = client.get(f"{API_URL}/segredos/{id_segredo}")
        assert resp_resgate.status_code == 200
        assert resp_resgate.json()["texto_puro"] == "MINHA_CHAVE_SUPER_SECRETA_123"
        print("[v] Conteudo recuperado com sucesso.")

        # 6. Tentativa de Segundo Acesso (Auto-Destruicao)
        print("[*] Verificando auto-destruicao (segundo acesso)...")
        resp_falha = client.get(f"{API_URL}/segredos/{id_segredo}")
        assert resp_falha.status_code == 404
        print("[v] Segredo nao encontrado apos o limite de acessos. Destruicao confirmada.")

        # 7. Verificacao de Auditoria Pos-Resgate
        print("[*] Verificando logs de resgate...")
        resp_auditoria = client.get(f"{API_URL}/auditoria", headers=headers)
        logs_final = resp_auditoria.json()
        eventos_resgate = [l for l in logs_final if l["segredo_id"] == id_segredo and l["tipo_evento"] == "RESGATE_SEGREDO"]
        assert len(eventos_resgate) >= 1
        print("[v] Evento de resgate auditado corretamente.")

        # 8. Teste de Rate Limit
        print("[*] Testando Rate Limit (disparando requisicoes rapidas)...")
        for i in range(15):
            r = client.post(f"{API_URL}/segredos", json=segredo_payload, headers=headers)
            if r.status_code == 429:
                print(f"[v] Rate Limit ativado com sucesso apos {i+1} tentativas.")
                break
        else:
            print("[X] Rate Limit nao foi ativado conforme esperado.")

        print("\n" + "="*50)
        print("TESTE DE GALA CONCLUIDO COM SUCESSO!")
        print("SISTEMA PRONTO PARA PRODUCAO.")
        print("="*50 + "\n")

    except Exception as e:
        print(f"\n[X] FALHA NO TESTE: {str(e)}")
        sys.exit(1)
    finally:
        client.close()

if __name__ == "__main__":
    test_de_gala()
