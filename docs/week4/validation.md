# Week 4 validation

## Browser and Flask checks

The Join form requires a nickname and service, limits the nickname to 24 characters, and keeps the phone optional with a 32-character maximum. I removed `novalidate` so the browser can enforce the required fields and length attributes. Flask was also tested directly with `curl.exe`, bypassing those browser checks.

| Rule | Layer | How I tested it | What happened |
| --- | --- | --- | --- |
| Nickname is required | Browser | Checked the Join form's `required` attribute with native validation enabled | An empty nickname is blocked before the browser submits the form. |
| Nickname cannot exceed 24 characters | Flask | `curl.exe` POST with a 25-character nickname and `service_id=1` | HTTP 400; no ticket was added. |
| Nickname cannot be blank | Flask | `curl.exe` POST with `nickname=` and `service_id=1` | HTTP 400; no ticket was added. |
| Service must exist | Flask | `curl.exe` POST with a valid nickname and nonexistent `service_id=999999` | HTTP 400; no ticket was added. |

Ticket count was 2 before and after all three Flask requests. The requests used the Join route without relying on browser validation.

These checks cover NFR-06: invalid Join submissions receive HTTP 400 without adding a ticket, and PostgreSQL constraints reject invalid ticket data. The browser enforces required Join fields and input lengths; Flask checks the full nickname and phone rules.

## PostgreSQL checks

Each invalid statement was run separately against the running PostgreSQL container. PostgreSQL rejected every statement with the following errors:

| Constraint | How I tested it | PostgreSQL error |
| --- | --- | --- |
| FOREIGN KEY | `INSERT INTO tickets (nickname, service_id) VALUES ('Bad FK', 999999);` | `ERROR: insert or update on table "tickets" violates foreign key constraint "tickets_service_id_fkey"` |
| UNIQUE | `INSERT INTO services (name) VALUES ('PC session');` | `ERROR: duplicate key value violates unique constraint "services_name_key"` |
| CHECK | `UPDATE tickets SET status = 'lost' WHERE id = 1;` | `ERROR: new row for relation "tickets" violates check constraint "ck_tickets_status"` |
| NOT NULL | `INSERT INTO tickets (nickname, service_id) VALUES (NULL, 1);` | `ERROR: null value in column "nickname" of relation "tickets" violates not-null constraint` |
| RESTRICT | `DELETE FROM services WHERE id = 1;` | `ERROR: update or delete on table "services" violates foreign key constraint "tickets_service_id_fkey" on table "tickets"` |

I also inserted one valid ticket inside a transaction and rolled it back. PostgreSQL returned an ID, the default `waiting` status, and a generated `created_at`; the rollback left the saved queue unchanged.

## SQL construction check

Ran the assignment's `git grep -nE 'f["''].*(SELECT|INSERT|UPDATE|DELETE)' -- '*.py'` check. It returned no matches; Mito uses SQLAlchemy ORM statements rather than interpolating user input into SQL strings.
