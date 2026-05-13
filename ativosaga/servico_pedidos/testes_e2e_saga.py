import pytest
import httpx
import time

# Configurações de URLs internas (Rede Docker)
URL_IDENTIDADE = "http://identidade:8000"
URL_PEDIDOS = "http://127.0.0.1:8000" # Rodando dentro do container de pedidos
URL_PAGAMENTOS = "http://pagamentos:8000"
URL_ESTOQUE = "http://estoque:8000"
URL_ATIVOS = "http://ativos:8000"

@pytest.fixture(scope="session", autouse=True)
def aguardar_servicos():
    """Garante que as APIs estão prontas antes de iniciar os testes."""
    servicos = [URL_IDENTIDADE, URL_PEDIDOS, URL_PAGAMENTOS, URL_ESTOQUE, URL_ATIVOS]
    for url in servicos:
        for _ in range(10):
            try:
                resp = httpx.get(url + "/docs") # Swagger costuma estar sempre lá
                if resp.status_code == 200:
                    break
            except Exception:
                pass
            time.sleep(2)
    print("\n[READY] Todos os serviços estão online.")

@pytest.fixture(scope="session")
def token_auth():
    """Cria um usuário e obtém o token para os testes."""
    email = f"teste_saga_{int(time.time())}@ativosaga.com"
    senha = "SenhaForte123"
    
    # Registro
    httpx.post(f"{URL_IDENTIDADE}/registro", json={"nome": "Tester Saga", "email": email, "senha": senha})
    
    # Login
    resp = httpx.post(f"{URL_IDENTIDADE}/login", json={"email": email, "senha": senha})
    return resp.json()["token_acesso"]

def test_cenario_1_sucesso_total(token_auth):
    """
    Cenário: Compra com sucesso.
    Fluxo: Pedido -> Estoque Reservado -> Pagamento OK -> Ativo Liberado -> Pedido PAGO.
    """
    id_produto = 501
    headers = {"Authorization": f"Bearer {token_auth}"}
    
    # 1. Definir estoque absoluto para o teste
    httpx.post(f"{URL_ESTOQUE}/definir", json={"id_produto": id_produto, "quantidade": 10})
    
    # 2. Criar Pedido
    resp_pedido = httpx.post(f"{URL_PEDIDOS}/pedidos/", headers=headers, json={
        "id_produto": id_produto,
        "quantidade": 1,
        "preco_total": 99.90
    })
    assert resp_pedido.status_code == 200
    id_pedido = resp_pedido.json()["id"]
    id_usuario = resp_pedido.json()["id_usuario"]
    
    # 3. Verificar status intermediário (PENDENTE)
    time.sleep(1) # Aguarda processamento RabbitMQ
    resp_status = httpx.get(f"{URL_PEDIDOS}/pedidos/{id_pedido}", headers=headers)
    assert resp_status.json()["status"] == "PENDENTE"
    
    # 4. Verificar reserva no estoque
    resp_estoque = httpx.get(f"{URL_ESTOQUE}/status/{id_produto}")
    assert resp_estoque.json()["reservado"] >= 1
    
    # 5. Simular Pagamento com Sucesso (Webhook/Manual)
    httpx.post(f"{URL_PAGAMENTOS}/teste-sucesso?id_pedido={id_pedido}&id_usuario={id_usuario}&id_produto={id_produto}")
    
    # 6. Aguardar processamento da Saga
    time.sleep(3)
    
    # 7. Verificar Status Final do Pedido
    resp_final = httpx.get(f"{URL_PEDIDOS}/pedidos/{id_pedido}", headers=headers)
    assert resp_final.json()["status"] == "PAGO"
    
    # 8. Verificar se o Ativo foi liberado na biblioteca
    resp_ativos = httpx.get(f"{URL_ATIVOS}/minha-biblioteca", headers=headers)
    assert any(a["id_produto"] == id_produto for a in resp_ativos.json())
    
    # 9. Verificar baixa definitiva no estoque (reservado volta a 0, disponivel continua -1)
    resp_estoque_final = httpx.get(f"{URL_ESTOQUE}/status/{id_produto}")
    assert resp_estoque_final.json()["reservado"] == 0

def test_cenario_2_falha_pagamento_compensacao(token_auth):
    """
    Cenário: Pagamento falha.
    Fluxo: Pedido -> Estoque Reservado -> Pagamento FALHA -> Estoque Devolvido -> Pedido CANCELADO.
    """
    id_produto = 502
    headers = {"Authorization": f"Bearer {token_auth}"}
    
    # 1. Definir estoque
    httpx.post(f"{URL_ESTOQUE}/definir", json={"id_produto": id_produto, "quantidade": 5})
    
    # 2. Criar Pedido
    resp_pedido = httpx.post(f"{URL_PEDIDOS}/pedidos/", headers=headers, json={
        "id_produto": id_produto,
        "quantidade": 1,
        "preco_total": 50.00
    })
    id_pedido = resp_pedido.json()["id"]
    id_usuario = resp_pedido.json()["id_usuario"]
    
    # 3. Simular Falha de Pagamento
    httpx.post(f"{URL_PAGAMENTOS}/teste-falha?id_pedido={id_pedido}&id_usuario={id_usuario}&id_produto={id_produto}&quantidade=1")
    
    # 4. Aguardar compensação
    time.sleep(3)
    
    # 5. Verificar se o estoque foi devolvido (disponível deve voltar a 5, reservado a 0)
    resp_estoque = httpx.get(f"{URL_ESTOQUE}/status/{id_produto}")
    assert resp_estoque.json()["disponivel"] == 5
    assert resp_estoque.json()["reservado"] == 0
    
    # 6. Verificar status do pedido (CANCELADO)
    resp_status = httpx.get(f"{URL_PEDIDOS}/pedidos/{id_pedido}", headers=headers)
    assert resp_status.json()["status"] == "CANCELADO"

def test_cenario_3_estoque_insuficiente(token_auth):
    """
    Cenário: Tentativa de compra sem estoque.
    Fluxo: Pedido -> Estoque Recusa -> Pedido continua PENDENTE (aguardando resposta que nunca vem ou timeout).
    Nota: No sistema atual, o estoque dá NACK mas não avisa o Pedido diretamente.
    """
    id_produto = 503
    headers = {"Authorization": f"Bearer {token_auth}"}
    
    # 1. Zerar estoque
    # (Poderíamos ter uma rota de reset, mas vamos adicionar 0 e garantir que está zerado se o banco for novo)
    # Para garantir, vamos tentar comprar 100 de algo que tem 0.
    
    # 2. Criar Pedido
    resp_pedido = httpx.post(f"{URL_PEDIDOS}/pedidos/", headers=headers, json={
        "id_produto": id_produto,
        "quantidade": 100,
        "preco_total": 10.00
    })
    id_pedido = resp_pedido.json()["id"]
    
    time.sleep(2)
    
    # 3. O pedido deve permanecer PENDENTE (ou falhar se tivermos lógica de timeout - não implementada ainda)
    resp_status = httpx.get(f"{URL_PEDIDOS}/pedidos/{id_pedido}", headers=headers)
    if resp_status.status_code != 200:
        print(f"Erro ao buscar status: {resp_status.text}")
    assert resp_status.status_code == 200
    assert resp_status.json()["status"] == "PENDENTE"

