-- Renames the bus tickets table and its indexes/constraints to English.

ALTER TABLE pasajes RENAME TO bus_tickets;

ALTER TABLE bus_tickets RENAME CONSTRAINT pasajes_pkey TO bus_tickets_pkey;
ALTER TABLE bus_tickets RENAME CONSTRAINT pasajes_terminal_uuid_fkey TO bus_tickets_terminal_uuid_fkey;

ALTER INDEX IF EXISTS ix_pasajes_ticket RENAME TO ix_bus_tickets_ticket;
ALTER INDEX IF EXISTS ix_pasajes_terminal_uuid RENAME TO ix_bus_tickets_terminal_uuid;

-- PostgreSQL 18+ also stores NOT NULL constraints by name (pasajes_<column>_not_null);
-- older versions have none, so rename whatever still carries the old prefix.
DO $$
DECLARE
    c record;
BEGIN
    FOR c IN
        SELECT conname FROM pg_constraint
        WHERE conrelid = 'bus_tickets'::regclass AND conname LIKE 'pasajes\_%'
    LOOP
        EXECUTE format(
            'ALTER TABLE bus_tickets RENAME CONSTRAINT %I TO %I',
            c.conname, 'bus_tickets' || substr(c.conname, length('pasajes') + 1)
        );
    END LOOP;
END $$;
