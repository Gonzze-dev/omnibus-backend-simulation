# Bus Terminals API

Backend for managing bus terminal tickets, built with **Python** and **FastAPI**.

## Requirements

- Python 3.10+

## Installation

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
```

## Database

The schema is managed with `migrate.py`, which uses the same `DB_*` variables (`.env`) as the API and records what has been applied in the `terminals_schema_migrations` table (databases that still have the old `terminales_schema_migrations` table get it renamed automatically). The API no longer creates tables on startup: you have to migrate first.

```bash
python migrate.py up        # or: make migrate-up
python migrate.py status    # which migrations are applied
python migrate.py baseline  # marks all of them as applied without running them
```

- **Empty database:** `up` runs `migrations/schema.sql` (full current schema) and marks every migration as applied.
- **Existing database:** `up` applies only the pending `NNN_name.up.sql` migrations, in order.
- **Database created before this script** (by `create_all`): run `baseline` exactly once.

Initial data: `make seed-terminals` (terminals of Argentina) and `python seed.py` (sample bus tickets).

In production the Docker image includes the script: `python migrate.py up` (for example as the *Pre-Deploy Command* on Railway).

When adding a new migration, create `migrations/NNN_name.up.sql` and **reflect the change in `schema.sql` too**.

## Run

```bash
make run    # or: uvicorn app.main:app --reload --port 4990
```

The server starts at `http://127.0.0.1:4990`.

## API documentation (OpenAPI)

FastAPI generates the **OpenAPI 3.1** specification from the Pydantic schemas and each route's metadata (summary, description, examples and error responses).

- Swagger UI: `http://127.0.0.1:4990/docs`
- ReDoc: `http://127.0.0.1:4990/redoc`
- JSON spec: `http://127.0.0.1:4990/openapi.json`
- Versioned copy: [`docs/openapi.json`](docs/openapi.json)

The versioned copy is regenerated with:

```bash
make openapi   # or: python export_openapi.py
```

It must be regenerated every time a route or schema changes, so that consumers (main backend, frontend) can read the contract without starting the service. It can be imported into Postman/Insomnia or used to generate clients.

## Endpoints

No authentication required (internal service). Errors return `{"detail": "..."}`; parameter validation errors return `422` in the standard FastAPI format.

| Method | Path                     | Description                                                      | Errors        |
|--------|--------------------------|------------------------------------------------------------------|---------------|
| GET    | `/health`                | Health check (`OK` as plain text)                                | —             |
| GET    | `/`                      | Redirects to `/health`                                           | —             |
| GET    | `/bus_tickets/{ticket}`  | Get a bus ticket by ticket code                                  | 404           |
| POST   | `/bus_tickets/`          | Create a bus ticket                                              | 404, 409, 422 |
| GET    | `/terminal/`             | List terminals (ordered by name)                                 | —             |
| GET    | `/terminal/exist/`       | `?uuid=` → `{"exist": bool}` whether the terminal exists         | 422           |
| GET    | `/terminal/trip/exist/`  | `?uuid=&license_plate=&start_date=` → whether there is a trip that day | 422     |
| GET    | `/terminal/trip/`        | `?uuid=&start_date=&end_date=` → the terminal's trips in the range | 400, 404, 422 |

### Examples

```bash
curl http://127.0.0.1:4990/terminal/

curl http://127.0.0.1:4990/bus_tickets/TKT-000123

curl "http://127.0.0.1:4990/terminal/trip/?uuid=c2bcc293-5b53-4bb2-963c-8f5fe0b91373&start_date=2026-03-30T00:00:00&end_date=2026-03-30T23:59:59"

curl -X POST http://127.0.0.1:4990/bus_tickets/   -H "Content-Type: application/json"   -d '{
    "postal_code": "5000",
    "terminal_uuid": "c2bcc293-5b53-4bb2-963c-8f5fe0b91373",
    "ticket": "TKT-000123",
    "dni": "40123456",
    "name": "Juan Pérez",
    "bus_license_plate": "AB123CD",
    "enterprise": "Flecha Bus",
    "start_date": "2026-03-30T06:00:00",
    "end_date": "2026-03-30T14:00:00",
    "trip_city": [
      {"city_name": "Rosario", "start_date": "2026-03-30T08:00:00", "end_date": "2026-03-30T08:20:00", "order": 1}
    ]
  }'
```

## Project structure

```
backend-terminales/
├── app/
│   ├── config.py
│   ├── database.py
│   ├── main.py              # FastAPI instance and OpenAPI metadata
│   ├── models/ticket.py     # Terminal, BusTicket (SQLAlchemy)
│   ├── schemas/ticket.py    # Pydantic schemas (with descriptions and examples)
│   └── routes/ticket.py     # /bus_tickets and /terminal routes
├── docs/openapi.json        # exported OpenAPI spec
├── migrations/
├── export_openapi.py
├── migrate.py
├── requirements.txt
└── README.md
```
