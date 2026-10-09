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
