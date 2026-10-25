# Mito — Week 3 Interface Report

## Title details

- **App:** Mito
- **Setting:** Arena internet cafe, Tibanga
- **Name:** Calvyn Kent L. Adeva
- **Student ID:** 20240064
- **Section:** CS3B
- **Date:** October 25, 2026
- **Pull request:** [#2](https://github.com/calvynddb/ccc181/pull/2)

## Personas

- **Tsujie, person waiting:** Tsujie is a 20-year-old third-year Microbiology student and regular at Arena. She checks her phone between classes or while nearby, but cannot know whether a PC is free without visiting or asking at the counter. When the wait seems too long, she often goes home. Her top tasks are checking the open-PC count before travelling, joining for one PC with a nickname, and checking her ticket status and people ahead while she waits. Her interview quote was, “The internet cafe that I go to, Arena, has times where its full so I either wait or mu uli, but more often than not kay mu uli nalang ko if feel nako dugay pa ma libre ang mga PC.” *(English translation: “Arena, the internet cafe I go to, is sometimes full. I either wait or go home; more often, I just go home if I think it will take a while before any PCs become free.”)* See [the full persona](personas.md).
- **Ethan, staff member:** Ethan is an internet-cafe counter attendant who monitors the stations from a computer while answering customers. Customers currently walk around to find a free PC or ask him at the counter, which interrupts his other work. His top tasks are keeping PC availability accurate, calling the oldest waiting ticket, and marking that ticket served or no-show. His interview quote was, “Ang current system karon, ang mga tawo kay mu suroy ra sila kung naay bakante or mangutana sako diri sa counter kung may bakante. Pero usually, sila na mismo musuroy para mag-check kung may PC, tapos muhulat or muhawa kung wala pang available.” *(English translation: “The current system has customers walking around to look for free PCs or asking me at the counter whether a PC is available. Usually, they check for themselves and wait or leave if none are free.”)* See [the full persona](personas.md).

## Screens

The screenshots show the running app at phone and laptop widths. The phone captures were checked at 375 px by the user.

| Screenshot | Image | Persona and requirements |
| --- | --- | --- |
| Join — phone | ![Join the queue on a phone](screenshots/join-mobile.png) | Tsujie uses the phone screen to check open PCs and join the individual queue (FR-01, FR-03). |
| Join — laptop | ![Join the queue on a laptop](screenshots/join-laptop.png) | Tsujie uses the laptop screen to check open PCs and join the individual queue (FR-01, FR-03). |
| My place — phone | ![My place on a phone with the hold option](screenshots/my-place-waiting-with-hold-option.png) | Tsujie uses the phone screen to check her ticket status and place in line (FR-02). |
| My place — laptop | ![My place on a laptop](screenshots/my-place-laptop.png) | Tsujie uses the laptop screen to check her ticket status and place in line (FR-02). |
| Staff dashboard — phone | ![Staff dashboard on a phone](screenshots/staff-mobile.png) | Ethan uses the phone screen to view the queue in order, call and update tickets, and manually update PC availability so the open-PC count stays accurate (FR-04, FR-05). |
| Staff dashboard — laptop | ![Staff dashboard on a laptop](screenshots/staff-laptop.png) | Ethan uses the laptop screen to view the queue in order, call and update tickets, and manually update PC availability so the open-PC count stays accurate (FR-04, FR-05). |

The [earlier Staff phone screenshot](screenshots/staff-mobile-before.png) is retained as evidence of the navigation problem that led to the card layout.

## Design decisions

1. **Show PC availability before the Join form.** The page puts the open-PC count and its last-updated time before the form so Tsujie can decide whether travelling to Arena is worthwhile. A ticket is for one player and one PC; the nickname is required and the phone number is optional. I kept tickets individual after considering squad tickets: if a three-person squad reached the front when only one PC was free, staff could not serve the group yet, leaving the available PC unused and extending the group's wait. Individual tickets let staff assign each free PC to the oldest waiting person.
2. **Make My place useful while Tsujie waits away from Arena.** The ticket number, status, and people ahead are the main visual focus, and the page updates when staff call her. The tester's question about automatic assignment led me to state that staff update availability, assign a PC, and call the ticket; Mito does not assign PCs by itself. The 10-minute hold lets Tsujie pause without losing her original order while staff call other ready tickets. A hold does not reserve a PC and expires if she does not resume in time. The waiting and on-hold states are shown in the [usability-test screenshots](usability-test.md#improvement).
3. **Give Ethan one clear workflow for the queue and PC updates.** Staff see the queue in order, manually update station availability so the open-PC count stays accurate, assign a specific free PC to the oldest waiting ticket, then call that customer. I moved the Call next panel ahead of the queue on phones, replaced the cramped phone table with readable ticket cards, and kept Serve and No-show with the called ticket. This follows Ethan's counter workflow and the self-review finding that duplicate Call actions could lead to an out-of-order call or assignment.

## Self-review

The wireframe review found a separate problem on each screen. **Join:** the frames used inconsistent PC-availability wording, and the zero-PC state did not make clear whether customers could still join. I annotated both frames with consistent “Open PCs” wording, a zero-PC message that still invites joining, and automatic count and timestamp updates in place of the drawn Refresh control. **My place:** the frames showed only WAITING, so they did not show what happens after staff assign a PC and call the ticket. I annotated the called state to show the assigned PC ID and marked status and position updates as automatic. The tester later asked if the assignment was automatic, so I clarified that staff manage availability and assign PCs; this wording has not been retested. **Staff:** the phone table was cramped, station controls were separated from the queue, and the laptop repeated the Call action. I changed the phone frame to stacked ticket cards, showed PC states on the same screen, and kept one prominent Call next action with Serve and No-show tied to the called ticket. The updated frames and full Works well / Problem / Change reviews are in [feedback.md](feedback.md). Automatic Join availability and in-place Staff updates remain future work; the assignment's JavaScript requirement is met by the live My place updates.

## Accessibility

The source review added 44 px minimum button heights and kept field errors in text. Mobile Lighthouse scores are Join 98 Performance / 95 Accessibility, My place 98 / 94, and Staff 98 / 95; all three show 100 Best Practices and 90 SEO. See the [Join](screenshots/lighthouse-mobile-join.png), [My place](screenshots/lighthouse-mobile-my-place.png), and [Staff](screenshots/lighthouse-mobile-staff.png) captures. The user reports that performance stayed the same, the keyboard-only flow passed, and the three queue screens work at 375 px. The shared layout has a skip link that appears on keyboard focus and a visible focus outline. A small overflow visible on the [welcome-page phone capture](screenshots/base-mobile-before.png) was corrected by reducing its grid gutter; confirm with a fresh capture. See [the accessibility notes](accessibility.md).

## Usability test

An anonymous tester who was not a CCC181 classmate tried Mito on the laptop I provided on October 25, 2026, and completed all three tasks. The same tester acted as Ethan for the staff task when I asked them to. In that session, joining took 7.64 seconds, identifying the ticket number and people ahead took 2.62 seconds, and calling and serving took 5.7 seconds. During the join task, the tester asked whether a PC is assigned automatically. I clarified that staff update PC availability, assign a PC, and call the next ticket. This wording change has not been retested. The larger interface improvement was the 10-minute hold: Tsujie can join while at school, pause without losing her original place, and resume before the hold expires. The [usability record](usability-test.md) includes its before-and-after screenshots and the task observations.

## Reflection

The hardest part was making the queue and PC availability work as one clear process. A ticket could not simply be called because it was next; staff first had to know which PC was actually free and assign that specific station. Keeping this consistent across joining, holding, calling, leaving, and serving took the most adjustment.

### Week 4 direction

When staff call a customer and assign a PC, My place should show a simple Arena map with that PC highlighted. The map should identify whether the station is on the first or second floor and show its position relative to nearby PCs. The station ID and floor should also appear in text, so customers can use the location information without relying on the visual highlight alone.

I also want to remove the manual-refresh burden from the other live screens. Join should update the open-PC count and its last-updated time automatically while the page is open, and Staff should update queue counts and PC availability in place. Those updates need to preserve a staff member's service filter, keyboard focus, and any PC selection they have not submitted. The Week 3 assignment only required automatic updates on My place, so these are follow-on improvements rather than missing Week 3 requirements.

Before Mito is used beyond this prototype, I also need to restrict the staff dashboard, which currently has no login, and move the Flask secret out of the source code. I will check that station availability, ticket status, hold expiry, and the displayed queue position still agree after these changes, then repeat the phone and keyboard checks on the updated screens.

## Declaration

Claude Code helped me think through the queue model. I first considered squad tickets, then considered what would happen if a three-person squad reached the front while only one PC became free. I chose individual tickets after comparing that case with the one-PC ticket requirement and the staff workflow in my proposal.

ChatGPT Codex helped me troubleshoot Flask implementation errors I encountered while building the app. For each suggested fix, I retraced the affected code and the steps that led to the error so I could understand what I had done wrong and how the fix addressed it. I then ran Mito locally, repeated the Join, My place, and Staff flows, and compared their behavior with FR-01 through FR-05 and the queue process I intended for Arena.
