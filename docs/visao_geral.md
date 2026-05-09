# 📑 PRD 01: Documento de Visão Geral (FashionFlow)

**Projeto:** FashionFlow – Ecossistema de E-commerce para Ativos Digitais  
**Responsável:** Luahn Kayê  
**Status:** Em Definição

---

## 1. Introdução e Contexto
O **FashionFlow** não é apenas uma loja virtual; é um laboratório de engenharia para sistemas de alta criticidade. O projeto simula a venda de peças de vestuário onde o "produto entregue" é o acesso vitalício à imagem/arte digital da peça (Ativo Digital).

O sistema deve ser capaz de processar compras de forma assíncrona, garantindo que o usuário receba seu produto mesmo em cenários de instabilidade de rede ou falha em serviços secundários.

---

## 2. Objetivos do Produto
*   **Segurança Robusta:** Implementar autenticação via JWT para garantir que apenas donos legítimos acessem seus ativos.
*   **Experiência Assíncrona:** O usuário recebe feedback imediato, enquanto o processamento pesado (estoque, pagamento e liberação) ocorre em background.
*   **Escalabilidade e Resiliência:** Utilizar arquitetura orientada a eventos para desacoplar os serviços.
*   **Monitoramento Profissional:** Visibilidade total da saúde do sistema através do Datadog.

---

## 3. A Jornada do Usuário (Jornada do Usuario)
Para entender o sistema, dividimos a experiência em 4 fases críticas:

| Fase | Ação do Usuário | O que acontece no sistema? |
| :--- | :--- | :--- |
| **1. Descoberta** | Navega pela vitrine (Público). | O Front consome a lista de produtos (Mock ou BD). |
| **2. Intenção** | Clica em "Comprar" ou "Carrinho". | **Bloqueio:** O sistema exige Login/Cadastro. |
| **3. Transação** | Realiza o pagamento via Stripe. | O pedido entra em estado "Pendente". A saga de eventos começa no RabbitMQ. |
| **4. Posse** | Acessa a aba "Minhas Compras". | O sistema libera a imagem para visualização após confirmação do evento de pagamento. |

---

## 4. Definição dos Microserviços (O Ecossistema)
O sistema será composto por 6 motores independentes:

1.  **Servico Identidade:** O "porteiro". Gerencia usuários e emite passaportes (Tokens JWT).
2.  **Servico Pedidos:** O "cérebro". Coordena a criação e o status dos pedidos.
3.  **Servico Estoque:** O "guarda-estoque". Reserva as peças e evita o overbooking.
4.  **Servico Pagamentos:** O "caixa". Faz a ponte com o Stripe e processa Webhooks.
5.  **Servico Ativos:** O "cofre". Libera as imagens na galeria do usuário logado.
6.  **Servico Notificacao:** O "mensageiro". Avisa o usuário sobre o sucesso da operação.

---

## 5. Regras de Negócio Críticas
*   **RN01 (Compra Autenticada):** Nenhuma ordem pode ser criada sem um `id_usuario` válido vindo de um Token JWT.
*   **RN02 (Reserva Obrigatória):** Um pagamento só pode ser solicitado se o estoque confirmar a reserva do item.
*   **RN03 (Garantia de Entrega):** Se o pagamento foi aprovado pelo Stripe, o Servico Ativos deve liberar a imagem, mesmo que o serviço de notificação esteja fora do ar.
*   **RN04 (Idempotência):** Se o RabbitMQ enviar a mesma mensagem de pagamento aprovado duas vezes, o sistema deve ignorar a segunda para evitar duplicidade na galeria.

---

## 6. Requisitos Técnicos de Alto Nível
*   **Backend:** Python 3.11+ com FastAPI (Assíncrono).
*   **Frontend:** React com Tailwind CSS e gerenciamento de estado global.
*   **Comunicação:** RabbitMQ (Protocolo AMQP).
*   **Persistência:** PostgreSQL (Bancos isolados por serviço).
*   **Observabilidade:** Datadog (Tracing, Logs e Métricas).