from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from interfaces.api import router as api_router
from infrastructure.monitoramento import middleware_golden_signals, endpoint_metricas

app = FastAPI(
    title="Cofre Digital API",
    description="Plataforma de Custódia de Segredos Efêmeros",
    version="1.0.0"
)

# Registro de Middleware de Monitoramento (Golden Signals)
@app.middleware("http")
async def monitorar_requisicoes(request, call_next):
    return await middleware_golden_signals(request, call_next)

# Configuração de CORS para permitir acesso do Frontend futuramente
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Em produção, especificar as origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusão das rotas
app.include_router(api_router)

# Endpoint para o Prometheus coletar métricas
@app.get("/metrics", tags=["Monitoramento"])
def obter_metricas():
    return endpoint_metricas()

@app.get("/", tags=["Saúde"])
def verificar_saude():
    """Endpoint básico para conferir se o serviço está online."""
    return {"status": "online", "projeto": "Cofre Digital"}

if __name__ == "__main__":
    import uvicorn
    # Inicializa o servidor Uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=54321,
        reload=True,
        log_level="info"
    )
