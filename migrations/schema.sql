-- Full, current schema of backend-terminales (equivalent to applying 001..NNN).
-- `python migrate.py up` uses it to initialize an empty database.
-- When adding a new migration, reflect the change here too.

CREATE TABLE IF NOT EXISTS terminals (
    uuid VARCHAR(36)  PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS bus_tickets (
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

CREATE UNIQUE INDEX IF NOT EXISTS ix_bus_tickets_ticket ON bus_tickets (ticket);
CREATE INDEX IF NOT EXISTS ix_bus_tickets_terminal_uuid ON bus_tickets (terminal_uuid);
