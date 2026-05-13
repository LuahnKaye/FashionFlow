# 🎨 PRD 03: Especificação do Frontend (Interface & UX)

Este documento define a camada de interação do **AtivoSAGA**. O objetivo é criar uma Single Page Application (SPA) moderna, que mascare a complexidade dos microserviços assíncronos e ofereça uma experiência de compra fluida e segura.

---

## 1. Stack Tecnológica
*   **Framework:** React (v18+) com Vite para um ambiente de desenvolvimento ultra-rápido.
*   **Linguagem:** TypeScript (para garantir segurança de tipos entre o Front e as APIs Python).
*   **Estilização:** Tailwind CSS (Design System utilitário e responsivo).
*   **Gerenciamento de Estado:**
    *   **Zustand:** Para estados globais simples (Carrinho e Autenticação).
    *   **TanStack Query (React Query):** Para sincronização de dados com o servidor e gerenciamento de cache/polling.
*   **Pagamentos:** Stripe Elements (SDK oficial para uma interface de checkout profissional).

---

## 2. Arquitetura de Navegação e Acesso
A aplicação será dividida em áreas públicas e protegidas por um **Guarda de Autenticacao** (Middleware de rota).

| Rota | Descrição | Acesso |
| :--- | :--- | :--- |
| `/` | Vitrine de produtos com cards de roupas. | Público |
| `/login` / `/cadastro` | Formulários de entrada e registro. | Público |
| `/carrinho` | Lista de itens selecionados para compra. | Protegido |
| `/checkout` | Integração direta com o formulário do Stripe. | Protegido |
| `/minhas-compras` | A Galeria de Ativos com as imagens desbloqueadas. | Protegido |

---

## 3. Funcionalidades de Interface (UI)

### 3.1 Muro de Autenticação Inteligente
*   O usuário pode navegar e ver produtos livremente.
*   Ao clicar em "Adicionar ao Carrinho" ou "Comprar Agora", o sistema verifica o estado de autenticação.
*   Se não houver um token válido, a aplicação salva a intenção de compra e redireciona para `/login`. Após o login, o usuário é devolvido à ação original.

### 3.2 O Carrinho e "Comprar Agora"
*   **Carrinho:** Persistido no `localStorage`. Itens permanecem lá mesmo após o fechamento da aba.
*   **Comprar Agora:** Um botão que limpa o fluxo normal, cria uma ordem temporária para apenas aquele item e leva o usuário diretamente para o `/checkout`.

### 3.3 Integração com Stripe Elements
Em vez de redirecionar para o site do Stripe, incorporamos o componente oficial. Isso mantém a confiança do usuário e permite customizar o design para combinar com a marca AtivoSAGA.

---

## 4. Experiência Assíncrona (UX do Microserviço)
Como o backend processa o estoque e o pagamento via RabbitMQ, o Frontend não recebe uma confirmação instantânea. Usaremos os seguintes padrões:

*   **Feedback de Processamento:** Ao finalizar o pagamento, o usuário é enviado para uma tela de "Processando seu Pedido".
*   **Polling com React Query:** O Frontend fará requisições ao Servico Pedidos a cada 3 segundos para verificar se o estado mudou para `CONCLUIDO`.
*   **Liberação Visual (Entrega de Ativos):** Assim que o estado for confirmado, a interface exibe uma animação de sucesso e libera o link para a Galeria de Ativos.

---

## 5. A Galeria de Ativos (O "Produto")
Esta é a área de maior valor para o usuário.

*   Exibição em Grid das imagens compradas.
*   As imagens devem ser carregadas de forma otimizada (Carregamento Preguicoso).
*   **Fator Uau:** Efeito de hover ou zoom para que o usuário sinta que realmente "possui" aquele ativo digital de moda.

---

## 6. Observabilidade e Performance (Datadog RUM)
Para garantir que o sistema atende à alta criticidade técnica, o Frontend terá o **Monitoramento de Usuario Real (RUM)** do Datadog:

*   **Rastreamento de Erros:** Captura erros de JavaScript antes que o usuário reporte.
*   **Performance:** Monitora o tempo de carregamento de imagens e a latência das chamadas para os microserviços.
*   **Jornadas do Usuario:** Visualização de onde os usuários desistem do carrinho de compras.

---

## 7. Requisitos Não-Funcionais
*   **Foco em Dispositivos Moveis (Mobile-First):** A interface deve ser impecável no celular (onde ocorre a maior parte do e-commerce atual).
*   **Segurança:** O Token JWT será armazenado em cookies `HttpOnly` ou memória volátil para mitigar ataques XSS.
*   **Acessibilidade:** Uso de tags semânticas e suporte a leitores de tela.
