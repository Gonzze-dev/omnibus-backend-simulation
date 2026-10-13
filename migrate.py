"""Apply the SQL migrations in migrations/ and record them in
terminals_schema_migrations.

Usage:
    python migrate.py [--dir migrations] <up|status|baseline>

    up        Empty database: runs schema.sql and marks every migration applied.
              Existing database: runs the pending migrations in order.
    status    Lists the migrations and whether they are applied.
    baseline  Marks every migration as applied without running it
              (for databases created before this script existed).
"""
import argparse
import sys
from pathlib import Path

from app.database import engine

MIGRATIONS_TABLE = "terminals_schema_migrations"
# Former name of MIGRATIONS_TABLE; renamed on startup if it still exists.
LEGACY_MIGRATIONS_TABLE = "terminales_schema_migrations"
SCHEMA_FILE = "schema.sql"
UP_SUFFIX = ".up.sql"
# Its presence means the database already has the application schema.
SENTINEL_TABLES = ["bus_tickets", "pasajes"]  # "pasajes" is the former name of bus_tickets


def list_migrations(directory: Path) -> list[str]:
    return sorted(f.name[: -len(UP_SUFFIX)] for f in directory.glob(f"*{UP_SUFFIX}"))


def applied(cur) -> set[str]:
    cur.execute(f"SELECT name FROM {MIGRATIONS_TABLE}")
    return {name for (name,) in cur.fetchall()}


def record(cur, names: list[str]) -> None:
    for name in names:
        cur.execute(
            f"INSERT INTO {MIGRATIONS_TABLE} (name) VALUES (%s) ON CONFLICT DO NOTHING",
            (name,),
        )


def exec_file(cur, path: Path) -> None:
    print(f"running {path.name}")
    # Without parameters psycopg2 sends the text as-is, so several statements work.
    cur.execute(path.read_text(encoding="utf-8"))


def up(conn, directory: Path) -> None:
    names = list_migrations(directory)
    with conn.cursor() as cur:
        done = applied(cur)
        if not done:
            cur.execute("SELECT bool_or(to_regclass(t) IS NOT NULL) FROM unnest(%s) AS t", (SENTINEL_TABLES,))
            if cur.fetchone()[0]:
                sys.exit(
                    f"the database already has tables but no migrations are recorded in "
                    f"{MIGRATIONS_TABLE}; if it is up to date run `python migrate.py baseline`"
                )
            print(f"empty database: applying {SCHEMA_FILE}")
            exec_file(cur, directory / SCHEMA_FILE)
            record(cur, names)
            conn.commit()
            return

    pending = [name for name in names if name not in done]
    for name in pending:
        # Each migration runs in its own transaction.
        with conn.cursor() as cur:
            exec_file(cur, directory / f"{name}{UP_SUFFIX}")
            record(cur, [name])
        conn.commit()
    if not pending:
        print("no pending migrations")


def status(conn, directory: Path) -> None:
    with conn.cursor() as cur:
        done = applied(cur)
    for name in list_migrations(directory):
        print(f"{'applied' if name in done else 'pending':<10} {name}")


def baseline(conn, directory: Path) -> None:
    names = list_migrations(directory)
    with conn.cursor() as cur:
        record(cur, names)
    conn.commit()
    print(f"{len(names)} migrations marked as applied")


COMMANDS = {"up": up, "status": status, "baseline": baseline}


def main() -> None:
    parser = argparse.ArgumentParser(description="SQL migration runner")
    parser.add_argument("command", nargs="?", default="up", choices=COMMANDS)
    parser.add_argument("--dir", default="migrations", type=Path)
    args = parser.parse_args()

    conn = engine.raw_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT to_regclass(%s) IS NOT NULL AND to_regclass(%s) IS NULL",
                (LEGACY_MIGRATIONS_TABLE, MIGRATIONS_TABLE),
            )
            if cur.fetchone()[0]:
                cur.execute(f"ALTER TABLE {LEGACY_MIGRATIONS_TABLE} RENAME TO {MIGRATIONS_TABLE}")
            cur.execute(
                f"""CREATE TABLE IF NOT EXISTS {MIGRATIONS_TABLE} (
                    name       VARCHAR(255) PRIMARY KEY,
                    applied_at TIMESTAMPTZ  NOT NULL DEFAULT now()
                )"""
            )
        conn.commit()
        COMMANDS[args.command](conn, args.dir)
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
