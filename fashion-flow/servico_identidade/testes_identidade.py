from fastapi.testclient import TestClient
from main import app
from banco_de_dados import Base, motor_do_banco

# Criamos as tabelas no banco de teste antes de rodar
Base.metadata.create_all(bind=motor_do_banco)

cliente = TestClient(app)

def teste_registro_usuario_sucesso():
    """
    Testa se um novo usuário consegue se registrar corretamente.
    """
    payload = {
        "nome": "Usuário de Teste",
        "email": "teste_tdd@exemplo.com",
        "senha": "senha_segura_123"
    }
    resposta = cliente.post("/registro", json=payload)
    
    assert resposta.status_code == 200
    assert resposta.json()["email"] == "teste_tdd@exemplo.com"
    assert "id" in resposta.json()

def teste_login_usuario_sucesso():
    """
    Testa se o login retorna um token JWT válido.
    """
    payload = {
        "email": "teste_tdd@exemplo.com",
        "senha": "senha_segura_123"
    }
    resposta = cliente.post("/login", json=payload)
    
    assert resposta.status_code == 200
    assert "token_acesso" in resposta.json()
    assert resposta.json()["tipo_token"] == "bearer"

def teste_registro_email_duplicado():
    """
    Garante que o sistema bloqueia e-mails repetidos.
    """
    payload = {
        "nome": "Outro Nome",
        "email": "teste_tdd@exemplo.com", # Já registrado no teste anterior
        "senha": "outra_senha"
    }
    resposta = cliente.post("/registro", json=payload)
    
    assert resposta.status_code == 400
    assert "já está em uso" in resposta.json()["detail"]
