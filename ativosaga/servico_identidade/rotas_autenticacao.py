# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from banco_de_dados import obter_banco
from modelos import Usuario
from esquemas import UsuarioCriar, UsuarioResposta, TokenAcesso, UsuarioLogin
from seguranca import gerar_hash_senha, verificar_senha, criar_token_acesso
from dependencias import verificar_token_acesso

# Roteador centraliza todas as rotas focadas em autenticação
roteador = APIRouter()

@roteador.post("/registro", response_model=UsuarioResposta)
def registrar_usuario(usuario_entrada: UsuarioCriar, banco: Session = Depends(obter_banco)):
    """
    Cria um novo usuário na base de dados caso o e-mail seja inédito.

    Args:
        usuario_entrada (UsuarioCriar): O payload enviado pelo cliente já validado.
        banco (Session): Sessão ativa com o banco.

    Returns:
        Usuario: Entidade do usuário criada (filtrada pelo UsuarioResposta).
    """
    # Buscamos se o usuário já existe para evitar e-mails duplicados
    usuario_existente = banco.query(Usuario).filter(Usuario.email == usuario_entrada.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Este e-mail já está em uso.")

    # Convertendo a senha antes de salvar
    senha_criptografada = gerar_hash_senha(usuario_entrada.senha)
    novo_usuario = Usuario(
        nome=usuario_entrada.nome,
        email=usuario_entrada.email, 
        senha_hash=senha_criptografada
    )
    
    banco.add(novo_usuario)
    banco.commit()
    banco.refresh(novo_usuario)
    
    return novo_usuario

@roteador.post("/login", response_model=TokenAcesso)
def realizar_login(usuario_entrada: UsuarioLogin, banco: Session = Depends(obter_banco)):
    """
    Confirma as credenciais do usuário e retorna um Token JWT válido.

    Args:
        usuario_entrada (UsuarioLogin): E-mail e senha enviados pelo cliente.
        banco (Session): Sessão ativa com o banco.

    Returns:
        TokenAcesso: Dicionário contendo o token_acesso e tipo_token.
    """
    usuario = banco.query(Usuario).filter(Usuario.email == usuario_entrada.email).first()
    
    # Falhamos se não existir o e-mail ou se a senha estiver incorreta
    if not usuario or not verificar_senha(usuario_entrada.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos."
        )

    # Injetamos o id e o nome no JWT para o frontend usar
    dados_payload = {
        "id_usuario": usuario.id,
        "nome": usuario.nome
    }
    token_gerado = criar_token_acesso(dados_payload)

    return {"token_acesso": token_gerado, "tipo_token": "bearer"}

@roteador.get("/perfil", response_model=UsuarioResposta)
def obter_perfil(
    dados_token: dict = Depends(verificar_token_acesso),
    banco: Session = Depends(obter_banco)
):
    """
    Rota protegida de exemplo. Só pode ser acessada se o usuário enviar um Token JWT válido.

    Args:
        dados_token (dict): O payload extraído do JWT pelo nosso Middleware de Segurança.
        banco (Session): Sessão ativa com o banco de dados.

    Returns:
        Usuario: Os dados do usuário logado.
    """
    # Usamos o id que o Middleware tirou de dentro do Token JWT para buscar o usuário
    id_usuario = dados_token.get("id_usuario")
    usuario = banco.query(Usuario).filter(Usuario.id == id_usuario).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    return usuario
