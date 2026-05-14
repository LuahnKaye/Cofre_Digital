import time
from fastapi import Request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

# 1. Tráfego: Contador de requisições totais por método e endpoint
REQUISICOES_TOTAIS = Counter(
    "http_requisicoes_totais",
    "Total de requisições HTTP recebidas",
    ["method", "endpoint"]
)

# 2. Latência: Histograma do tempo de resposta
LATENCIA_REQUISICAO = Histogram(
    "http_latencia_segundos",
    "Latência das requisições HTTP em segundos",
    ["method", "endpoint"]
)

# 3. Erros: Contador de requisições que falharam (status 4xx e 5xx)
REQUISICOES_ERRO = Counter(
    "http_requisicoes_erro_totais",
    "Total de requisições HTTP com erro",
    ["method", "endpoint", "status_code"]
)

async def middleware_golden_signals(request: Request, call_next):
    """
    Middleware para capturar os 4 Golden Signals (Latência, Tráfego, Erros).
    A Saturação é geralmente monitorada via infraestrutura (CPU/RAM).
    """
    start_time = time.time()
    
    # Obtém o endpoint para rotulagem (labels)
    endpoint = request.url.path
    metodo = request.method
    
    # Incrementa contador de tráfego
    REQUISICOES_TOTAIS.labels(method=metodo, endpoint=endpoint).inc()
    
    response = await call_next(request)
    
    # Calcula e registra latência
    duracao = time.time() - start_time
    LATENCIA_REQUISICAO.labels(method=metodo, endpoint=endpoint).observe(duracao)
    
    # Registra erros se status >= 400
    if response.status_code >= 400:
        REQUISICOES_ERRO.labels(
            method=metodo, 
            endpoint=endpoint, 
            status_code=response.status_code
        ).inc()
        
    return response

def endpoint_metricas():
    """Retorna as métricas formatadas para o Prometheus."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
