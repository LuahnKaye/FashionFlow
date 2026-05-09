import httpx
import jwt
from datetime import datetime, timedelta

# Configurações para gerar o Token (iguais aos serviços)
CHAVE_SECRETA = "minha_chave_ultra_secreta_aqui_para_assinatura"
ALGORITMO = "HS256"

def gerar_token_teste(id_usuario: int):
    """Gera um token JWT manual para teste sem precisar do serviço de identidade rodando."""
    payload = {
        "id_usuario": id_usuario,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, CHAVE_SECRETA, algorithm=ALGORITMO)

def testar_criacao_pedido():
    print("\n--- Teste de Criacao de Pedido (Integracao HTTP) ---\n")
    
    # 1. Geramos um token para o Usuario ID 99
    token = gerar_token_teste(99)
    print(f"Token de Teste Gerado: {token[:20]}...")

    # 2. Dados do Pedido
    dados_pedido = {
        "id_produto": 501,
        "quantidade": 2,
        "preco_total": 299.90
    }

    # 3. Fazemos a chamada para o servico na porta 8001
    url = "http://127.0.0.1:8001/pedidos/"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"Enviando pedido para {url}...")
    
    try:
        with httpx.Client() as cliente:
            resposta = cliente.post(url, json=dados_pedido, headers=headers)
            
            if resposta.status_code == 200:
                print("OK: Pedido criado com sucesso no banco de dados!")
                print(f"Dados retornados: {resposta.json()}")
            else:
                print(f"ERRO: O servico retornou status {resposta.status_code}")
                print(f"Detalhes: {resposta.json()}")
    except Exception as e:
        print(f"ERRO de Conexao: {e}")
        print("\nNota: Certifique-se de que o servico esta rodando com 'uvicorn main:aplicativo_fastapi --port 8001'")

if __name__ == "__main__":
    testar_criacao_pedido()
