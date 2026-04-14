import uuid

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import JSON

from app.database import Base


class BusTicket(Base):
    __tablename__ = "pasajes"

    uuid = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    postal_code = Column(String(20), nullable=False)
    bus_terminal_name = Column(String(255), nullable=False)
    ticket = Column(String(100), nullable=False, unique=True, index=True)
    dni = Column(String(20), nullable=False)
    name = Column(String(255), nullable=False)
    bus_license_plate = Column(String(20), nullable=False)
    enterprise = Column(String(255), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    trip_city = Column(JSON, nullable=False)
