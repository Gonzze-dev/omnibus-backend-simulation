# Build context: raíz del repo (docker build -f infra.prod/Dockerfile .)
# En Railway: RAILWAY_DOCKERFILE_PATH=infra.prod/Dockerfile
# Migraciones (p. ej. como Pre-Deploy Command en Railway): python migrate.py up

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY app ./app
COPY migrations ./migrations
COPY migrate.py seed.py seed_terminals.py terminals.py bus_tickets.py update_dates.py ./

RUN useradd -r -u 10001 app
USER app

EXPOSE 4990

CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-4990} --proxy-headers --forwarded-allow-ips='*'"]
