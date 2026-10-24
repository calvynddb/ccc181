## Tsujie, the person waiting

> "The internet cafe that I go to, Arena, has times where its full so I either wait or mu uli, but more often than not kay mu uli nalang ko if feel nako dugay pa ma libre ang mga PC." *(English translation: "Arena, the internet cafe I go to, is sometimes full. I either wait or go home; more often, I just go home if I think it will take a while before any PCs become free.")* *(interview)*

| | |
| --- | --- |
| **Photo or sketch** | ![Stock photo representing Tsujie, a student using a laptop](screenshots/alex-shaw-lxKeLs3UTVo-unsplash.jpg) Photo by Alex Shaw, published September 20, 2020. Free to use under the [Unsplash License](https://unsplash.com/license). |
| **Age, role and background** | 20, 3rd-year Biology student majoring in Microbiology, and a regular at Arena internet cafe. She visits between classes and on free days. *(interview)* |
| **Goals** | Find an available PC without making an unnecessary trip; join the queue when all PCs are occupied; use her waiting time for schoolwork or another nearby activity. |
| **Frustrations** | She cannot tell remotely whether a PC is free; she may spend the effort and time travelling to Arena only to find it full; uncertainty about the wait makes her decide to go home instead. *(interview)* |
| **Devices and context** | She uses her phone while travelling between classes or while getting food nearby. She needs to check the queue remotely because the only current way to know about available PCs is to visit Arena or ask at the counter. *(observation)* |
| **Tech comfort** | High. Tsujie grew up with technology, is comfortable learning digital tools, and prefers digital solutions when they reduce uncertainty. |
| **Accessibility needs** | The app should work on a phone with readable text, clear status labels, and simple controls that are easy to use while walking or multitasking. It should also load reliably on mobile data. |

### Scenario

Tsujie finishes a class and considers going to Arena to use a PC. Before travelling, she opens Mito on her phone and checks how many PCs are open and when the count was last updated. When the cafe is full, she joins the queue for one PC with her nickname and sees her ticket number and place in line. She gets food nearby while waiting and returns when her status shows that her PC is ready.

### Top tasks in the app

| Task | Screen | Requirement ID |
| --- | --- | --- |
| Check the number of open PCs before travelling | Join | FR-03 |
| Join the queue for one PC using a nickname | Join | FR-01 |
| Check how many people are ahead and whether her ticket has been called | My place | FR-02 |

### What this means for my interface

1. Because Tsujie does not want to travel to a full cafe, the app must show the number of open PCs and when that count was last updated before she arrives.
2. Because she may wait somewhere else, her ticket status and position must be easy to find on My place.
3. Because she uses her phone between classes and while multitasking, the interface must be mobile-friendly, readable, and quick to use.

## Ethan, the staff member

> "Ang current system karon, ang mga tawo kay mu suroy ra sila kung naay bakante or mangutana sako diri sa counter kung may bakante. Pero usually, sila na mismo musuroy para mag-check kung may PC, tapos muhulat or muhawa kung wala pang available." *(English translation: "The current system has customers walking around to look for free PCs or asking me at the counter whether a PC is available. Usually, they check for themselves and wait or leave if none are free.")* *(interview)*

| | |
| --- | --- |
| **Photo or sketch** | ![Stock photo representing Ethan, an internet cafe staff member](screenshots/pj-go-1assCt31JVc-unsplash.jpg) Photo by Pj Go, published March 21, 2021. Free to use under the [Unsplash License](https://unsplash.com/license). |
| **Age, role and background** | Adult internet-cafe counter attendant who monitors PC availability and helps customers find or wait for open PCs. |
| **Goals** | Keep individual tickets in order; assign an open PC to the oldest waiting customer; keep station availability accurate so customers can check before travelling. |
| **Frustrations** | Customers have to roam around or ask at the counter to find free PCs; customers may wait in the wrong place or miss an opening; manually explaining availability takes attention away from monitoring the cafe. *(interview)* |
| **Devices and context** | He works at the counter and uses the computer that monitors the internet cafe while also watching PC availability and answering customer questions. *(observation)* |
| **Tech comfort** | Medium to high. Ethan already uses a computer to monitor the cafe and needs a queue tool that fits into that existing counter workflow. |
| **Accessibility needs** | The dashboard should use clear, high-contrast status labels, readable rows, and large action buttons so it can be scanned quickly from the counter. Important queue changes should not depend on color alone. |

### Scenario

Ethan monitors the PCs from the counter while customers walk around looking for open spots. When a PC becomes free or occupied, he updates that station in Mito. He checks the waiting list, assigns a free PC to the oldest waiting individual, and calls that ticket. He marks the customer as served after they take the PC, or records a no-show if they do not arrive.

### Top tasks in the app

| Task | Screen | Requirement ID |
| --- | --- | --- |
| Manually update which PCs are open so the displayed open-PC count stays accurate | Staff dashboard | FR-05 |
| See the individual waiting list in order and call the oldest ticket | Staff dashboard | FR-04 |
| Mark a ticket served or no-show | Staff dashboard | FR-04 |

### What this means for my interface

1. Because Ethan monitors the cafe while serving customers at the counter, the waiting list and free PC stations must be scannable at a glance.
2. Because PC availability changes as customers sit down or leave, the dashboard must let him update each station quickly so the open-PC count stays current.
3. Because customers may miss their call, the dashboard must provide clear actions for calling, serving, and marking a no-show.
