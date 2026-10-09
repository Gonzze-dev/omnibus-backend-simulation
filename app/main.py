from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run
from app.config import settings
from app.database import Base, engine
from app.routes.ticket import bus_ticket_router, terminal_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Terminales de Buses",
    description="Backend for bus terminal ticket management",
    version="1.0.0",
    port=4990,
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


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    PORT = 4990

    run(
        "app.main:app",
        host="0.0.0.0",
        port=PORT,
        reload=True,
    )