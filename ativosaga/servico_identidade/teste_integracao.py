from fastapi.testclient import TestClient
from main import app
import random
import string

def gerar_email_aleatorio():
    """
    Gera um e-mail aleatório para evitar erros de 'e-mail já cadastrado' nos testes repetidos.
    """
    sufixo = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    return f"usuario_{sufixo}@teste.com"

def testar_fluxo_completo():
    """
    Executa um fluxo completo de teste: Registro -> Login -> Perfil Protegido.
    """
    # Usar o TestClient dentro de um 'with' garante que os eventos de startup/shutdown rodem
    # e evita problemas de compatibilidade com versões específicas do httpx.
    with TestClient(app) as cliente:
        print("\n--- Iniciando Testes de Integracao - Servico de Identidade ---\n")
        
        email_teste = gerar_email_aleatorio()
        senha_teste = "SenhaSegura123"

        # --- PASSO 1: Registro de Usuario ---
        print(f"1. Testando Registro com e-mail: {email_teste}...")
        resposta_registro = cliente.post("/registro", json={"email": email_teste, "senha": senha_teste})
        
        if resposta_registro.status_code == 200:
            print("OK: Registro concluido com sucesso!")
        else:
            print(f"ERRO no Registro: {resposta_registro.json()}")
            return

        # --- PASSO 2: Login ---
        print("2. Testando Login para obter Token JWT...")
        resposta_login = cliente.post("/login", json={"email": email_teste, "senha": senha_teste})
        
        if resposta_login.status_code == 200:
            token = resposta_login.json().get("token_acesso")
            print(f"OK: Login bem-sucedido! Token gerado (resumo): {token[:30]}...")
        else:
            print(f"ERRO no Login: {resposta_login.json()}")
            return

        # --- PASSO 3: Acesso ao Perfil (Rota Protegida) ---
        print("3. Testando Acesso ao Perfil Protegido...")
        # Enviamos o Token no Header de Autorização como Bearer
        cabecalhos = {"Authorization": f"Bearer {token}"}
        resposta_perfil = cliente.get("/perfil", headers=cabecalhos)
        
        if resposta_perfil.status_code == 200:
            dados = resposta_perfil.json()
            print(f"OK: Perfil acessado com sucesso! ID do Usuario: {dados.get('id')}")
            print(f"Email retornado: {dados.get('email')}")
        else:
            print(f"ERRO ao acessar Perfil: {resposta_perfil.json()}")

if __name__ == "__main__":
    testar_fluxo_completo()
