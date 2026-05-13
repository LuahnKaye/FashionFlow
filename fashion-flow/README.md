# 👗 FashionFlow - Ecossistema de Microsserviços E-commerce

Bem-vindo ao **FashionFlow**, uma plataforma de e-commerce de alta costura digital construída sob os princípios de **EDA (Event-Driven Architecture)** e Microsserviços, focada em escalabilidade, resiliência e experiência do usuário premium.

Este projeto foi desenvolvido para demonstrar o domínio de tecnologias de ponta e padrões de arquitetura distribuída (Saga Pattern), sendo uma vitrine de engenharia de software para recrutadores e desenvolvedores seniores.

---

## 🌟 Diferenciais Técnicos (O que olhar primeiro)

1.  **Arquitetura EDA (Event-Driven Architecture)**: O sistema utiliza o padrão Saga (Coreografia) para gerenciar transações distribuídas entre Estoque, Pedidos e Pagamentos de forma reativa e assíncrona.
2.  **Segurança Auditada**: Proteção contra vulnerabilidades conhecidas como **ReDoS** (via atualização do FastAPI para 0.109.1) e falhas de **Idempotência** em gateways de pagamento.
3.  **CI/CD de Alta Fidelidade**: O pipeline do GitHub Actions utiliza **Service Containers com PostgreSQL 15 real**, evitando o uso de SQLite em testes e garantindo que o comportamento em teste seja idêntico ao de produção.
4.  **Resiliência com RabbitMQ**: Implementação de **DLQs (Dead Letter Queues)** e mecanismos de retry para garantir que nenhuma mensagem de pagamento ou entrega de ativo seja perdida.

---

## 🏗️ Arquitetura do Sistema (EDA)

O sistema é composto por 6 motores independentes que se comunicam através de eventos via RabbitMQ:

*   **Identidade**: Gestão de usuários e autenticação via JWT.
*   **Pedidos**: Orquestrador do ciclo de vida da compra.
*   **Pagamentos**: Integração com Stripe e processamento de Webhooks idempotentes.
*   **Ativos**: O "Cofre" digital. Consome mensagens do RabbitMQ para liberar produtos na galeria do usuário.
*   **Estoque**: Gerencia reserva e baixa automática de produtos.
*   **Notificações**: Serviço reativo para comunicação com o cliente.

---

## 🚀 Como Executar o Projeto

### 1. Pré-requisitos
*   [Docker](https://www.docker.com/) e Docker Compose instalados.
*   [Stripe CLI](https://stripe.com/docs/stripe-cli) (para simular pagamentos reais).

### 2. Subindo tudo com um comando
Na raiz do projeto, execute:
```bash
docker-compose up -d --build
```
*Isso subirá o PostgreSQL, RabbitMQ e todos os 6 Microsserviços.*

### 3. Configurando o Fluxo de Pagamento (Stripe)
Para que o sistema libere os produtos automaticamente:
1.  Faça login no Stripe: `stripe login`
2.  Inicie o redirecionamento de webhooks:
    ```bash
    stripe listen --forward-to localhost:8002/webhook
    ```
3.  O sistema processará o evento de `checkout.session.completed` de forma segura e idempotente.

---

## 🔍 Guia de Validação (Testes)

### 1. Testes Automatizados no Container
Você pode validar a integridade de cada serviço rodando os testes dentro do Docker:
```bash
# Testes de Identidade
docker exec fashionflow_identidade pytest testes_identidade.py

# Testes de Pedidos
docker exec fashionflow_pedidos pytest testes_pedidos.py
```

### 2. Painel de Controle (RabbitMQ)
Acesse [http://localhost:15672](http://localhost:15672) (user: `convidado` / pass: `convidado`) para visualizar a topologia das filas e trocas (exchanges).

### 3. Documentação Interativa (Swagger)
Cada microserviço expõe sua própria API Documentada:
*   [Identidade (Auth)](http://localhost:8000/docs)
*   [Pedidos](http://localhost:8001/docs)
*   [Pagamentos](http://localhost:8002/docs)

---

## 🛠️ Stack Tecnológica
*   **Backend**: Python, FastAPI, SQLAlchemy.
*   **Mensageria**: RabbitMQ (Pika).
*   **Banco de Dados**: PostgreSQL.
*   **Frontend**: React, Tailwind CSS, Framer Motion.
*   **DevOps**: Docker, GitHub Actions (CI/CD).

---
*Desenvolvido com foco em padrões de código limpo, resiliência e arquitetura distribuída de nível corporativo.*
