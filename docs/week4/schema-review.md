# Week 4 schema review

This is a static review of the ERD and schema against ten queue scenarios. It checks the documented data model and current Mito behavior; these scenarios were reasoned through, not executed as runtime tests.

## Ten scenarios

| # | Scenario | What the schema does | Hiccup or conclusion |
| --- | --- | --- | --- |
| 1 | A customer joins with a nickname and no phone number. | Creates a ticket with a generated ID, nickname, service, waiting status, and nullable phone/station. | Works. `phone` must stay nullable; the queue and ticket number come from the ticket row/ID. |
| 2 | A customer enters a valid phone number with spaces, parentheses, or a country prefix. | The check accepts the allowed punctuation and checks for 7–15 digits. | The previous `varchar(20)` could reject valid formatted input even when the digits were valid. Increase it to `varchar(32)` and keep browser and Flask length limits aligned at 32. |
| 3 | Two customers submit Join at nearly the same time. | Identity IDs remain unique, and ticket ID gives a stable order for subsequent reads. | Works for uniqueness and deterministic ordering. A sequence gap is normal; ID order represents database assignment order, not an exact measure of who clicked first over the network. |
| 4 | Staff deactivates a PC type with historical tickets and assigned PCs. | `services.active` changes while ticket and station FKs preserve their type references. | History remains readable and inactive types no longer appear on Join. Do not delete a type that still has tickets or stations. |
| 5 | Two staff actions try to call the next ticket using the same free PC. | The call must match the ticket's type to the station's type, then lock and update both records together. | A foreign key alone cannot ensure the PC is free or that its type matches. `Call next` filters stations by type and locks the station and ticket in one transaction. |
| 6 | A customer's hold expires, or staff calls them and their five-minute response window passes. | `held_until` and `hold_expired` record hold expiry; `called_at` and `claim_until` record the staff call and exact response deadline. | Keep the two cases distinct. The app must process expired deadlines and update the ticket/station transactionally; PostgreSQL does not change rows merely because a timestamp passed. Explain on My place that a missed call deadline makes the ticket no-show and releases the assigned PC. |
| 7 | A customer leaves, and staff later counts departures by day and service. | `left_at`, `status`, and `service_id` retain the facts needed for the report. | Group by the local Manila calendar date (`(left_at AT TIME ZONE 'Asia/Manila')::date`), not the server's implicit timezone, or departures near midnight can land on the wrong day. Keep `left` distinct from `no-show`. |
| 8 | Staff deletes a mistaken ticket, or someone attempts to delete its PC type/station. | FR-09 deletes the ticket row directly; `ON DELETE RESTRICT` protects PC types referenced by tickets or stations. | Matches the intended rules. Deleting the ticket is intentionally permanent; PC type and station history is protected from accidental cascade deletion. |
| 9 | A station is added without map coordinates, or with only one coordinate. | Nullable map fields allow no map data; pair/floor checks prevent a partial map location. | Works for the current scope. FR-10 is later/could; coordinate and floor fields do not create a usable map until map UI and data are added. |
| 10 | A customer has a long or indefinite PC session, so the next ticket's wait is unknown. | No expected-duration or wait-estimate field is stored. | Correctly avoids a misleading ETA because paid session time may be extended indefinitely. Current PC availability and queue position remain useful facts without promising a wait duration. |

## Works well / Problem / Change

### 1. Ticket identity and optional contact

- **Works well:** A generated ticket ID provides a simple visible number and stable queue ordering without a separate queue-position field. Nickname identifies the visit while phone remains optional.
- **Problem:** `varchar(20)` was too short for some formatted phone numbers that otherwise satisfy the accepted 7–15 digit rule.
- **Change:** Increase the database limit to 32 characters and align Flask and browser validation to that limit. Keep digits validation separate from display formatting.

### 2. Ticket-to-station assignment

- **Works well:** A nullable ticket station foreign key represents a waiting customer before PC assignment; a station type groups Standard and VIP PCs separately.
- **Problem:** A foreign key only proves that both rows exist. It does not prove the PC matches the ticket's requested type or remains free when staff calls.
- **Change:** Filter available stations by the ticket's PC type, then lock and recheck the selected station and next ticket before updating both in one transaction. Stations without a type cannot be assigned.

### 3. Holds and expiry

- **Works well:** `held_until` represents the 10-minute deadline, while ordering by ticket ID lets a resumed customer return to their original place without storing a mutable queue position.
- **Problem:** A timestamp alone does not explain why a ticket became a no-show. Without a persisted expiry reason, the expired-hold state can be lost across restart. A timestamp passing also does not automatically update a row.
- **Change:** Persist `hold_expired`, constrain it to no-show tickets, and make expiry processing part of queue reads or a scheduled app task. Keep the transition logic transactional.

### 4. Called-ticket deadline

- **Works well:** `called_at` already records when staff called a ticket, and the added `claim_until` preserves the exact five-minute deadline shown to the customer.
- **Problem:** Showing only “you were called” leaves Tsujie unsure how long she has to reach the PC or what happens if she is late. A duration calculated only from a configurable setting could also change after the call or a restart.
- **Change:** Store `claim_until` when staff calls the ticket, show the exact deadline and outcome on My place, and when it passes mark the ticket no-show and return its station to free. Keep the deadline in ticket history.

### 5. Departure reports

- **Works well:** `left_at` and `service_id` preserve enough facts to count departures without storing duplicated daily totals.
- **Problem:** A database session's timezone may not match the café's day boundary, which can miscount late-night departures.
- **Change:** Convert `left_at` to `Asia/Manila` before grouping by date. Keep the stored timestamp timezone-aware.

The Join form lists only active PC types, so customers choose Standard or VIP. The dashboard filters tickets by type and Call next only offers a free station of the ticket's selected type. Deactivation preserves existing ticket and station references.
