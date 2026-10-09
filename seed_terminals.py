"""Seed script to insert the bus terminals of Argentina into the database."""
from app.database import SessionLocal
from app.models.ticket import Terminal
from terminals import terminals


def seed_terminals():
    db = SessionLocal()
    try:
        existing = {name for (name,) in db.query(Terminal.name).all()}
        missing = [name for name in terminals if name not in existing]
        for name in missing:
            db.add(Terminal(name=name))

        db.commit()
        print(f"Inserted {len(missing)} terminals ({len(existing)} already existed).")
    except Exception as e:
        db.rollback()
        print(f"Insert error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_terminals()
