"""Script to update all bus tickets so they are valid for today (00:00 - 23:59)."""
from datetime import datetime, time

from app.database import SessionLocal
from app.models.ticket import BusTicket


def update_dates():
    today = datetime.now().date()
    start_date = datetime.combine(today, time.min)
    end_date = datetime.combine(today, time(23, 59, 59))

    db = SessionLocal()
    try:
        updated = db.query(BusTicket).update(
            {BusTicket.start_date: start_date, BusTicket.end_date: end_date},
            synchronize_session=False,
        )
        db.commit()
        print(f"Updated {updated} bus tickets: valid from {start_date} to {end_date}.")
    except Exception as e:
        db.rollback()
        print(f"Update error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    update_dates()
