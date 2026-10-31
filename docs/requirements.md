# Mito requirements

**Setting:** Internet cafés such as Arena.
**People who wait:** Customers such as [Tsujie](week3/personas.md#tsujie-the-person-waiting), who want to check PC availability and follow their place in line.
**People who serve:** Staff such as [Ethan](week3/personas.md#ethan-the-staff-member), who update PC availability, assign stations and manage the queue.

**Problem statement:** Internet-café customers need to check whether a PC is open and follow their place in the queue without standing at the counter, because staff manually manage station availability and call each customer when a PC is assigned.

## Functional requirements

★ marks a requirement specific to the internet-café setting. “Stores data?” means the app must remember the information after Flask and PostgreSQL restart.

| ID | Requirement | Priority | Stores data? | Status |
| --- | --- | --- | --- | --- |
| FR-01 ★ | A customer can join the queue for one PC session using a nickname and an optional phone number. | Must | Yes | Built (Week 3) |
| FR-02 | A customer can see their ticket number, current status and number of waiting tickets ahead of them. | Must | Yes | Built (Week 3) |
| FR-03 ★ | A customer can see how many PCs are open and when that availability was last updated. | Must | Yes | Built (Week 3) |
| FR-04 ★ | Staff can view tickets in order, assign an open PC to the oldest waiting customer, call that customer, and mark a called ticket served or no-show. | Must | Yes | Built (Week 3) |
| FR-05 ★ | Staff can mark each PC free or busy, and Mito calculates the open-PC count from those station states. | Must | Yes | Built (Week 3) |
| FR-06 ★ | A customer with a waiting ticket can hold their place for 10 minutes and resume in their original ticket order before the hold expires. | Must | Yes | Built (Week 3) |
| FR-07 | A customer can leave the queue, and their ticket is removed from the active queue while its departure status is retained. | Must | Yes | Built (Week 3) |
| FR-08 ★ | Staff can add and rename a queue service and deactivate it when it is no longer offered. | Must | Yes | This week |
| FR-09 | Staff can permanently delete a ticket that was created by mistake. | Must | Yes | This week |
| FR-10 ★ | When staff call a customer, My place can show the assigned PC highlighted on a floor map with its floor and position relative to nearby PCs. | Could | Yes | Later |
| FR-11 | A customer viewing Join sees PC availability and its last-updated time refresh automatically while the page is open. | Should | No | Later |
| FR-12 | Staff see queue and PC availability updates automatically while the dashboard is open, without losing their service filter or an unsubmitted PC selection. | Should | No | Later |
| FR-13 | Staff can review how many customers leave before being served, grouped by service and day. | Could | Yes | Later |
| FR-14 ★ | Before deciding to come to the café, a customer can see a clearly labeled rough wait estimate. | Won't (this semester) | No | Dropped |
| FR-15 ★ | After staff assigns a PC and calls a customer, My place shows the exact five-minute response deadline and explains that missing it changes the ticket to no-show and releases the PC. | Should | Yes | This week |
| FR-16 ★ | Staff can add a PC station with a unique PC ID, and Mito includes it in the availability count and dashboard. | Should | Yes | This week |

FR-15 is a Week 4 addition to make the call outcome clearer for customers who may be away from the café. It has not yet been checked with the person who reviewed the original requirements. The five-minute duration follows the existing Mito design draft; the current Flask implementation does not yet enforce a call deadline.

## Non-functional requirements

| ID | Requirement | Category | Priority |
| --- | --- | --- | --- |
| NFR-01 | A ticket, its status and its queue order remain available after restarting Flask and PostgreSQL. | Reliability | Must |
| NFR-02 | Two customers joining at the same time cannot receive the same ticket number. | Data integrity | Must |
| NFR-03 | No database password or Flask secret key is tracked in Git. | Security | Must |
| NFR-04 | At 375px viewport width, Join, My place and Staff have no horizontal page scrolling. | Responsive design | Should |
| NFR-05 | A keyboard-only user can complete Join and the Staff filter, Call next and Serve flow with visible keyboard focus. | Accessibility | Must |
| NFR-06 | Invalid nickname, phone, ticket status and station data are rejected at the browser, Flask and database layers. | Data integrity | Must |

## MVP

**MVP:** FR-01 through FR-09 and NFR-01 through NFR-03, plus NFR-05 and NFR-06. These cover joining and tracking an individual ticket, staff-managed PCs and queue actions, the service data needed by the app, and reliable storage. FR-10 through FR-13 are planned improvements rather than requirements for the Week 4 MVP. FR-14 is dropped because Mito cannot make a credible wait-time estimate from the information the café tracks.

**Out of scope:** Customer accounts and online payments are out of scope because Mito only needs a nickname and optional phone number to manage the queue. Automatic PC detection and automatic PC assignment are also out of scope because staff at the café determine which stations are actually available and assign a specific PC before calling a customer. Staff login is deferred to the later security work identified in the Week 4 assignment.

## Requirements check with a person from the setting

**Status:** Feedback recorded from an internet-café customer represented by the Tsujie persona. **Review date:** October 30, 2026, 5:00 PM (Asia/Manila). The approximate review duration has not been recorded.

### Summary of Tsujie's feedback

**1. Is anything missing that you would need?** She would prefer a rough wait estimate before deciding whether to come over. I considered FR-14, then marked it Dropped after reviewing how the café works: customers can extend purchased credits or hours indefinitely, so Mito cannot know when an occupied PC will become free. A numeric estimate would be unreliable. The app will show current open-PC availability and ticket position instead.

**2. Is anything here wrong, or not important to you?** She does not need a PC map because the PCs are clearly labeled inside the café. She would rather use the app to see whether PCs are free and join the queue. I lowered FR-10 from Should to Could and kept it marked Later.

**3. Which three matter most to you?** Her top three are seeing how many PCs are open (FR-03), seeing her ticket number and status (FR-02), and being able to hold her place while she is at campus (FR-06).

| Who (role only, no full name) | What they said | What I changed |
| --- | --- | --- |
| Internet-café customer | Preferred a rough wait estimate before coming; said the map is unnecessary because PCs are clearly labeled in the café; prioritized open PCs, ticket number/status, and holding a place from campus. | Considered FR-14, then marked it Dropped because session duration can be extended indefinitely and a numeric estimate would be unreliable. Lowered FR-10 to Could/Later and recorded FR-03, FR-02 and FR-06 as the top priorities. |
