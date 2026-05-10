from fastapi.testclient import TestClient
from main import app
from banco_de_dados import obter_banco, motor_do_banco
from sqlalchemy.orm import sessionmaker
from modelos import Pedido

cliente = TestClient(app)

def test_criacao_pedido_sem_token_falha():
    """Garante que o sistema exige autenticação para criar pedidos."""
    payload = {"id_produto": 1, "quantidade": 1, "preco_total": 100.0}
    resposta = cliente.post("/pedidos/", json=payload)
    assert resposta.status_code == 401 # Unauthorized

def test_saude_pedidos():
    """Verifica se o serviço está online."""
    resposta = cliente.get("/")
    assert resposta.status_code == 200
    assert "Serviço de Pedidos" in resposta.json()["status"]
