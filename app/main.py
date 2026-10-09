from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, RedirectResponse
from uvicorn import run
from app.config import settings
from app.routes.ticket import bus_ticket_router, terminal_router

DESCRIPTION = """
Servicio upstream de terminales de ómnibus. Expone las terminales y los
pasajes vendidos en ellas, y es consumido por el backend principal
(`EXTERNAL_TERMINAL_UPSTREAM_URL`) y, a través de él, por el microservicio de OCR.

**Autenticación:** ninguna. Es un servicio interno accesible solo desde la red del sistema.

**Fechas:** ISO 8601 (`2026-03-30T06:00:00`). Las fechas sin zona horaria se
interpretan tal como están guardadas en la base.

**Errores:** las respuestas de error tienen la forma `{"detail": "..."}`. Los
errores de validación (422) siguen el formato estándar de FastAPI.
"""

TAGS_METADATA = [
    {"name": "Bus Tickets", "description": "Consulta y alta de pasajes por código de boleto."},
    {"name": "Terminal", "description": "Terminales y viajes asociados a cada una."},
    {"name": "Health", "description": "Estado del servicio."},
]

app = FastAPI(
    title="API Terminales de Buses",
    summary="Gestión de terminales y pasajes de ómnibus",
    description=DESCRIPTION,
    version="1.0.0",
    openapi_tags=TAGS_METADATA,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bus_ticket_router)
app.include_router(terminal_router)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/health")


@app.get(
    "/health",
    tags=["Health"],
    response_class=PlainTextResponse,
    summary="Health check",
    responses={200: {"content": {"text/plain": {"example": "OK"}}}},
)
def health_check():
    """Devuelve `OK` en texto plano si el servicio está en funcionamiento."""
    return "OK"

if __name__ == "__main__":
    PORT = 4990

    run(
        "app.main:app",
        host="0.0.0.0",
        port=PORT,
        reload=True,
    )