from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TripCity(BaseModel):
    city_name: str = Field(..., description="Nombre de la ciudad del recorrido", examples=["Rosario"])
    start_date: datetime = Field(..., description="Llegada a la ciudad", examples=["2026-03-30T08:00:00"])
    end_date: datetime = Field(..., description="Salida de la ciudad", examples=["2026-03-30T08:20:00"])
    order: int = Field(..., description="Posición de la parada en el recorrido (1 = primera)", examples=[1])


class BusTicketBase(BaseModel):
    postal_code: str = Field(..., description="Código postal de la terminal de origen", examples=["2000"])
    terminal_uuid: str = Field(
        ...,
        description="UUID de la terminal a la que pertenece el pasaje",
        examples=["c2bcc293-5b53-4bb2-963c-8f5fe0b91373"],
    )
    ticket: str = Field(..., description="Código de boleto (único)", examples=["TKT-000123"])
    dni: str = Field(..., description="DNI del pasajero", examples=["40123456"])
    name: str = Field(..., description="Nombre completo del pasajero", examples=["Juan Pérez"])
    bus_license_plate: str = Field(..., description="Patente del colectivo", examples=["AB123CD"])
    enterprise: str = Field(..., description="Empresa de transporte", examples=["Flecha Bus"])
    start_date: datetime = Field(..., description="Fecha y hora de salida del viaje", examples=["2026-03-30T06:00:00"])
    end_date: datetime = Field(..., description="Fecha y hora de llegada del viaje", examples=["2026-03-30T14:00:00"])
    trip_city: list[TripCity] = Field(..., description="Paradas intermedias del recorrido, ordenadas por `order`")


class BusTicketCreate(BusTicketBase):
    pass


class BusTicketResponse(BusTicketBase):
    uuid: str = Field(..., description="Identificador generado del pasaje", examples=["3f1c9a52-8d0e-4b7a-9e61-2a4c5d6e7f80"])

    model_config = ConfigDict(from_attributes=True)


class ExistTerminalResponse(BaseModel):
    exist: bool = Field(..., description="`true` si el recurso consultado existe", examples=[True])


class TerminalItem(BaseModel):
    uuid: str = Field(..., description="UUID de la terminal", examples=["c2bcc293-5b53-4bb2-963c-8f5fe0b91373"])
    terminal: str = Field(..., description="Nombre de la terminal", examples=["Terminal Córdoba"])


class TerminalBusTicketItem(BaseModel):
    license_plate: str = Field(..., description="Patente del colectivo", examples=["AB123CD"])
    enterprise: str = Field(..., description="Empresa de transporte", examples=["Flecha Bus"])
    start_date: str = Field(..., description="Salida del viaje (ISO 8601)", examples=["2026-03-30T06:00:00"])
    end_date: str = Field(..., description="Llegada del viaje (ISO 8601)", examples=["2026-03-30T14:00:00"])


class TerminalBusTicketsResponse(BaseModel):
    name: str = Field(..., description="Nombre de la terminal", examples=["Terminal Córdoba"])
    payload: list[TerminalBusTicketItem] = Field(..., description="Viajes que se superponen con el rango pedido")


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Mensaje de error", examples=["Terminal not found"])
