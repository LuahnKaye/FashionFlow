# 👗 FashionFlow - Ecossistema de Microsserviços E-commerce

Bem-vindo ao **FashionFlow**, uma plataforma de e-commerce de alta costura digital construída com uma arquitetura moderna de microsserviços, focada em escalabilidade, resiliência e experiência do usuário premium.

## 🚀 Como Executar o Projeto (Guia para Recrutadores)

Para garantir que o fluxo de pagamento e entrega de ativos funcione 100% de forma automatizada, siga estes passos:

### 1. Pré-requisitos
*   [Docker](https://www.docker.com/) e Docker Compose instalados.
*   [Stripe CLI](https://stripe.com/docs/stripe-cli) (para simular os pagamentos em ambiente de teste).

### 2. Subindo a Infraestrutura
No terminal, na raiz do projeto, execute:
```bash
docker-compose up -d --build
```
*Isso subirá o Banco de Dados (PostgreSQL), o Mensageiro (RabbitMQ) e os 6 Microsserviços.*

### 3. Configurando a Automação de Pagamentos (Stripe)
Para que o sistema libere os produtos automaticamente após a compra:
1.  Abra um novo terminal e faça login no Stripe:
    ```bash
    stripe login
    ```
2.  Inicie o redirecionamento de eventos para o seu ambiente local:
    ```bash
    stripe listen --forward-to localhost:8002/webhook
    ```
3.  **Importante**: O sistema também possui um fallback automático. Assim que você for redirecionado para a página de `/sucesso`, o frontend verificará o status e liberará o produto mesmo que o webhook demore.

---

## 🏗️ Arquitetura do Sistema

O projeto é dividido em serviços especialistas que se comunicam de forma assíncrona:

*   **Identidade (Porta 8000)**: Gerencia usuários e autenticação via JWT.
*   **Pedidos (Porta 8001)**: Orquestra a criação de ordens de compra.
*   **Pagamentos (Porta 8002)**: Integração com Stripe e publicação de eventos de sucesso.
*   **Ativos (Porta 8003)**: O "Cofre" digital. Consome mensagens do RabbitMQ para liberar downloads e gerenciar a galeria do usuário.
*   **Estoque**: Gerencia a disponibilidade de produtos e realiza a reserva/compensação automática (Saga Pattern).
*   **Notificações**: Serviço puramente reativo que ouve eventos para futuros disparos de e-mail.

## 🛠️ Tecnologias Utilizadas
*   **Backend**: Python, FastAPI, SQLAlchemy, Pika (RabbitMQ).
*   **Frontend**: React, Tailwind CSS, Framer Motion.
*   **Mensageria**: RabbitMQ (Exchange Fanout para máxima escalabilidade).
*   **Banco de Dados**: PostgreSQL.
*   **DevOps**: Docker & Docker Compose.

---

## 🔍 Guia de Validação Técnica (Para Recrutadores)

Para validar a robustez da arquitetura, siga este roteiro de testes:

### 1. Testes Automatizados (Qualidade)
Verifique a suíte de testes rodando diretamente nos containers:
```bash
# Teste de Identidade (Registro, Login, Duplicidade)
docker exec fashionflow_identidade pytest testes_identidade.py

# Teste de Pedidos (Autorização e Saúde)
docker exec fashionflow_pedidos pytest testes_pedidos.py
```

### 2. Observabilidade e Mensageria
- **RabbitMQ Dashboard**: Acesse [http://localhost:15672](http://localhost:15672) (`convidado`/`convidado`) para ver o fluxo de mensagens e as **DLQs** (Dead Letter Queues) configuradas.
- **Documentação Swagger**: Cada serviço possui sua própria documentação automática. Ex: [http://localhost:8000/docs](http://localhost:8000/docs).

### 3. Validação do Saga Pattern (Resiliência)
1. Crie um pedido via Swagger no Serviço de Pedidos.
2. Verifique no banco que o estoque foi **reservado** (`quantidade_reservada`).
3. Simule o sucesso do pagamento via rota de teste:
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:8002/teste-sucesso?id_pedido=ID&id_usuario=ID&id_produto=ID" -Method Post
   ```
4. Note a baixa definitiva no Estoque e a liberação automática no Serviço de Ativos.

---
*Desenvolvido com foco em padrões de código limpo, resiliência e arquitetura distribuída.*
