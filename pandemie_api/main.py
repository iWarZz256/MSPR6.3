from fastapi import FastAPI
from database import Base, engine
from routers import continent, pays, famille, virus, logging, pandemie, suivi, auth, user
from fastapi.middleware.cors import CORSMiddleware
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
