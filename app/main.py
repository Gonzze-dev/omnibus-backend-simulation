from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, RedirectResponse
from uvicorn import run
from app.config import settings
from app.routes.ticket import bus_ticket_router, terminal_router

DESCRIPTION = """
Upstream bus terminal service. Exposes the terminals and the bus tickets
sold at them, and is consumed by the main backend
(`EXTERNAL_TERMINAL_UPSTREAM_URL`) and, through it, by the OCR microservice.

**Authentication:** none. It is an internal service reachable only from the system network.

**Dates:** ISO 8601 (`2026-03-30T06:00:00`). Dates without a time zone are
interpreted exactly as stored in the database.

**Errors:** error responses have the shape `{"detail": "..."}`. Validation
errors (422) follow the standard FastAPI format.
"""

TAGS_METADATA = [
    {"name": "Bus Tickets", "description": "Look up and create bus tickets by ticket code."},
    {"name": "Terminal", "description": "Terminals and the trips associated with each one."},
    {"name": "Health", "description": "Service status."},
]

app = FastAPI(
    title="Bus Terminals API",
    summary="Bus terminal and bus ticket management",
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
    """Returns `OK` as plain text if the service is up."""
    return "OK"

if __name__ == "__main__":
    PORT = 4990

    run(
        "app.main:app",
        host="0.0.0.0",
        port=PORT,
        reload=True,
    )