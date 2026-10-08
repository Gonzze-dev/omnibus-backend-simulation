from datetime import datetime, time, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.ticket import BusTicket, Terminal
from app.schemas.ticket import (
    BusTicketCreate,
    BusTicketResponse,
    ExistTerminalResponse,
    TerminalBusTicketItem,
    TerminalBusTicketsResponse,
    TerminalItem,
)

bus_ticket_router = APIRouter(prefix="/bus_tickets", tags=["Bus Tickets"])
terminal_router = APIRouter(prefix="/terminal", tags=["Terminal"])


@bus_ticket_router.get("/{ticket}", response_model=BusTicketResponse)
def get_bus_ticket_by_ticket(ticket: str, db: Session = Depends(get_db)):
    bus_ticket = db.query(BusTicket).filter(BusTicket.ticket == ticket).first()
    if not bus_ticket:
        raise HTTPException(status_code=404, detail="Bus ticket not found")
    return bus_ticket


@bus_ticket_router.post("/", response_model=BusTicketResponse, status_code=201)
def create_bus_ticket(data: BusTicketCreate, db: Session = Depends(get_db)):
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


@terminal_router.get("/", response_model=list[TerminalItem])
def list_terminals(db: Session = Depends(get_db)):
    terminals = db.query(Terminal).order_by(Terminal.name).all()
    return [TerminalItem(uuid=t.uuid, terminal=t.name) for t in terminals]


@terminal_router.get(
    "/exist/",
    response_model=ExistTerminalResponse,
)
def exist_terminal(
    uuid: UUID = Query(..., description="Terminal UUID"),
    db: Session = Depends(get_db),
):
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
)
def exist_trip(
    uuid: UUID = Query(..., description="Terminal UUID"),
    license_plate: str = Query(..., description="Bus license plate"),
    start_date: datetime = Query(
        ...,
        description="Any instant on the calendar day to check (e.g. 2026-03-30)",
    ),
    db: Session = Depends(get_db),
):
    """
    Whether the terminal has a bus ticket with that license plate whose trip
    overlaps the full calendar day of `start_date` (00:00–24:00 that date).
    """
    day_start, day_end = _calendar_day_bounds(start_date)
    print(day_start, day_end)
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
)
def get_bus_tickets_by_terminal(
    uuid: UUID = Query(..., description="Terminal UUID"),
    start_date: datetime = Query(..., description="Range start (inclusive)"),
    end_date: datetime = Query(..., description="Range end (inclusive)"),
    db: Session = Depends(get_db),
):
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
