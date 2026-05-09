import pika
import json

usuario = 'convidado'
senha = 'convidado'
host = 'localhost' # Rodando de fora do docker apontando para a porta 5672 exposta

credenciais = pika.PlainCredentials(usuario, senha)
parametros = pika.ConnectionParameters(host=host, port=5672, credentials=credenciais)
conexao = pika.BlockingConnection(parametros)
canal = conexao.channel()

dados = {
    "id_pedido": 999,
    "id_usuario": 1,
    "id_produto": 501
}

canal.basic_publish(
    exchange='pagamento_ex',
    routing_key='',
    body=json.dumps(dados)
)

print(" [OK] Mensagem de teste enviada!")
conexao.close()
