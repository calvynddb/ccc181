# Accessibility check

## Lighthouse

Scores below were transcribed from the supplied Chrome Lighthouse mobile screenshots. Lighthouse displays Performance, Accessibility, Best Practices, and SEO scores; “Mobile” is the audit form factor, not a separate score. The user reports that performance stayed the same after the Staff layout change; the original score panel is retained as the evidence.

| Screen | Performance | Accessibility | Best Practices | SEO | Evidence |
| --- | ---: | ---: | ---: | ---: | --- |
| Join | 98 | 95 | 100 | 90 | [Mobile Lighthouse screenshot](screenshots/lighthouse-mobile-join.png) |
| My place | 98 | 94 | 100 | 90 | [Mobile Lighthouse screenshot](screenshots/lighthouse-mobile-my-place.png) |
| Staff | 98 | 95 | 100 | 90 | [Mobile Lighthouse screenshot](screenshots/lighthouse-mobile-staff.png) |
| Welcome page (additional) | 97 | 94 | 100 | 90 | [Mobile Lighthouse screenshot](screenshots/lighthouse-mobile-home.png) |

## Keyboard-only check

The user reports that the keyboard-only flow passed and no failures were found. In the usual keyboard flow, Tab moves through the page controls in reading order, a visible outline marks the focused control, Enter activates links, and Enter or Space activates buttons. Mito's shared layout provides a skip link as the first keyboard stop; it becomes visible on focus and jumps past the navigation to the main content. The source also adds a clear focus outline. These notes describe the expected/source-reviewed behavior; the user did not report a separate focus-by-focus observation.

## Manual checklist

The user checked the three queue screens at 375 px. The checklist below combines source review with the user's browser check; the welcome-page gutter correction has not yet been recaptured.

| Check | Join | My place | Staff |
| --- | --- | --- | --- |
| Every input has a visible label | ✅ Nickname and phone | ✅ No input fields | ✅ Service filter and PC assignment |
| Error messages say what to do, in text | ✅ Nickname and phone errors | ✅ No form errors on this screen | ✅ Staff actions give text feedback |
| Status is shown in words, not only color | ✅ Availability is text | ✅ Ticket status is text | ✅ Ticket and station status is text |
| Text and buttons are readable at 375 px with no sideways page scroll | ✅ User checked at 375 px | ✅ User checked at 375 px | ✅ User checked at 375 px; narrow-screen cards shown in screenshot |
| Buttons are at least about 44 × 44 px on a phone | ✅ Buttons have 44 px minimum height | ✅ Leave button has 44 px minimum height | ✅ Buttons have 44 px minimum height; station controls are larger |
| Page has one `<h1>` and headings in order | ✅ Source review | ✅ Source review | ✅ Source review |
| `<html lang="en">` is set | ✅ Shared layout | ✅ Shared layout | ✅ Shared layout |

## Fixes from source review

- Added a 44 px minimum height to Bootstrap buttons and larger touch targets for PC station controls.
- Kept textual labels beside status colors and gave the ticket status region `aria-live="polite"` for automatic updates.
- Kept the staff table inside Bootstrap's horizontally scrollable `.table-responsive` wrapper.
- Replaced the cramped Staff table with stacked ticket cards below laptop width and moved the Call next panel before the queue on phone screens. The updated Staff phone screenshot shows the revised layout.
- The [welcome-page phone capture before the gutter fix](screenshots/base-mobile-before.png) showed horizontal overflow; reduced the small-screen grid gutter. A fresh welcome-page capture is still needed to confirm the fix.
