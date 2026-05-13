from sqlalchemy import Column, Integer, String, Boolean
from banco_de_dados import Base

class Usuario(Base):
    """
    Representa a tabela de usuários físicos no banco de dados.
    """
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    
    nome = Column(String, nullable=True) # Campo para o nome do usuário
    
    # Adicionamos um index aqui pois faremos buscas frequentes por email no login
    email = Column(String, unique=True, index=True, nullable=False)
    
    # Salvar a senha criptografada é uma regra de ouro de segurança
    senha_hash = Column(String, nullable=False)
    
    esta_ativo = Column(Boolean, default=True)
