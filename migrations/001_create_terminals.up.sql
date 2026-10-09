-- Moves terminal names out of pasajes into their own table and links
-- each bus ticket to its terminal through a foreign key.
BEGIN;

CREATE TABLE terminals (
    uuid VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

INSERT INTO terminals (uuid, name)
SELECT gen_random_uuid()::text, name
FROM (SELECT DISTINCT trim(bus_terminal_name) AS name FROM pasajes) t;

ALTER TABLE pasajes ADD COLUMN terminal_uuid VARCHAR(36);

UPDATE pasajes p
SET terminal_uuid = t.uuid
FROM terminals t
WHERE t.name = trim(p.bus_terminal_name);

ALTER TABLE pasajes
    ALTER COLUMN terminal_uuid SET NOT NULL,
    ADD CONSTRAINT pasajes_terminal_uuid_fkey
        FOREIGN KEY (terminal_uuid) REFERENCES terminals (uuid);

CREATE INDEX ix_pasajes_terminal_uuid ON pasajes (terminal_uuid);

ALTER TABLE pasajes DROP COLUMN bus_terminal_name;

COMMIT;
