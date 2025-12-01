from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import APP_NAME, APP_VERSION
from routes import huespedes, hoteles, habitaciones

# Crear aplicación
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="API de Sistema de Reservas y Gestión Hotelera"
)

# Configurar CORS para que Android pueda conectarse
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, cambiar a dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(huespedes.router)
app.include_router(hoteles.router)
app.include_router(habitaciones.router)

@app.get("/")
def root():
    """Endpoint raíz - verificar que la API está funcionando"""
    return {
        "mensaje": "Bienvenido a TRANQUIDESCANSO API",
        "version": APP_VERSION,
        "docs": "/docs"
    }

@app.get("/health")
def health():
    """Health check para Render"""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
