from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest
from prometheus_client.exposition import CONTENT_TYPE_LATEST
import time

from database import Base, engine
from routers import continent, pays, famille, virus, logging, pandemie, suivi, auth, user
from predict import router as predict_router
from predict import model

# Création des tables dans la base si elles n'existent pas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Suivi des Pandémies",
    description="Un projet FastAPI avec MySQL pour suivre les pandémies dans le monde.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routers
app.include_router(continent.router)
app.include_router(pays.router)
app.include_router(famille.router)
app.include_router(virus.router)
app.include_router(logging.router)
app.include_router(pandemie.router)
app.include_router(suivi.router)
app.include_router(predict_router)
app.include_router(auth.router)
app.include_router(user.router)

# Endpoints de base
@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API de suivi des pandémies."}

@app.get("/health", summary="Vérifie que l'API et le modèle sont opérationnels")
def health_check():
    return {
        "status": "ok",
        "model_type": type(model).__name__,
        "n_features_in": getattr(model, "n_features_in_", None)
    }

# -------- Monitoring Prometheus --------
REQUEST_COUNT = Counter('http_requests_total', 'Nombre total de requêtes HTTP', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'Durée des requêtes HTTP', ['method', 'endpoint'])

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    REQUEST_LATENCY.labels(request.method, request.url.path).observe(process_time)
    REQUEST_COUNT.labels(request.method, request.url.path).inc()
    return response

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
