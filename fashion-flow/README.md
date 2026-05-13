# 👗 FashionFlow - Ecossistema de Microsserviços E-commerce (EDA)

Bem-vindo ao **FashionFlow**, uma plataforma de e-commerce de alta costura digital construída sob os princípios de **EDA (Event-Driven Architecture)** e Microsserviços. Este projeto demonstra competência técnica em sistemas distribuídos de alta criticidade, onde resiliência e desacoplamento são prioridades.

---

## 🌟 Diferenciais Técnicos (Nível Enterprise)

1.  **Arquitetura EDA & Saga Pattern**: Orquestração assíncrona entre serviços via RabbitMQ (Coreografia), garantindo que falhas parciais não interrompam a jornada do usuário.
2.  **Cloud-Native (AWS Ready)**: Desenhado para ser escalável na AWS, utilizando **ECS Fargate** (Compute), **RDS PostgreSQL** (Dados) e **Amazon S3** (Storage de Ativos).
3.  **Observabilidade com Datadog**: Implementação de **Distributed Tracing** (Rastreamento Distribuído) para monitorar o fluxo de mensagens e identificar gargalos de performance.
4.  **Segurança e Idempotência**: Proteção contra **ReDoS**, validação rigorosa de JWT e lógica de idempotência em pagamentos para prevenir duplicidade.
5.  **Qualidade de Software**:
    *   **SOLID & Clean Architecture**: Uso de Repository Pattern e Princípio de Responsabilidade Única (SRP).
    *   **Clean Code (PT-BR)**: Nomenclatura em Português Brasileiro para máxima clareza de intenção.

---

## 🏗️ Estrutura do Ecossistema

O sistema é composto por 6 motores independentes que se comunicam via RabbitMQ:

*   **Identidade (Porta 8000)**: Gerencia usuários e autenticação via JWT.
*   **Pedidos (Porta 8001)**: Orquestrador do ciclo de vida da compra.
*   **Pagamentos (Porta 8002)**: Integração com Stripe e processamento de Webhooks idempotentes.
*   **Ativos (Porta 8003)**: O "Cofre" digital. Consome mensagens para liberar produtos na galeria.
*   **Estoque**: Gerencia reserva e baixa automática de produtos (Saga Pattern).
*   **Notificações**: Serviço reativo para comunicação assíncrona com o cliente.

---

## 🚀 Como Executar o Projeto

### 1. Pré-requisitos
*   [Docker](https://www.docker.com/) e Docker Compose instalados.
*   [Stripe CLI](https://stripe.com/docs/stripe-cli) (para simular pagamentos reais).

### 2. Subindo a Infraestrutura
Na raiz do projeto, execute:
```bash
docker-compose up -d --build
```
*Isso subirá o PostgreSQL, RabbitMQ e todos os 6 Microsserviços.*

### 3. Configurando o Fluxo de Pagamento (Stripe)
1.  Faça login no Stripe: `stripe login`
2.  Inicie o redirecionamento de webhooks:
    ```bash
    stripe listen --forward-to localhost:8002/webhook
    ```
3.  O sistema processará o evento `checkout.session.completed` de forma segura e automática.

---

## 🔍 Guia de Validação e Testes

### 1. Testes Automatizados no Container
O projeto conta com CI/CD (GitHub Actions) rodando em PostgreSQL real, mas você pode validar localmente:
```bash
# Testes de Identidade
docker exec fashionflow_identidade pytest testes_identidade.py

# Testes de Pedidos
docker exec fashionflow_pedidos pytest testes_pedidos.py
```

### 2. Painel de Controle e Mensageria
*   **RabbitMQ Dashboard**: [http://localhost:15672](http://localhost:15672) (user: `convidado` / pass: `convidado`).
*   **Documentação Swagger (APIs)**:
    *   [Identidade (Auth)](http://localhost:8000/docs)
    *   [Pedidos](http://localhost:8001/docs)
    *   [Pagamentos](http://localhost:8002/docs)

### 3. Validação do Saga Pattern (Resiliência)
1. Crie um pedido via Swagger no Serviço de Pedidos.
2. Verifique no banco que o estoque foi reservado.
3. Simule o sucesso do pagamento via rota de teste:
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:8002/teste-sucesso?id_pedido=ID&id_usuario=ID&id_produto=ID" -Method Post
   ```

---

## 🛠️ Stack Tecnológica
*   **Backend**: Python (FastAPI), SQLAlchemy, Pika.
*   **Frontend**: React, Tailwind CSS, Framer Motion.
*   **Infra**: Docker, RabbitMQ, PostgreSQL, Datadog (Tracing).

---
*Este projeto demonstra excelência em padrões de projeto, resiliência de sistemas distribuídos e cultura DevOps.*
