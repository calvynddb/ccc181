const joinForm = document.getElementById("join-form");
if (joinForm) {
  joinForm.addEventListener("submit", () => {
    const button = joinForm.querySelector("button[type=submit]");
    if (button) {
      button.disabled = true;
      button.textContent = "Getting your ticket…";
    }
  });
}

document.querySelectorAll("form[data-confirm]").forEach((form) => {
  form.addEventListener("submit", (event) => {
    if (!confirm(form.dataset.confirm)) event.preventDefault();
  });
});

const liveStatus = document.getElementById("live-status");
if (liveStatus) {
  const statusUrl = liveStatus.dataset.statusUrl;
  const statusBadge = document.getElementById("ticket-status");
  const position = document.getElementById("ticket-position");
  const leaveAction = document.getElementById("leave-action");
  const holdAction = document.getElementById("hold-action");
  const resumeAction = document.getElementById("resume-action");
  const holdNote = document.getElementById("hold-note");
  const queueNote = document.getElementById("queue-note");
  const badgeClasses = {
    waiting: "text-bg-warning",
    "on-hold": "text-bg-info",
    called: "text-bg-success",
    served: "text-bg-secondary",
    "no-show": "text-bg-danger",
  };

  async function refreshStatus() {
    try {
      const response = await fetch(statusUrl, { headers: { Accept: "application/json" } });
      if (!response.ok) return;
      const data = await response.json();

      statusBadge.textContent = data.status;
      Object.values(badgeClasses).forEach((className) => statusBadge.classList.remove(className));
      statusBadge.classList.add(badgeClasses[data.status] || "text-bg-secondary");

      if (data.status === "waiting") {
        position.textContent = data.ahead === 0
          ? "You're next!"
          : `${data.ahead} ${data.ahead === 1 ? "person" : "people"} ahead of you`;
      } else if (data.status === "called") {
        position.textContent = `Your PC is ready${data.station_id ? `: ${data.station_id}` : ""}. Please arrive by ${data.claim_until}. If you miss this deadline, your ticket becomes no-show and the PC is released.`;
      } else if (data.status === "on-hold") {
        position.textContent = `Your place is on hold until ${data.held_until}.`;
      } else if (data.status === "served") {
        position.textContent = `Your session has started${data.station_id ? ` at ${data.station_id}` : ""}`;
      } else {
        if (data.hold_expired) {
          position.textContent = "Your 10-minute hold expired. Join again when you're ready.";
        } else if (data.was_called) {
          position.textContent = "Your response deadline passed or staff marked this ticket no-show. The assigned PC has been released.";
        } else {
          position.textContent = "This ticket is no longer in the queue.";
        }
      }

      if (leaveAction) {
        leaveAction.hidden = !["waiting", "called", "on-hold"].includes(data.status);
      }
      if (holdAction) holdAction.hidden = data.status !== "waiting";
      if (resumeAction) resumeAction.hidden = data.status !== "on-hold";
      if (holdNote) holdNote.hidden = data.status !== "on-hold";
      if (queueNote) queueNote.hidden = data.status === "on-hold";
    } catch (error) {
      console.warn("Could not refresh ticket status", error);
    }
  }

  refreshStatus();
  window.setInterval(refreshStatus, 10000);
}
