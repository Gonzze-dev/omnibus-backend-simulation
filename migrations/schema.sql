-- Esquema completo y actual de backend-terminales (equivale a aplicar 001..NNN).
-- `python migrate.py up` lo usa para inicializar una base vacía.
-- Al agregar una migración nueva, reflejar el cambio también acá.

CREATE TABLE IF NOT EXISTS terminals (
    uuid VARCHAR(36)  PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS pasajes (
    uuid              VARCHAR(36)  PRIMARY KEY,
    postal_code       VARCHAR(20)  NOT NULL,
    terminal_uuid     VARCHAR(36)  NOT NULL REFERENCES terminals (uuid),
    ticket            VARCHAR(100) NOT NULL,
    dni               VARCHAR(20)  NOT NULL,
    name              VARCHAR(255) NOT NULL,
    bus_license_plate VARCHAR(20)  NOT NULL,
    enterprise        VARCHAR(255) NOT NULL,
    start_date        TIMESTAMP    NOT NULL,
    end_date          TIMESTAMP    NOT NULL,
    trip_city         JSON         NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_pasajes_ticket ON pasajes (ticket);
CREATE INDEX IF NOT EXISTS ix_pasajes_terminal_uuid ON pasajes (terminal_uuid);
