"""Export / load the terminals and bus tickets data, keeping their UUIDs.

The UUIDs must be preserved: omnibus-backend stores the terminal UUID as
bus_terminal.external_terminal_id.

Usage:
    python seed_data.py export [--db NAME] [--file data/seed_data.json]
        Reads terminals and bus tickets from the database and writes them to the file.

    python seed_data.py load [--db NAME] [--file data/seed_data.json] [--replace]
        Upserts the file into the database (by uuid). The schema must exist
        (`python migrate.py up`). With --replace, deletes every bus ticket and
        terminal first, so the database ends up exactly like the file.

The connection comes from .env (DB_URL, DB_USER, ...); --db overrides DB_NAME.
"""
import argparse
import json
import sys
from pathlib import Path

from sqlalchemy import create_engine, text

from app.config import settings

DEFAULT_FILE = Path("data/seed_data.json")

TERMINAL_COLUMNS = ["uuid", "name"]
BUS_TICKET_COLUMNS = [
    "uuid",
    "postal_code",
    "terminal_uuid",
    "ticket",
    "dni",
    "name",
    "bus_license_plate",
    "enterprise",
    "start_date",
    "end_date",
    "trip_city",
]


def make_engine(db_name: str | None):
    if db_name:
        settings.DB_NAME = db_name
    return create_engine(settings.DATABASE_URL, echo=False)


def export(engine, path: Path) -> None:
    with engine.connect() as conn:
        terminals = conn.execute(
            text(f"SELECT {', '.join(TERMINAL_COLUMNS)} FROM terminals ORDER BY name")
        ).mappings().all()
        bus_tickets = conn.execute(
            text(f"SELECT {', '.join(BUS_TICKET_COLUMNS)} FROM bus_tickets ORDER BY ticket")
        ).mappings().all()

    data = {
        "terminals": [dict(row) for row in terminals],
        "bus_tickets": [
            {
                **row,
                "start_date": row["start_date"].isoformat(),
                "end_date": row["end_date"].isoformat(),
            }
            for row in bus_tickets
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"exported {len(data['terminals'])} terminals and {len(data['bus_tickets'])} bus tickets to {path}")


def name_conflicts(conn, terminals: list[dict]) -> list[str]:
    """Terminal names that already exist in the database with another uuid."""
    existing = dict(conn.execute(text("SELECT name, uuid FROM terminals")).all())
    return [
        f"{t['name']} (database: {existing[t['name']]}, file: {t['uuid']})"
        for t in terminals
        if t["name"] in existing and existing[t["name"]] != t["uuid"]
    ]


def load(engine, path: Path, replace: bool) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    terminals, bus_tickets = data["terminals"], data["bus_tickets"]

    with engine.begin() as conn:
        if replace:
            conn.execute(text("DELETE FROM bus_tickets"))
            conn.execute(text("DELETE FROM terminals"))
        else:
            conflicts = name_conflicts(conn, terminals)
            if conflicts:
                sys.exit(
                    "these terminals already exist with another uuid (use --replace to overwrite the database):\n  "
                    + "\n  ".join(conflicts)
                )

        conn.execute(
            text(
                "INSERT INTO terminals (uuid, name) VALUES (:uuid, :name) "
                "ON CONFLICT (uuid) DO UPDATE SET name = EXCLUDED.name"
            ),
            terminals,
        )

        updates = ", ".join(f"{c} = EXCLUDED.{c}" for c in BUS_TICKET_COLUMNS if c != "uuid")
        conn.execute(
            text(
                f"INSERT INTO bus_tickets ({', '.join(BUS_TICKET_COLUMNS)}) "
                f"VALUES ({', '.join(':' + c for c in BUS_TICKET_COLUMNS)}) "
                f"ON CONFLICT (uuid) DO UPDATE SET {updates}"
            ),
            [{**p, "trip_city": json.dumps(p["trip_city"], ensure_ascii=False)} for p in bus_tickets],
        )

    print(f"loaded {len(terminals)} terminals and {len(bus_tickets)} bus tickets into {settings.DB_NAME}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export / load terminals and bus tickets")
    parser.add_argument("command", choices=["export", "load"])
    parser.add_argument("--db", help="database name (defaults to DB_NAME from .env)")
    parser.add_argument("--file", type=Path, default=DEFAULT_FILE)
    parser.add_argument("--replace", action="store_true", help="load: deletes the existing data before loading")
    args = parser.parse_args()

    engine = make_engine(args.db)
    if args.command == "export":
        export(engine, args.file)
    else:
        load(engine, args.file, args.replace)


if __name__ == "__main__":
    main()
