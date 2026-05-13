# 👗 FashionFlow - Ecossistema de Microsserviços E-commerce (EDA)

Bem-vindo ao **FashionFlow**, uma plataforma de e-commerce de ativos digitais construída sob os princípios de **EDA (Event-Driven Architecture)** e Microsserviços. Este projeto demonstra competência técnica em sistemas distribuídos de alta criticidade, onde resiliência e desacoplamento são prioridades.

---

## 🌟 Diferenciais Técnicos (Nível Enterprise)

1.  **Arquitetura EDA & Saga Pattern**: Orquestração assíncrona entre serviços via RabbitMQ (Coreografia), garantindo que falhas parciais não interrompam a jornada do usuário.
2.  **Cloud-Native (AWS Ready)**: Desenhado para ser escalável na AWS, utilizando **ECS Fargate** (Compute), **RDS PostgreSQL** (Dados) e **Amazon S3** (Storage de Ativos).
3.  **Observabilidade com Datadog**: Implementação de **Distributed Tracing** (Rastreamento Distribuído) para monitorar o fluxo de mensagens e identificar gargalos de performance entre serviços.
4.  **Segurança e Idempotência**: Proteção contra **ReDoS**, validação rigorosa de JWT e lógica de idempotência em pagamentos e entregas de ativos para prevenir duplicidade.
5.  **Qualidade de Código (SOLID & Clean Architecture)**:
    *   **SRP (Responsabilidade Única)**: Cada serviço foca em um domínio de negócio específico.
    *   **Repository Pattern**: Separação clara entre lógica de negócio e persistência de dados.
    *   **Clean Code (PT-BR)**: Convenção de nomenclatura em Português Brasileiro para máxima clareza de intenção e redução de carga cognitiva da equipe.

---

## 🏗️ Estrutura do Ecossistema

*   **Identidade (Auth)**: JWT, segurança e gestão de usuários.
*   **Pedidos (Order)**: Orquestrador do fluxo de compra.
*   **Pagamentos (Payment)**: Gateway Stripe com Webhooks idempotentes.
*   **Estoque (Inventory)**: Reserva e compensação automática de SKUs.
*   **Ativos (Asset)**: Galeria digital segura e entrega de produtos.
*   **Notificações**: Comunicação assíncrona e reativa.

---

## 🚀 Como Executar o Projeto

### 1. Pré-requisitos
*   [Docker](https://www.docker.com/) e Docker Compose.
*   [Stripe CLI](https://stripe.com/docs/stripe-cli) (opcional para testes locais de webhook).

### 2. Inicialização Rápida
```bash
docker-compose up -d --build
```
*Isso subirá toda a infraestrutura (Postgres, RabbitMQ) e os 6 microsserviços automaticamente.*

---

## 🔍 Qualidade e CI/CD

O projeto conta com um pipeline robusto de **CI/CD via GitHub Actions**:
*   **Linting**: Validação estática com Ruff.
*   **Testes de Integração**: Executados em um container real de **PostgreSQL 15**, garantindo fidelidade total ao ambiente de produção.

### Rodar Testes Localmente:
```bash
# Testes de Identidade
docker exec fashionflow_identidade pytest testes_identidade.py

# Testes de Pedidos
docker exec fashionflow_pedidos pytest testes_pedidos.py
```

---

## 🛠️ Stack Tecnológica
*   **Backend**: Python, FastAPI, SQLAlchemy, Pika.
*   **Observabilidade**: Datadog (Distributed Tracing).
*   **Infra**: Docker, RabbitMQ, PostgreSQL.
*   **Frontend**: React, Tailwind CSS, Framer Motion.

---
*Este projeto foi construído para demonstrar excelência em padrões de projeto, resiliência de sistemas distribuídos e cultura DevOps.*
