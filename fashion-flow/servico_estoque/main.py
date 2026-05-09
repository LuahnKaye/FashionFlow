from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from banco_de_dados import motor_do_banco, Base, obter_banco
from modelos import Estoque
from pydantic import BaseModel

# Inicializa as tabelas
Base.metadata.create_all(bind=motor_do_banco)

aplicativo_fastapi = FastAPI(title="FashionFlow - Servico de Estoque")

class ItemEstoque(BaseModel):
    id_produto: int
    quantidade: int

@aplicativo_fastapi.post("/adicionar")
def adicionar_estoque(item: ItemEstoque, banco: Session = Depends(obter_banco)):
    """
    Adiciona ou atualiza a quantidade de um produto no estoque.
    """
    existente = banco.query(Estoque).filter(Estoque.id_produto == item.id_produto).first()
    if existente:
        existente.quantidade_disponivel += item.quantidade
    else:
        novo_item = Estoque(id_produto=item.id_produto, quantidade_disponivel=item.quantidade)
        banco.add(novo_item)
    
    banco.commit()
    return {"mensagem": f"Estoque atualizado para o produto {item.id_produto}"}

@aplicativo_fastapi.get("/status/{id_produto}")
def verificar_estoque(id_produto: int, banco: Session = Depends(obter_banco)):
    item = banco.query(Estoque).filter(Estoque.id_produto == id_produto).first()
    if not item:
        raise HTTPException(status_code=404, detail="Produto nao encontrado no estoque")
    return {
        "id_produto": item.id_produto,
        "disponivel": item.quantidade_disponivel,
        "reservado": item.quantidade_reservada
    }
