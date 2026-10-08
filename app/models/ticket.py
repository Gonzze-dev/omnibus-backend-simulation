import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from app.database import Base


class Terminal(Base):
    __tablename__ = "terminals"

    uuid = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)

    bus_tickets = relationship("BusTicket", back_populates="terminal")


class BusTicket(Base):
    __tablename__ = "pasajes"

    uuid = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    postal_code = Column(String(20), nullable=False)
    terminal_uuid = Column(
        String(36), ForeignKey("terminals.uuid"), nullable=False, index=True
    )
    ticket = Column(String(100), nullable=False, unique=True, index=True)
    dni = Column(String(20), nullable=False)
    name = Column(String(255), nullable=False)
    bus_license_plate = Column(String(20), nullable=False)
    enterprise = Column(String(255), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    trip_city = Column(JSON, nullable=False)

    terminal = relationship("Terminal", back_populates="bus_tickets")
