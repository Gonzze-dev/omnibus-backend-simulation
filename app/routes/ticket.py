from datetime import datetime, time, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.ticket import BusTicket, Terminal
from app.schemas.ticket import (
    BusTicketCreate,
    BusTicketResponse,
    ErrorResponse,
    ExistTerminalResponse,
    TerminalBusTicketItem,
    TerminalBusTicketsResponse,
    TerminalItem,
)

bus_ticket_router = APIRouter(prefix="/bus_tickets", tags=["Bus Tickets"])
terminal_router = APIRouter(prefix="/terminal", tags=["Terminal"])


@bus_ticket_router.get(
    "/{ticket}",
    response_model=BusTicketResponse,
    summary="Obtener pasaje por código de boleto",
    responses={404: {"model": ErrorResponse, "description": "No existe un pasaje con ese código"}},
)
def get_bus_ticket_by_ticket(ticket: str, db: Session = Depends(get_db)):
    """
    Devuelve los datos completos de un pasaje (pasajero, colectivo, fechas y
    paradas). Lo consume el backend principal cuando un usuario se registra
    en un viaje.
    """
    bus_ticket = db.query(BusTicket).filter(BusTicket.ticket == ticket).first()
    if not bus_ticket:
        raise HTTPException(status_code=404, detail="Bus ticket not found")
    return bus_ticket


@bus_ticket_router.post(
    "/",
    response_model=BusTicketResponse,
    status_code=201,
    summary="Crear pasaje",
    responses={
        404: {"model": ErrorResponse, "description": "La terminal indicada no existe"},
        409: {"model": ErrorResponse, "description": "Ya existe un pasaje con ese código de boleto"},
    },
)
def create_bus_ticket(data: BusTicketCreate, db: Session = Depends(get_db)):
    """
    Registra un pasaje nuevo. El código `ticket` debe ser único y
    `terminal_uuid` debe referenciar una terminal existente.
    """
    existing = db.query(BusTicket).filter(BusTicket.ticket == data.ticket).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail="A bus ticket with that ticket code already exists",
        )
    if not db.get(Terminal, data.terminal_uuid):
        raise HTTPException(status_code=404, detail="Terminal not found")

    bus_ticket = BusTicket(**data.model_dump())
    db.add(bus_ticket)
    db.commit()
    db.refresh(bus_ticket)
    return bus_ticket


@terminal_router.get(
    "/",
    response_model=list[TerminalItem],
    summary="Listar terminales",
)
def list_terminals(db: Session = Depends(get_db)):
    """Todas las terminales registradas, ordenadas por nombre."""
    terminals = db.query(Terminal).order_by(Terminal.name).all()
    return [TerminalItem(uuid=t.uuid, terminal=t.name) for t in terminals]


@terminal_router.get(
    "/exist/",
    response_model=ExistTerminalResponse,
    summary="Verificar si existe una terminal",
)
def exist_terminal(
    uuid: UUID = Query(..., description="UUID de la terminal"),
    db: Session = Depends(get_db),
):
    """
    Indica si existe una terminal con ese UUID. El backend principal lo usa
    antes de crear una terminal interna asociada.
    """
    found = db.get(Terminal, str(uuid))
    return {"exist": found is not None}


def _calendar_day_bounds(dt: datetime) -> tuple[datetime, datetime]:
    """Start of dt's calendar day and exclusive end (next midnight)."""
    if dt.tzinfo is not None:
        day_start = datetime.combine(dt.date(), time.min, tzinfo=dt.tzinfo)
    else:
        day_start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)
    return day_start, day_end


@terminal_router.get(
    "/trip/exist/",
    response_model=ExistTerminalResponse,
    summary="Verificar si existe un viaje en una fecha",
)
def exist_trip(
    uuid: UUID = Query(..., description="UUID de la terminal"),
    license_plate: str = Query(..., description="Patente del colectivo"),
    start_date: datetime = Query(
        ...,
        description="Cualquier instante del día calendario a verificar (p. ej. 2026-03-30)",
    ),
    db: Session = Depends(get_db),
):
    """
    Indica si la terminal tiene un pasaje con esa patente cuyo viaje se
    superpone con el día calendario de `start_date` (00:00–24:00 de esa
    fecha). Lo usa el backend principal antes de enviar notificaciones de
    demora.
    """
    day_start, day_end = _calendar_day_bounds(start_date)
    found = (
        db.query(BusTicket)
        .filter(
            BusTicket.terminal_uuid == str(uuid),
            BusTicket.bus_license_plate == license_plate,
            BusTicket.start_date < day_end,
            BusTicket.end_date > day_start,
        )
        .first()
    )

    return {"exist": found is not None}


@terminal_router.get(
    "/trip/",
    response_model=TerminalBusTicketsResponse,
    summary="Listar viajes de una terminal en un rango",
    responses={
        400: {"model": ErrorResponse, "description": "`start_date` es posterior a `end_date`"},
        404: {"model": ErrorResponse, "description": "La terminal no existe"},
    },
)
def get_bus_tickets_by_terminal(
    uuid: UUID = Query(..., description="UUID de la terminal"),
    start_date: datetime = Query(..., description="Inicio del rango (inclusive)"),
    end_date: datetime = Query(..., description="Fin del rango (inclusive)"),
    db: Session = Depends(get_db),
):
    """
    Devuelve los viajes de la terminal que se superponen con el rango
    `[start_date, end_date]`, ordenados por salida. Lo usa el microservicio
    de OCR (vía backend principal) para saber qué colectivos se esperan.
    """
    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date cannot be after end_date",
        )

    terminal = db.get(Terminal, str(uuid))
    if not terminal:
        raise HTTPException(status_code=404, detail="Terminal not found")

    tickets = (
        db.query(BusTicket)
        .filter(
            BusTicket.terminal_uuid == terminal.uuid,
            BusTicket.start_date <= end_date,
            BusTicket.end_date >= start_date,
        )
        .order_by(BusTicket.start_date)
        .all()
    )

    payload = [
        TerminalBusTicketItem(
            license_plate=p.bus_license_plate,
            enterprise=p.enterprise,
            start_date=p.start_date.isoformat(),
            end_date=p.end_date.isoformat(),
        )
        for p in tickets
    ]

    return TerminalBusTicketsResponse(name=terminal.name, payload=payload)
