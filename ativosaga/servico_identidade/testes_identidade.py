from fastapi.testclient import TestClient
from main import app
from banco_de_dados import motor_do_banco
from sqlalchemy.orm import sessionmaker
from modelos import Usuario

cliente = TestClient(app)

EMAIL_TESTE = "teste_final@exemplo.com"
SENHA_TESTE = "senha_segura_123"

def setup_module(module):
    """Limpa o ambiente antes de começar a suíte de testes."""
    SessionLocal = sessionmaker(bind=motor_do_banco)
    db = SessionLocal()
    try:
        usuario = db.query(Usuario).filter(Usuario.email == EMAIL_TESTE).first()
        if usuario:
            db.delete(usuario)
            db.commit()
    finally:
        db.close()

def test_1_registro_sucesso():
    payload = {
        "nome": "Usuário Teste",
        "email": EMAIL_TESTE,
        "senha": SENHA_TESTE
    }
    resposta = cliente.post("/registro", json=payload)
    assert resposta.status_code == 200

def test_2_login_sucesso():
    payload = {
        "email": EMAIL_TESTE,
        "senha": SENHA_TESTE
    }
    resposta = cliente.post("/login", json=payload)
    assert resposta.status_code == 200
    assert "token_acesso" in resposta.json()

def test_3_registro_duplicado_falha():
    payload = {
        "nome": "Outro",
        "email": EMAIL_TESTE,
        "senha": "outra"
    }
    resposta = cliente.post("/registro", json=payload)
    assert resposta.status_code == 400
    assert "já está em uso" in resposta.json()["detail"]
