# ADR 003: Estratégia de Monitoramento (Golden Signals)

## Status
Aceito

## Contexto
Sistemas de segurança precisam de alta disponibilidade e visibilidade de erros. Logs tradicionais não são suficientes para detectar anomalias de performance ou ataques de negação de serviço em tempo real.

## Decisão
Adotamos o **Prometheus** como coletor de métricas e o **Grafana** para visualização, focando nos **4 Golden Signals** (Latência, Tráfego, Erros e Saturação). Criamos um middleware customizado no FastAPI para expor essas métricas no endpoint `/metrics`.

## Consequências
*   **Positivas**: Visibilidade total da saúde do sistema. Facilita a identificação de picos de carga ou bugs silenciosos (ex: aumento repentino de 5xx).
*   **Negativas**: Exposição do endpoint `/metrics` (que deve ser protegido por firewall/VPN em produção real).
