# pyrefly: ignore [missing-import]
import jwt
# pyrefly: ignore [missing-import]
from fastapi import HTTPException, status, Depends
# pyrefly: ignore [missing-import]
from fastapi.security import OAuth2PasswordBearer

# Importante: Estas chaves devem ser iguais às do Serviço de Identidade
CHAVE_SECRETA = "minha_chave_ultra_secreta_aqui_para_assinatura"
ALGORITMO = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verificar_token_acesso(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Decodifica o Token JWT e extrai o payload (dados do usuário).
    
    Args:
        token (str): O token recebido via header Authorization.
        
    Returns:
        dict: O payload contendo o id_usuario.
    """
    try:
        payload = jwt.decode(token, CHAVE_SECRETA, algorithms=[ALGORITMO])
        id_usuario: int = payload.get("id_usuario")
        
        if id_usuario is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: ID do usuário ausente."
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="O token de acesso expirou."
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível validar as credenciais."
        )
