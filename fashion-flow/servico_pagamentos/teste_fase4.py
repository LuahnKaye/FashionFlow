"""
Teste de Integracao - Fase 4: Pagamento -> Ativos

Simula o fluxo completo SEM precisar do Stripe real:
1. Registra uma transacao no banco de pagamentos
2. Publica 'pagamento.sucesso' no RabbitMQ
3. O consumidor de ativos processa e libera o produto
4. Verificamos no banco de ativos se o produto foi liberado
"""
import pika
import json
import time
import sys

# Adicionamos o caminho dos outros servicos para importar seus modulos
sys.path.insert(0, '../servico_pagamentos')
sys.path.insert(0, '../servico_ativos')

def testar_fluxo_pagamento_ativos():
    print("\n--- Teste de Integracao: Fase 4 (Pagamentos -> Ativos) ---\n")

    # ============================================================
    # PASSO 1: Registrar transacao no banco de pagamentos
    # ============================================================
    print("1. Registrando transacao no banco de pagamentos...")
    
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Banco de pagamentos
    motor_pagamentos = create_engine("postgresql://postgres:senha_postgres@localhost:5432/bd_pagamentos")
    SessaoPagamentos = sessionmaker(bind=motor_pagamentos)
    
    # Importamos o modelo e criamos a tabela
    from sqlalchemy import Column, Integer, String, Float, DateTime
    from sqlalchemy.orm import declarative_base
    from datetime import datetime
    
    BasePagamentos = declarative_base()
    
    class TransacaoTeste(BasePagamentos):
        __tablename__ = "transacoes"
        id = Column(Integer, primary_key=True)
        id_pedido = Column(Integer, nullable=False)
        id_usuario = Column(Integer, nullable=False)
        valor = Column(Float, nullable=False)
        id_sessao_stripe = Column(String, unique=True)
        status = Column(String, default="CRIADO")
        data_criacao = Column(DateTime, default=datetime.utcnow)
        data_atualizacao = Column(DateTime, default=datetime.utcnow)
    
    BasePagamentos.metadata.create_all(bind=motor_pagamentos)
    
    banco_pag = SessaoPagamentos()
    nova_transacao = TransacaoTeste(
        id_pedido=3,
        id_usuario=99,
        valor=299.90,
        id_sessao_stripe="cs_test_simulado_12345",
        status="PAGO"
    )
    banco_pag.add(nova_transacao)
    banco_pag.commit()
    print(f"   OK: Transacao #{nova_transacao.id} registrada como PAGO.")
    banco_pag.close()

    # ============================================================
    # PASSO 2: Garantir que a tabela do servico de ativos existe
    # ============================================================
    print("2. Preparando banco de ativos...")
    
    motor_ativos = create_engine("postgresql://postgres:senha_postgres@localhost:5432/bd_ativos")
    SessaoAtivos = sessionmaker(bind=motor_ativos)
    
    BaseAtivos = declarative_base()
    
    class BibliotecaTeste(BaseAtivos):
        __tablename__ = "biblioteca_usuario"
        id = Column(Integer, primary_key=True)
        id_usuario = Column(Integer, nullable=False)
        id_pedido = Column(Integer, nullable=False)
        id_produto = Column(Integer, nullable=False)
        url_imagem = Column(String)
        status = Column(String, default="LIBERADO")
        data_liberacao = Column(DateTime, default=datetime.utcnow)
    
    BaseAtivos.metadata.create_all(bind=motor_ativos)
    print("   OK: Tabela biblioteca_usuario pronta.")

    # ============================================================
    # PASSO 3: Publicar mensagem 'pagamento.sucesso' no RabbitMQ
    # ============================================================
    print("3. Publicando mensagem 'pagamento.sucesso' no RabbitMQ...")
    
    credenciais = pika.PlainCredentials('convidado', 'convidado')
    parametros = pika.ConnectionParameters(host='localhost', credentials=credenciais)
    conexao = pika.BlockingConnection(parametros)
    canal = conexao.channel()
    
    canal.queue_declare(queue='pagamento.sucesso', durable=True)
    
    payload = {
        "id_pedido": 3,
        "id_usuario": 99,
        "id_sessao_stripe": "cs_test_simulado_12345",
        "valor": 299.90
    }
    
    canal.basic_publish(
        exchange='',
        routing_key='pagamento.sucesso',
        body=json.dumps(payload),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    conexao.close()
    print("   OK: Mensagem publicada com sucesso!")

    # ============================================================
    # PASSO 4: Aguardar o consumidor processar
    # ============================================================
    print("4. Aguardando o consumidor de ativos processar (3 segundos)...")
    time.sleep(3)

    # ============================================================
    # PASSO 5: Verificar se o ativo foi liberado no banco
    # ============================================================
    print("5. Verificando banco de ativos...")
    
    banco_ativos = SessaoAtivos()
    ativo = banco_ativos.query(BibliotecaTeste).filter(
        BibliotecaTeste.id_pedido == 3,
        BibliotecaTeste.id_usuario == 99
    ).first()
    
    if ativo:
        print(f"   OK: Ativo encontrado na biblioteca do usuario!")
        print(f"   -> ID: {ativo.id}")
        print(f"   -> Produto: {ativo.id_produto}")
        print(f"   -> Status: {ativo.status}")
        print(f"   -> URL Imagem: {ativo.url_imagem}")
    else:
        print("   AVISO: Ativo NAO encontrado. Verifique se o consumidor esta rodando.")
    
    banco_ativos.close()
    print("\n--- Teste Concluido ---\n")

if __name__ == "__main__":
    testar_fluxo_pagamento_ativos()
