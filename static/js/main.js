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

const liveStatus = document.getElementById("live-status");
if (liveStatus) {
  const statusUrl = liveStatus.dataset.statusUrl;
  const statusBadge = document.getElementById("ticket-status");
  const position = document.getElementById("ticket-position");
  const leaveAction = document.getElementById("leave-action");
  const badgeClasses = {
    waiting: "text-bg-warning",
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
        position.textContent = `Your PC is ready${data.station_id ? `: ${data.station_id}` : ""}`;
      } else if (data.status === "served") {
        position.textContent = `Your session has started${data.station_id ? ` at ${data.station_id}` : ""}`;
      } else {
        position.textContent = "This ticket is no longer in the queue.";
      }

      if (leaveAction) {
        leaveAction.hidden = !["waiting", "called"].includes(data.status);
      }
    } catch (error) {
      console.warn("Could not refresh ticket status", error);
    }
  }

  refreshStatus();
  window.setInterval(refreshStatus, 10000);
}
