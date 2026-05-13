Master Overview: AtivoSAGA (End-to-End)
1. Visão Geral e Intento do Projeto
O AtivoSAGA é um ecossistema de e-commerce de ativos digitais desenvolvido sob os princípios de Microserviços e Arquitetura Orientada a Eventos (EDA).

O projeto nasceu da necessidade de demonstrar competência técnica em sistemas distribuídos de alta criticidade, onde a falha de um componente (como o serviço de e-mail) não deve impedir a conclusão da jornada de valor do usuário (a compra e posse do ativo digital).

2. Arquitetura e Comunicação (O "Cérebro")
O sistema é composto por 6 motores independentes que se comunicam via RabbitMQ utilizando o padrão Saga (Coreografia).

Os 6 Microserviços:
Identity (Auth): Gestão de usuários e segurança via JWT.

Order: Orquestrador do ciclo de vida do pedido.

Inventory: Reserva e baixa de estoque de SKUs.

Payment: Gateway Stripe e processamento de Webhooks.

Asset: Entrega e galeria de imagens digitais (O Produto).

Notification: Comunicação assíncrona com o cliente.

3. Estratégia Cloud: AWS Deployment (Item 2 Adicionado)
Para atender ao requisito de experiência sólida em nuvem, o projeto é desenhado para ser Cloud-Native. Embora o desenvolvimento seja via Docker, a infraestrutura de produção é mapeada para a AWS:

Compute (ECS/Fargate): Os containers Docker de cada microserviço rodam no Amazon ECS, garantindo escalabilidade automática.

Database (RDS PostgreSQL): Instâncias gerenciadas para garantir alta disponibilidade e backups automáticos dos bancos de dados.

Messaging (Amazon MQ ou Self-Managed): O RabbitMQ atua como o sistema de mensageria central.

Storage (Amazon S3): Armazenamento das imagens de alta resolução que o usuário "ganha" ao comprar.

Security (IAM & Secrets Manager): Gestão de chaves de API (Stripe/JWT) de forma segura, sem expor no código.

4. DevOps: CI/CD e Qualidade de Software (Item 3 Adicionado)
Um sistema de alta criticidade técnica exige automação total para evitar erros humanos.

Estratégia de CI/CD (GitHub Actions):
Continuous Integration (CI): A cada push, o sistema executa automaticamente o Ruff (Linting) e o Pytest (Testes Unitários e Integração). Se um teste falhar, o código não entra no branch principal.

Continuous Deployment (CD): Após a aprovação dos testes, o GitHub Actions constrói a imagem Docker e faz o deploy automático para o AWS ECS.

Estratégia de Testes (TDD):
Testes Unitários: Foco total na lógica de negócio (ex: cálculo de impostos, expiração de JWT).

Testes de Integração: Simulação da conversa entre o microserviço e o RabbitMQ/PostgreSQL.

Observabilidade (Datadog): Injeção de rastreamento (Distributed Tracing) para monitorar gargalos entre os serviços.

5. Padrões de Projeto e Boas Práticas (Destaques para Entrevista)
Ao ser questionado sobre a qualidade do código, você pode destacar estes pontos:

Saga Pattern (Coreografia): Usamos mensageria (RabbitMQ) para garantir que, se o pagamento for confirmado, o ativo seja liberado sem que o serviço de pagamentos precise "conhecer" o serviço de ativos. Isso é o Desacoplamento Máximo.

Repository & Service Pattern: A lógica de banco de dados e a lógica de negócio são separadas, permitindo que o código seja testável e fácil de manter (Clean Architecture).

Idempotência: O Serviço de Ativos verifica se um pedido já foi processado antes de liberar o item, prevenindo que o usuário receba o mesmo item duas vezes por erro de rede (Crucial para sistemas financeiros).

Clean Code (PT-BR): Seguimos uma convenção rigorosa de nomenclatura em português brasileiro para garantir que qualquer desenvolvedor da equipe entenda a intenção do código sem precisar de tradutores, reduzindo a carga cognitiva.

SOLID: Princípio de Responsabilidade Única (SRP) aplicado em cada microserviço. O Serviço de Identidade só cuida de Login, o de Pagamentos só cuida de Stripe.
