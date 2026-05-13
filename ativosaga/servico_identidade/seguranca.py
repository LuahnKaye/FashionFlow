import os
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta

# Configurações do JWT lidas do ambiente
CHAVE_SECRETA = os.getenv("JWT_SECRET", "chave_padrao_desenvolvimento_nao_use_em_producao")
ALGORITMO = "HS256"
MINUTOS_EXPIRACAO_TOKEN = 1440

# Inicializa o contexto para gerar e verificar o bcrypt
contexto_criptografia = CryptContext(schemes=["bcrypt"], deprecated="auto")

def gerar_hash_senha(senha_plana: str) -> str:
    """
    Gera um hash seguro para a senha do usuário a partir da senha original.

    Args:
        senha_plana (str): A senha legível recebida pelo endpoint.

    Returns:
        str: O hash da senha que será armazenado no banco.
    """
    return contexto_criptografia.hash(senha_plana)

def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    """
    Verifica se a senha fornecida bate com o hash criptografado existente.

    Args:
        senha_plana (str): A senha fornecida durante o login.
        senha_hash (str): O hash registrado previamente no banco.

    Returns:
        bool: Retorna True se a senha confere, caso contrário False.
    """
    return contexto_criptografia.verify(senha_plana, senha_hash)

def criar_token_acesso(dados: dict) -> str:
    """
    Gera e assina um Token JWT contendo as informações (payload) do usuário.

    Args:
        dados (dict): O payload com as informações a serem armazenadas no token (ex: id_usuario).

    Returns:
        str: A string que representa o token JWT recém-criado.
    """
    copia_dados = dados.copy()
    
    # Estabelecemos uma data de expiração para o token por segurança
    data_expiracao = datetime.utcnow() + timedelta(minutes=MINUTOS_EXPIRACAO_TOKEN)
    copia_dados.update({"exp": data_expiracao})
    
    token_codificado = jwt.encode(copia_dados, CHAVE_SECRETA, algorithm=ALGORITMO)
    return token_codificado
