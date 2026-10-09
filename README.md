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
uvicorn app.main:app --reload
```

El servidor se levanta en `http://127.0.0.1:8000`.

## Documentación interactiva

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Endpoints

| Método | Ruta                | Descripción                     |
|--------|---------------------|---------------------------------|
| GET    | `/health`           | Health check (`OK`)             |
| GET    | `/`                 | Redirige a `/health`            |
| GET    | `/pasajes/{ticket}` | Obtener pasaje por ticket       |
| POST   | `/pasajes/`         | Crear un nuevo pasaje           |

## Estructura del proyecto

```
backend-terminales/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── pasaje.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── pasaje.py
│   └── routes/
│       ├── __init__.py
│       └── pasaje.py
├── .env
├── requirements.txt
└── README.md
```
