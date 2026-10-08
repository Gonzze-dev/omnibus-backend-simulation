"""Seed script to insert sample data into the database."""
from app.database import SessionLocal, engine, Base
from app.models.ticket import BusTicket, Terminal
from bus_tickets import bus_tickets

Base.metadata.create_all(bind=engine)


def seed():
    db = SessionLocal()
    try:
        count = db.query(BusTicket).count()
        if count > 0:
            print(f"Database already has {count} bus tickets. Skipping seed.")
            return

        terminals = {t.name: t for t in db.query(Terminal).all()}
        for data in bus_tickets:
            data = dict(data)
            terminal_name = data.pop("bus_terminal_name")
            terminal = terminals.get(terminal_name)
            if terminal is None:
                terminal = Terminal(name=terminal_name)
                db.add(terminal)
                terminals[terminal_name] = terminal
            db.add(BusTicket(**data, terminal=terminal))

        db.commit()
        print(f"Inserted {len(bus_tickets)} bus tickets successfully.")
    except Exception as e:
        db.rollback()
        print(f"Insert error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
