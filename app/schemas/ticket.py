from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TripCity(BaseModel):
    city_name: str = Field(..., description="Name of the route city", examples=["Rosario"])
    start_date: datetime = Field(..., description="Arrival at the city", examples=["2026-03-30T08:00:00"])
    end_date: datetime = Field(..., description="Departure from the city", examples=["2026-03-30T08:20:00"])
    order: int = Field(..., description="Position of the stop in the route (1 = first)", examples=[1])


class BusTicketBase(BaseModel):
    postal_code: str = Field(..., description="Postal code of the origin terminal", examples=["2000"])
    terminal_uuid: str = Field(
        ...,
        description="UUID of the terminal the bus ticket belongs to",
        examples=["c2bcc293-5b53-4bb2-963c-8f5fe0b91373"],
    )
    ticket: str = Field(..., description="Ticket code (unique)", examples=["TKT-000123"])
    dni: str = Field(..., description="Passenger DNI (national ID)", examples=["40123456"])
    name: str = Field(..., description="Passenger full name", examples=["Juan Pérez"])
    bus_license_plate: str = Field(..., description="Bus license plate", examples=["AB123CD"])
    enterprise: str = Field(..., description="Transport company", examples=["Flecha Bus"])
    start_date: datetime = Field(..., description="Trip departure date and time", examples=["2026-03-30T06:00:00"])
    end_date: datetime = Field(..., description="Trip arrival date and time", examples=["2026-03-30T14:00:00"])
    trip_city: list[TripCity] = Field(..., description="Intermediate stops of the route, ordered by `order`")


class BusTicketCreate(BusTicketBase):
    pass


class BusTicketResponse(BusTicketBase):
    uuid: str = Field(..., description="Generated bus ticket identifier", examples=["3f1c9a52-8d0e-4b7a-9e61-2a4c5d6e7f80"])

    model_config = ConfigDict(from_attributes=True)


class ExistTerminalResponse(BaseModel):
    exist: bool = Field(..., description="`true` if the requested resource exists", examples=[True])


class TerminalItem(BaseModel):
    uuid: str = Field(..., description="Terminal UUID", examples=["c2bcc293-5b53-4bb2-963c-8f5fe0b91373"])
    terminal: str = Field(..., description="Terminal name", examples=["Terminal Córdoba"])


class TerminalBusTicketItem(BaseModel):
    license_plate: str = Field(..., description="Bus license plate", examples=["AB123CD"])
    enterprise: str = Field(..., description="Transport company", examples=["Flecha Bus"])
    start_date: str = Field(..., description="Trip departure (ISO 8601)", examples=["2026-03-30T06:00:00"])
    end_date: str = Field(..., description="Trip arrival (ISO 8601)", examples=["2026-03-30T14:00:00"])


class TerminalBusTicketsResponse(BaseModel):
    name: str = Field(..., description="Terminal name", examples=["Terminal Córdoba"])
    payload: list[TerminalBusTicketItem] = Field(..., description="Trips that overlap the requested range")


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error message", examples=["Terminal not found"])
