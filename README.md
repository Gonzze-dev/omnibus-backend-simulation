# API Terminales de Buses

Backend para gestión de pasajes de terminales de buses, construido con **Python** y **FastAPI**.

## Requisitos

- Python 3.10+

## Instalación

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
```

## Base de datos

El esquema se gestiona con `migrate.py`, que usa las mismas variables `DB_*` (`.env`) que la API y registra lo aplicado en la tabla `terminales_schema_migrations`. La API ya no crea tablas al arrancar: hay que migrar antes.

```bash
python migrate.py up        # o: make migrate-up
python migrate.py status    # qué migraciones están aplicadas
python migrate.py baseline  # marca todas como aplicadas sin ejecutarlas
```

- **Base vacía:** `up` ejecuta `migrations/schema.sql` (esquema completo actual) y marca todas las migraciones como aplicadas.
- **Base existente:** `up` aplica solo las migraciones `NNN_nombre.up.sql` pendientes, en orden.
- **Base creada antes de este script** (por `create_all`): ejecutar `baseline` una única vez.

Datos iniciales: `make seed-terminals` (terminales de Argentina) y `python seed.py` (pasajes de ejemplo).

En producción la imagen Docker incluye el script: `python migrate.py up` (por ejemplo como *Pre-Deploy Command* en Railway).

Al agregar una migración nueva, crear `migrations/NNN_nombre.up.sql` y **reflejar el cambio también en `schema.sql`**.

## Ejecutar

```bash
make run    # o: uvicorn app.main:app --reload --port 4990
```

El servidor se levanta en `http://127.0.0.1:4990`.

## Documentación de la API (OpenAPI)

FastAPI genera la especificación **OpenAPI 3.1** a partir de los esquemas Pydantic y los metadatos de cada ruta (resumen, descripción, ejemplos y respuestas de error).

- Swagger UI: `http://127.0.0.1:4990/docs`
- ReDoc: `http://127.0.0.1:4990/redoc`
- Spec en JSON: `http://127.0.0.1:4990/openapi.json`
- Copia versionada: [`docs/openapi.json`](docs/openapi.json)

La copia versionada se regenera con:

```bash
make openapi   # o: python export_openapi.py
```

Hay que regenerarla cada vez que se modifica una ruta o un esquema, para que los consumidores (backend principal, frontend) puedan leer el contrato sin levantar el servicio. Se puede importar en Postman/Insomnia o usar para generar clientes.

## Endpoints

No requieren autenticación (servicio interno). Los errores devuelven `{"detail": "..."}`; los de validación de parámetros, `422` con el formato estándar de FastAPI.

| Método | Ruta                     | Descripción                                                        | Errores       |
|--------|--------------------------|--------------------------------------------------------------------|---------------|
| GET    | `/health`                | Health check (`OK` en texto plano)                                 | —             |
| GET    | `/`                      | Redirige a `/health`                                               | —             |
| GET    | `/bus_tickets/{ticket}`  | Obtener un pasaje por código de boleto                             | 404           |
| POST   | `/bus_tickets/`          | Crear un pasaje                                                    | 404, 409, 422 |
| GET    | `/terminal/`             | Listar terminales (ordenadas por nombre)                           | —             |
| GET    | `/terminal/exist/`       | `?uuid=` → `{"exist": bool}` si la terminal existe                 | 422           |
| GET    | `/terminal/trip/exist/`  | `?uuid=&license_plate=&start_date=` → si hay un viaje ese día      | 422           |
| GET    | `/terminal/trip/`        | `?uuid=&start_date=&end_date=` → viajes de la terminal en el rango | 400, 404, 422 |

### Ejemplos

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

## Estructura del proyecto

```
backend-terminales/
├── app/
│   ├── config.py
│   ├── database.py
│   ├── main.py              # instancia FastAPI y metadatos OpenAPI
│   ├── models/ticket.py     # Terminal, BusTicket (SQLAlchemy)
│   ├── schemas/ticket.py    # esquemas Pydantic (con descripciones y ejemplos)
│   └── routes/ticket.py     # rutas /bus_tickets y /terminal
├── docs/openapi.json        # spec OpenAPI exportada
├── migrations/
├── export_openapi.py
├── migrate.py
├── requirements.txt
└── README.md
```
