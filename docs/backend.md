# ⚙️ PRD 02: Especificação Técnica do Backend

Este documento detalha a engenharia por trás do **FashionFlow**. O foco aqui é garantir que os 6 microserviços operem de forma independente, mas perfeitamente sincronizada, utilizando o que há de mais moderno em desenvolvimento assíncrono com Python.

---

## 1. Stack Tecnológica Base
Para manter a uniformidade e facilitar a manutenção, todos os microserviços seguirão este padrão:

*   **Linguagem:** Python 3.11+
*   **Framework:** FastAPI (pela alta performance e suporte nativo a `async/await`).
*   **Servidor ASGI:** Uvicorn.
*   **Banco de Dados:** PostgreSQL (Interface assíncrona com SQLAlchemy 2.0 e Alembic para migrations).
*   **Mensageria:** RabbitMQ (Protocolo AMQP via biblioteca `aio-pika`).
*   **Validação de Dados:** Pydantic v2.
*   **Segurança:** PyJWT (para tokens de acesso) e Passlib (para criptografia de senhas).

---

## 2. Arquitetura de Comunicação (The Saga Pattern)
Como lidamos com múltiplos bancos de dados, usaremos o padrão **Saga por Coreografia**. Não existe um "maestro" central; cada serviço sabe o que fazer quando ouve um evento específico no RabbitMQ.

### Fluxo de Eventos (Tabela de Mensageria)

| Evento | Origem | Destino(s) | Ação Realizada |
| :--- | :--- | :--- | :--- |
| `pedido.criado` | Servico Pedidos | Servico Estoque | Reserva o item no estoque. |
| `estoque.reservado` | Servico Estoque | Servico Pagamentos | Gera a sessão/link do Stripe. |
| `pagamento.sucesso` | Servico Pagamentos | Servico Ativos & Servico Pedidos | Libera a imagem e completa o pedido. |
| `pagamento.falhou` | Servico Pagamentos | Servico Estoque | Cancela a reserva e devolve o item ao estoque. |

---

## 3. Detalhamento dos Microserviços

### 3.1 Servico Identidade (O Core de Segurança)
*   **Responsabilidade:** Autenticação e Autorização.
*   **Database Schema:** Tabela `usuarios` (`id`, `email`, `senha_hash`, `esta_ativo`).
*   **Lógica JWT:** Emite um token contendo `id_usuario` e `expiracao`. Os outros serviços apenas validam a assinatura do token usando a `SECRET_KEY`.

### 3.2 Servico Pedidos (Gestão de Estado)
*   **Responsabilidade:** Criar pedidos e gerenciar a "Máquina de Estados".
*   **Database Schema:** Tabela `pedidos` (`id`, `id_usuario`, `total`, `estado`).
*   **Estados:** `PENDENTE` ➔ `AGUARDANDO_PAGAMENTO` ➔ `PAGO` ➔ `CONCLUIDO` (ou `CANCELADO`).

### 3.3 Servico Estoque (Lógica de Estoque)
*   **Responsabilidade:** Evitar que dois usuários comprem a última unidade ao mesmo tempo.
*   **Mecanismo:** Ao receber `pedido.criado`, ele move a quantidade de `disponivel` para `reservado`. Só dá baixa definitiva (decremento) após o `pagamento.sucesso`.

### 3.4 Servico Pagamentos (Integração Stripe)
*   **Responsabilidade:** Criar o Payment Intent no Stripe e ouvir Webhooks.
*   **Segurança:** Deve validar a assinatura do Webhook do Stripe para evitar ataques de falso pagamento.

### 3.5 Servico Ativos (Entrega do Produto)
*   **Responsabilidade:** Gerenciar o que o usuário "possui".
*   **Database Schema:** Tabela `ativos_usuario` (`id`, `id_usuario`, `sku_produto`, `desbloqueado_em`).
*   **Entrega:** Ao ouvir `pagamento.sucesso`, ele cria o registro que libera a visualização da imagem no Frontend.

---

## 4. Estratégia de Resiliência e Erros
Para garantir o nível profissional exigido:

*   **Filas de Mensagens Mortas (DLQ):** Se uma mensagem falhar 3 vezes (ex: banco de dados fora do ar), ela vai para uma fila especial para análise, evitando a perda de dados.
*   **Idempotência:** Cada evento terá um `id_correlacao`. Se o Servico Ativos receber duas vezes a confirmação do mesmo pagamento, ele processará apenas a primeira.
*   **Graceful Shutdown:** Os serviços esperarão as tarefas assíncronas terminarem antes de desligar os containers.

---

## 5. Observabilidade (Datadog)
Cada microserviço será injetado com o agente do Datadog (`ddtrace`) para monitorar:

*   **Traces:** Ver o caminho de uma requisição que começa no Servico Identidade e termina no Servico Ativos.
*   **Logs:** Centralizados e tagueados por `nome_servico` e `ambiente`.
*   **Métricas:** Tempo de resposta das rotas e latência das filas do RabbitMQ.