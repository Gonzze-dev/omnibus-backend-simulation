from datetime import datetime

from pydantic import BaseModel


class TripCity(BaseModel):
    city_name: str
    start_date: datetime
    end_date: datetime
    order: int


class BusTicketBase(BaseModel):
    postal_code: str
    terminal_uuid: str
    ticket: str
    dni: str
    name: str
    bus_license_plate: str
    enterprise: str
    start_date: datetime
    end_date: datetime
    trip_city: list[TripCity]


class BusTicketCreate(BusTicketBase):
    pass


class BusTicketResponse(BusTicketBase):
    uuid: str

    class Config:
        from_attributes = True


class ExistTerminalResponse(BaseModel):
    exist: bool


class TerminalItem(BaseModel):
    uuid: str
    terminal: str


class TerminalBusTicketItem(BaseModel):
    license_plate: str
    enterprise: str
    start_date: str
    end_date: str


class TerminalBusTicketsResponse(BaseModel):
    name: str
    payload: list[TerminalBusTicketItem]
