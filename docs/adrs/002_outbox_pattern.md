# ADR 002: Uso do Transactional Outbox Pattern

## Status
Aceito

## Contexto
Ao resgatar um segredo, precisamos diminuir o contador no banco de dados e notificar um worker assíncrono para a deleção física. Se fizermos o commit no banco e enviarmos para o RabbitMQ sequencialmente, uma falha na rede entre o banco e o broker causaria inconsistência (o dado foi lido, mas nunca será apagado fisicamente).

## Decisão
Implementamos o **Transactional Outbox Pattern**. O evento de deleção é salvo na mesma transação SQL que atualiza o segredo. Um serviço `OutboxRelay` separado lê esses eventos e os publica no RabbitMQ com garantia de entrega *At Least Once*.

## Consequências
*   **Positivas**: Consistência eventual garantida. Nunca haverá um segredo que expirou no DB mas não foi deletado no worker.
*   **Negativas**: Aumenta ligeiramente a latência da escrita devido à inserção na tabela de outbox.
