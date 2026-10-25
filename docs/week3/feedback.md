# Week 3 self-review

I reviewed the screens again from Tsujie's point of view while she is checking the queue away from Arena, and from Ethan's point of view while he is managing PCs at the counter. The main tasks are visible, but I can see that I tried to fit too many explanations and panels into the phone layouts. A queue also depends on live information, so a customer or staff member should not have to keep pressing a button to find out whether anything changed. My next pass should make the pages calmer and keep the current queue state fresh in the background.

## Join the queue — Tsujie (phone and laptop)

> **Works well:** I put the open-PC count and its last-updated time before the form. That gives Tsujie the information she needs before deciding whether to travel to Arena. The nickname is the main required detail, and the phone number is optional, so joining does not ask her for more information than the queue needs.
>
> **Problem:** I noticed that the page explains the staff process in more than one place. The availability card, the “How it works” panel, and the note near the Join button compete for space, especially on a phone. A manual refresh button would add another task for Tsujie and still make her responsible for checking whether the number changed. This breaks **visibility of system status** because the displayed update time can look current after the count has become stale. A zero count also needs to say clearly that she can still join, matching the language and choices in the real setting.
>
> **Change:** I marked the Refresh control for removal in both Join wireframes and noted that the open-PC count and timestamp should update automatically while the page is open. If an update fails, the last count should remain visible with a message that it could not be refreshed, so old information is not presented as current. I would keep one short explanation that staff assign a PC after she joins, remove the repeated process copy, and show “No PCs open — you can still join” when the count is zero. This keeps the choice clear without making the form longer.

## My place — Tsujie (phone and laptop)

> **Works well:** The ticket number, text status, and people ahead are the most prominent details. That matches Tsujie's need to check her place while she is away from the cafe. The 10-minute hold also gives her a way to pause without losing her original place when she cannot get to Arena right away.
>
> **Problem:** My on-hold screen repeats the hold explanation inside the status card, then repeats part of it in the staff note below. That is unnecessary reading at the moment Tsujie needs to know whether she should resume. This weakens **recognition rather than recall** because she has to sort through repeated wording to find the one action for her current state. I also need the called state to be unmistakable: if staff assigns a PC, a waiting message or a people-ahead count should not remain the main instruction. Clear state changes support **visibility of system status**.
>
> **Change:** I marked the Refresh control for removal in both My place wireframes and noted that the ticket status and position should update automatically while the page is open. Waiting should show the ticket and people ahead; on hold should show the expiry time and one Resume action; called should show the assigned PC and a clear instruction to go there. I would keep Leave the queue available but visually secondary to the action relevant to the current status.

## Staff dashboard — Ethan (phone and laptop)

> **Works well:** The queue is ordered, the PC stations have clear FREE/BUSY labels, and the next-ticket panel gives Ethan a direct way to assign a station and call the oldest waiting person. Keeping Serve and No-show with the called ticket also makes those actions easier to understand.
>
> **Problem:** The first phone version squeezed names, statuses, and actions into a table that was hard to scan. The later card layout is easier to read, but the dashboard still takes a lot of scrolling: Ethan moves between the next ticket, PC availability, and the rest of the queue. Some ticket details appear in both the next-ticket panel and the queue list. The counts and station states can also change while Ethan is looking at the page; asking him to press Refresh would add a step during a busy shift and weaken **visibility of system status**. Automatic updates must not unexpectedly reset his service filter, move keyboard focus, or erase a PC choice he has not submitted; preserving these controls supports **consistency** and **error prevention**.
>
> **Change:** I replaced the cramped phone table with ticket cards, moved the next action and PC availability ahead of the queue on phones, and kept one Call next control tied to the oldest waiting ticket. For a future pass, I would update the queue and station states in place without disturbing Ethan's selected filter, current focus, or an unsubmitted PC choice. I would also trim repeated ticket details so the most urgent action is easier to find. The laptop can keep its table because the wider screen makes the columns easier to compare.

## Main lesson

The red marks and captions on the Join and My place frames record proposed revisions from this review; the current app automatically updates My place, while Join availability and the Staff dashboard still need a future in-place update. My first instinct was to add more labels and instructions whenever a screen felt unclear. That helped explain the process, but it also made the phone pages longer and repeated information the customer had already read. I should make the system explain each state once, put the next useful action near it, and keep queue information current automatically. That would help Tsujie trust what she sees and let Ethan spend his attention on managing the actual PCs rather than refreshing or re-reading the dashboard.
