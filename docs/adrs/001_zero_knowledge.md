# ADR 001: Implementação de Arquitetura Zero-Knowledge

## Status
Aceito

## Contexto
O Cofre Digital armazena informações sensíveis (senhas, segredos). Em caso de vazamento de banco de dados ou acesso indevido por administradores, os dados em texto puro seriam expostos, gerando um risco crítico de segurança.

## Decisão
Decidimos implementar uma arquitetura **Zero-Knowledge**, onde o servidor nunca recebe o segredo original em texto puro. 

1.  A criptografia inicial ocorre no navegador (Client-side) usando AES-256.
2.  A chave de decifração é passada via **URL Fragment (#)**. 
3.  O servidor armazena apenas o conteúdo já cifrado pelo cliente.

## Consequências
*   **Positivas**: Segurança absoluta contra vazamentos no DB. Nem mesmo o administrador do sistema consegue ler os dados.
*   **Negativas**: Se o usuário perder o link original (com o fragmento #), o dado torna-se irrecuperável.
