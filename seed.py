"""Seed script to insert sample data into the database."""
from app.database import SessionLocal, engine, Base
from app.models.ticket import BusTicket
from bus_tickets import bus_tickets

Base.metadata.create_all(bind=engine)


def seed():
    db = SessionLocal()
    try:
        count = db.query(BusTicket).count()
        if count > 0:
            print(f"Database already has {count} bus tickets. Skipping seed.")
            return

        for data in bus_tickets:
            row = BusTicket(**data)
            db.add(row)

        db.commit()
        print(f"Inserted {len(bus_tickets)} bus tickets successfully.")
    except Exception as e:
        db.rollback()
        print(f"Insert error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
