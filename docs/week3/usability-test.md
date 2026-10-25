# Week 3 usability test

## Session

- **Date:** October 25, 2026
- **Device:** Laptop
- **Tester:** Anonymous; no name or face recorded
- **Persona match:** The tester resembled Tsujie; the observer took Ethan's staff role
- **Build:** Exact commit not recorded. The test happened before the workflow clarification below was added.
- **Timing:** The owner later timed each task during a follow-up run; times below are single-run observations, not averages.

## Tasks and observations

| Task | Result | Time | Observation |
| --- | --- | --- | --- |
| Join the queue for one PC session | With clarification; completed | 7.64 seconds | Time depends on how long the nickname is, whether the tester enters the optional phone number from memory, and whether they are in a rush. Tester asked whether a PC would be assigned automatically after joining. The flow depends on staff at Arena updating PC availability and manually assigning an open PC before calling the ticket. |
| Find the ticket number and people ahead | Completed | 2.62 seconds | The ticket number and people ahead were front and center; Tsujie noticed and identified them directly. |
| Call the next ticket and mark it served | Completed | 5.7 seconds | About two deliberate clicks, with a double-check before acting rather than mindless clicking. |

## Design rule check

- Tsujie's rule to make her ticket position easy to find held up; the tester completed the ticket check. Task-specific observations were not recorded.
- Ethan's rule to show station availability and provide a clear call action held up, but the customer side did not explain clearly enough that a person at Arena updates stations and assigns PCs.

## Improvement

- **Problem:** Tsujie may join while she is still at school, but does not want to rush when staff call her while she is not yet at Arena. Leaving the queue would make her lose her place.
- **Fix:** Added a 10-minute hold and resume action. While a ticket is on hold, staff can call other ready tickets; resuming before expiry restores the ticket's original order. A hold does not reserve a PC.
- **Before:** The waiting ticket has no way to pause and keep its place.

  ![My place before the hold option](screenshots/my-place-mobile.png)

- **After:** My place offers a 10-minute hold and shows the expiry time and resume action.

  ![My place while the ticket is on hold](screenshots/my-place-on-hold.png)

### PC-assignment clarification

The tester also asked whether a PC would be assigned automatically after joining. I clarified that staff at Arena update which PCs are free, assign one to the oldest waiting ticket, and call that customer. I then made that workflow explicit on Join, My place, and Staff. The tester did not retest this wording change, so I have not recorded it as a verified usability improvement.
