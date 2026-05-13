# 🚀 Guia de Execução: Projeto AtivoSAGA

Este roteiro segue a lógica de **"Infraestrutura Primeiro, Código Depois"**. Primeiro garantimos que os alicerces estão sólidos para depois levantarmos as paredes (o código).

---

## ✅ Fase 1: Fundação e Ambiente — CONCLUÍDA
O objetivo aqui é ter o ecossistema pronto para receber seus microserviços.

*   ✅ **Estrutura de Pastas:** Raiz `fashion-flow/` e subpastas criadas.
*   ✅ **Orquestração (Docker):** `docker-compose.yml` com PostgreSQL e RabbitMQ.
*   ✅ **Scripts de Banco:** `init-dbs.sql` criando todos os bancos (`bd_pedidos`, `bd_identidade`, `bd_estoque`, `bd_pagamentos`, `bd_ativos`, `bd_notificacoes`).
*   ✅ **Teste de Conexão:** RabbitMQ e PostgreSQL acessíveis.

---

## ✅ Fase 2: O Pilar de Segurança (Servico Identidade) — CONCLUÍDA
Sem identidade, não há transação. Este é seu primeiro microserviço.

*   ✅ **Boilerplate:** FastAPI + SQLAlchemy + Pydantic configurados.
*   ✅ **Autenticação:**
    *   `POST /registro` com hash de senha via Passlib/bcrypt.
    *   `POST /login` gerando Token JWT.
*   ✅ **Middleware de Validação:** Lógica de validação JWT replicada nos outros serviços.
*   ✅ **Teste de Integração:** Fluxo Registro → Login → Perfil Protegido validado.

---

## ✅ Fase 3: O Fluxo Transacional (Servico Pedidos & Servico Estoque) — CONCLUÍDA
Aqui é onde o "coração" do e-commerce começa a bater.

*   ✅ **Servico Pedidos:** Rota de criação de pedido com status `PENDENTE`.
*   ✅ **Integração RabbitMQ:** Mensagem `pedido.criado` publicada na fila após salvar.
*   ✅ **Servico Estoque:** Consumidor que diminui `quantidade_disponivel` e aumenta `quantidade_reservada`.
*   ✅ **Teste de Integração:** Pedido criado → Mensagem enviada → Estoque reservado automaticamente (10 → 8 disponíveis, 0 → 2 reservados).

---

## ✅ Fase 4: Dinheiro e Entrega (Servico Pagamentos & Servico Ativos) — CONCLUÍDA
O momento de transformar o pagamento em posse digital.

*   ✅ **Servico Pagamentos (Stripe):** Rota de criação de Sessão de Checkout implementada.
*   ✅ **Webhook:** Rota `/webhook-stripe` que recebe confirmação e publica `pagamento.sucesso`.
*   ✅ **Servico Ativos:** Consumidor que ouve `pagamento.sucesso` e cria registro na `biblioteca_usuario`.
*   ✅ **Teste de Integração:** Transação registrada → Mensagem publicada → Ativo liberado na biblioteca do usuário.
*   ⚠️ **Pendente:** Configurar chaves reais do Stripe (atualmente usando simulação).

---

## 📅 Fase 5: A Experiência do Usuário (Frontend)
Hora de dar vida ao projeto com React.

*   **Setup Inicial:** Inicie o Vite + React + Tailwind.
*   **Contexto de Autenticacao:** Crie o provedor de autenticação que guarda o Token JWT.
*   **Vitrine e Carrinho:** Desenvolva a listagem de produtos e a lógica de persistência no `localStorage`.
*   **Integração Stripe:** Implemente o componente de pagamento e a tela de "Aguardando Confirmação".
*   **A Galeria:** Desenvolva a página que consome do Servico Ativos para exibir as imagens compradas.

---

## 📅 Fase 6: Observabilidade e Polimento (Finalização)
O que separa o amador do profissional sênior.

*   **Datadog Tracing:** Injete o `ddtrace` nos seus microserviços para visualizar os gráficos de latência.
*   **Tratamento de Erros:** Implemente as Filas de Mensagens Mortas (DLQ) no RabbitMQ para mensagens que falham.
*   **Documentação (README):** Escreva um README impecável explicando como subir o projeto e qual arquitetura foi utilizada.
