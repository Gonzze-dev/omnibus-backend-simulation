"""Export / load the terminals and bus tickets data, keeping their UUIDs.

The UUIDs must be preserved: omnibus-backend stores the terminal UUID as
bus_terminal.external_terminal_id.

Usage:
    python seed_data.py export [--db terminales] [--file data/seed_data.json]
        Reads terminals and pasajes from the database and writes them to the file.

    python seed_data.py load [--db NAME] [--file data/seed_data.json] [--replace]
        Upserts the file into the database (by uuid). The schema must exist
        (`python migrate.py up`). With --replace, deletes every pasaje and
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
PASAJE_COLUMNS = [
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
        pasajes = conn.execute(
            text(f"SELECT {', '.join(PASAJE_COLUMNS)} FROM pasajes ORDER BY ticket")
        ).mappings().all()

    data = {
        "terminals": [dict(row) for row in terminals],
        "pasajes": [
            {
                **row,
                "start_date": row["start_date"].isoformat(),
                "end_date": row["end_date"].isoformat(),
            }
            for row in pasajes
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"exportados {len(data['terminals'])} terminales y {len(data['pasajes'])} pasajes a {path}")


def name_conflicts(conn, terminals: list[dict]) -> list[str]:
    """Terminal names that already exist in the database with another uuid."""
    existing = dict(conn.execute(text("SELECT name, uuid FROM terminals")).all())
    return [
        f"{t['name']} (base: {existing[t['name']]}, archivo: {t['uuid']})"
        for t in terminals
        if t["name"] in existing and existing[t["name"]] != t["uuid"]
    ]


def load(engine, path: Path, replace: bool) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    terminals, pasajes = data["terminals"], data["pasajes"]

    with engine.begin() as conn:
        if replace:
            conn.execute(text("DELETE FROM pasajes"))
            conn.execute(text("DELETE FROM terminals"))
        else:
            conflicts = name_conflicts(conn, terminals)
            if conflicts:
                sys.exit(
                    "estas terminales ya existen con otro uuid (usá --replace para pisar la base):\n  "
                    + "\n  ".join(conflicts)
                )

        conn.execute(
            text(
                "INSERT INTO terminals (uuid, name) VALUES (:uuid, :name) "
                "ON CONFLICT (uuid) DO UPDATE SET name = EXCLUDED.name"
            ),
            terminals,
        )

        updates = ", ".join(f"{c} = EXCLUDED.{c}" for c in PASAJE_COLUMNS if c != "uuid")
        conn.execute(
            text(
                f"INSERT INTO pasajes ({', '.join(PASAJE_COLUMNS)}) "
                f"VALUES ({', '.join(':' + c for c in PASAJE_COLUMNS)}) "
                f"ON CONFLICT (uuid) DO UPDATE SET {updates}"
            ),
            [{**p, "trip_city": json.dumps(p["trip_city"], ensure_ascii=False)} for p in pasajes],
        )

    print(f"cargados {len(terminals)} terminales y {len(pasajes)} pasajes en {settings.DB_NAME}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Exporta / carga terminales y pasajes")
    parser.add_argument("command", choices=["export", "load"])
    parser.add_argument("--db", help="nombre de la base (por defecto DB_NAME del .env)")
    parser.add_argument("--file", type=Path, default=DEFAULT_FILE)
    parser.add_argument("--replace", action="store_true", help="load: borra los datos existentes antes de cargar")
    args = parser.parse_args()

    engine = make_engine(args.db)
    if args.command == "export":
        export(engine, args.file)
    else:
        load(engine, args.file, args.replace)


if __name__ == "__main__":
    main()
