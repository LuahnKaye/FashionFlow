import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

# Chave deve ser identica aos outros servicos
CHAVE_SECRETA = "minha_chave_ultra_secreta_aqui_para_assinatura"
ALGORITMO = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verificar_token_acesso(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Protege o endpoint garantindo que apenas usuarios logados e validos 
    possam criar sessoes de pagamento.
    """
    try:
        payload = jwt.decode(token, CHAVE_SECRETA, algorithms=[ALGORITMO])
        id_usuario: int = payload.get("id_usuario")
        
        if id_usuario is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalido: ID do usuario ausente."
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
            detail="Nao foi possivel validar as credenciais."
        )
