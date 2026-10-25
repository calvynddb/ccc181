"""Mito: a simple queue for individual PC sessions at Arena in Tibanga."""

from datetime import datetime, timedelta
import re
import sys

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

if sys.version_info.releaselevel != "final":
    raise RuntimeError(
        "Mito requires a stable Python release. This project is pinned to Python 3.13.12; "
        f"the active interpreter is {sys.version.split()[0]}. Select the workspace .venv interpreter."
    )
if sys.version_info < (3, 11):
    raise RuntimeError("Mito requires Python 3.11 or newer.")

app = Flask(__name__)
app.secret_key = "dev-only-change-me"

SERVICES = [{"id": 1, "name": "PC session"}]

STATIONS = [
    {"id": "PC-01", "status": "free"},
    {"id": "PC-02", "status": "busy"},
    {"id": "PC-03", "status": "free"},
    {"id": "PC-04", "status": "free"},
]
AVAILABILITY_UPDATED_AT = datetime.now().astimezone()

TICKETS = [
    {
        "number": 1,
        "nickname": "Ana",
        "phone": None,
        "service_id": 1,
        "status": "waiting",
        "station_id": None,
        "held_until": None,
        "hold_expired": False,
    },
    {
        "number": 2,
        "nickname": "Ben",
        "phone": None,
        "service_id": 1,
        "status": "waiting",
        "station_id": None,
        "held_until": None,
        "hold_expired": False,
    },
]

HOLD_DURATION = timedelta(minutes=10)


@app.before_request
def expire_ticket_holds():
    now = datetime.now().astimezone()
    for ticket in TICKETS:
        if (ticket["status"] == "on-hold" and ticket["held_until"]
                and ticket["held_until"] <= now):
            ticket["status"] = "no-show"
            ticket["held_until"] = None
            ticket["hold_expired"] = True


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/join")
def join_form():
    return render_template(
        "join.html",
        open_pcs=sum(station["status"] == "free" for station in STATIONS),
        station_count=len(STATIONS),
        updated_at=AVAILABILITY_UPDATED_AT,
        form={},
        errors={},
    )


@app.post("/join")
def join():
    form = request.form
    nickname = form.get("nickname", "").strip()
    phone = form.get("phone", "").strip()
    errors = {}

    if not nickname:
        errors["nickname"] = "Enter a nickname."
    elif len(nickname) > 24:
        errors["nickname"] = "Use 24 characters or fewer."

    if phone:
        digits = re.sub(r"\D", "", phone)
        if not re.fullmatch(r"[0-9+() .-]+", phone) or not 7 <= len(digits) <= 15:
            errors["phone"] = "Enter a valid phone number, or leave this optional field blank."

    if errors:
        flash("Please fix the highlighted fields.", "danger")
        return (
            render_template(
                "join.html",
                open_pcs=sum(station["status"] == "free" for station in STATIONS),
                station_count=len(STATIONS),
                updated_at=AVAILABILITY_UPDATED_AT,
                form=form,
                errors=errors,
            ),
            400,
        )

    number = max((ticket["number"] for ticket in TICKETS), default=0) + 1
    TICKETS.append(
        {
            "number": number,
            "nickname": nickname,
            "phone": phone or None,
            "service_id": SERVICES[0]["id"],
            "status": "waiting",
            "station_id": None,
            "held_until": None,
            "hold_expired": False,
        }
    )
    session["current_ticket_id"] = number
    flash(f"You joined the queue. Your ticket is #{number}.", "success")
    return redirect(url_for("ticket", ticket_id=number))


@app.get("/staff")
def staff_dashboard():
    service_id = request.args.get("service_id", type=int)
    valid_service_ids = {service["id"] for service in SERVICES}
    if service_id not in valid_service_ids:
        service_id = None

    queue = [
        ticket
        for ticket in TICKETS
        if ticket["status"] in ("waiting", "called", "on-hold")
        and (service_id is None or ticket["service_id"] == service_id)
    ]
    queue.sort(key=lambda ticket: ticket["number"])
    names = {service["id"]: service["name"] for service in SERVICES}
    next_ticket = next((ticket for ticket in queue if ticket["status"] == "waiting"), None)
    free_stations = [station for station in STATIONS if station["status"] == "free"]
    return render_template(
        "staff.html",
        queue=queue,
        services=SERVICES,
        names=names,
        selected=service_id,
        next_ticket=next_ticket,
        free_stations=free_stations,
        stations=STATIONS,
        open_pcs=len(free_stations),
        waiting_count=sum(ticket["status"] == "waiting" for ticket in queue),
        called_count=sum(ticket["status"] == "called" for ticket in queue),
        held_count=sum(ticket["status"] == "on-hold" for ticket in queue),
        updated_at=AVAILABILITY_UPDATED_AT,
    )


@app.post("/staff/call-next")
def call_next():
    service_id = request.form.get("service_id", type=int)
    if service_id not in {service["id"] for service in SERVICES}:
        service_id = SERVICES[0]["id"]
    station_id = request.form.get("station_id", "")
    station = next((item for item in STATIONS if item["id"] == station_id), None)
    next_ticket = next(
        (
            ticket
            for ticket in sorted(TICKETS, key=lambda item: item["number"])
            if ticket["status"] == "waiting" and ticket["service_id"] == service_id
        ),
        None,
    )
    if next_ticket is None:
        flash("There are no waiting tickets for this service.", "info")
    elif station is None or station["status"] != "free":
        flash("Choose a PC that is currently open.", "warning")
    else:
        next_ticket["status"] = "called"
        next_ticket["station_id"] = station["id"]
        station["status"] = "busy"
        global AVAILABILITY_UPDATED_AT
        AVAILABILITY_UPDATED_AT = datetime.now().astimezone()
        flash(f"Ticket #{next_ticket['number']} called to {station['id']}.", "success")
    return redirect(url_for("staff_dashboard", service_id=service_id))


@app.post("/staff/stations/<station_id>/toggle")
def toggle_station(station_id):
    station = next((item for item in STATIONS if item["id"] == station_id), None)
    if station is None:
        abort(404)
    station["status"] = "busy" if station["status"] == "free" else "free"
    global AVAILABILITY_UPDATED_AT
    AVAILABILITY_UPDATED_AT = datetime.now().astimezone()
    flash(f"{station['id']} marked {station['status']}.", "info")
    return redirect(url_for("staff_dashboard"))


@app.post("/staff/tickets/<int:ticket_id>/<action>")
def staff_action(ticket_id, action):
    ticket = next((item for item in TICKETS if item["number"] == ticket_id), None)
    if ticket is None or action not in ("serve", "no-show"):
        abort(404)

    service_id = request.form.get("service_id", type=int)
    if action == "serve" and ticket["status"] != "called":
        flash(f"Call ticket #{ticket_id} before marking it served.", "warning")
    elif action == "no-show" and ticket["status"] not in ("waiting", "called", "on-hold"):
        flash(f"Ticket #{ticket_id} is already {ticket['status']}.", "info")
    else:
        ticket["status"] = "served" if action == "serve" else "no-show"
        ticket["held_until"] = None
        if action == "no-show" and ticket["station_id"]:
            station = next(
                (item for item in STATIONS if item["id"] == ticket["station_id"]), None
            )
            if station:
                station["status"] = "free"
                global AVAILABILITY_UPDATED_AT
                AVAILABILITY_UPDATED_AT = datetime.now().astimezone()
        flash(f"Ticket #{ticket_id} marked {ticket['status']}.", "info")
    return redirect(url_for("staff_dashboard", service_id=service_id))


@app.route("/queue/<int:ticket_id>")
def ticket(ticket_id):
    current_ticket = next(
        (ticket for ticket in TICKETS if ticket["number"] == ticket_id), None
    )
    if current_ticket is None:
        abort(404)

    ahead = sum(
        1
        for other in TICKETS
        if other["service_id"] == current_ticket["service_id"]
        and other["status"] == "waiting"
        and other["number"] < current_ticket["number"]
    )
    service = next(
        service for service in SERVICES if service["id"] == current_ticket["service_id"]
    )
    return render_template(
        "ticket.html",
        ticket=current_ticket,
        service=service,
        ahead=ahead,
        status_classes={
            "waiting": "text-bg-warning",
            "on-hold": "text-bg-info",
            "called": "text-bg-success",
            "served": "text-bg-secondary",
            "no-show": "text-bg-danger",
        },
        held_until=current_ticket["held_until"].strftime("%I:%M %p") if current_ticket["held_until"] else None,
        hold_expired=current_ticket["hold_expired"],
    )


@app.post("/queue/<int:ticket_id>/leave")
def leave_queue(ticket_id):
    current_ticket = next(
        (ticket for ticket in TICKETS if ticket["number"] == ticket_id), None
    )
    if current_ticket is None:
        abort(404)
    if current_ticket["status"] in ("waiting", "called", "on-hold"):
        if current_ticket["status"] == "called" and current_ticket["station_id"]:
            station = next(
                (item for item in STATIONS if item["id"] == current_ticket["station_id"]),
                None,
            )
            if station:
                station["status"] = "free"
                global AVAILABILITY_UPDATED_AT
                AVAILABILITY_UPDATED_AT = datetime.now().astimezone()
        current_ticket["status"] = "no-show"
        current_ticket["held_until"] = None
        flash(f"Ticket #{ticket_id} has left the queue.", "info")
    else:
        flash(f"Ticket #{ticket_id} is already {current_ticket['status']}.", "info")
    if session.get("current_ticket_id") == ticket_id:
        session.pop("current_ticket_id", None)
    return redirect(url_for("index"))


@app.post("/queue/<int:ticket_id>/hold")
def hold_queue_place(ticket_id):
    current_ticket = next((item for item in TICKETS if item["number"] == ticket_id), None)
    if current_ticket is None:
        abort(404)
    if current_ticket["status"] == "waiting":
        current_ticket["status"] = "on-hold"
        current_ticket["held_until"] = datetime.now().astimezone() + HOLD_DURATION
        flash("Your place is on hold for 10 minutes. Resume before it expires to keep your ticket order.", "info")
    else:
        flash("Only a waiting ticket can be put on hold.", "warning")
    return redirect(url_for("ticket", ticket_id=ticket_id))


@app.post("/queue/<int:ticket_id>/resume")
def resume_queue_place(ticket_id):
    current_ticket = next((item for item in TICKETS if item["number"] == ticket_id), None)
    if current_ticket is None:
        abort(404)
    if current_ticket["status"] == "on-hold":
        current_ticket["status"] = "waiting"
        current_ticket["held_until"] = None
        flash("Your place is back in the queue in its original ticket order.", "success")
    else:
        flash("This ticket is no longer on hold.", "info")
    return redirect(url_for("ticket", ticket_id=ticket_id))


@app.get("/queue/<int:ticket_id>/status.json")
def ticket_status(ticket_id):
    current_ticket = next(
        (ticket for ticket in TICKETS if ticket["number"] == ticket_id), None
    )
    if current_ticket is None:
        abort(404)
    ahead = sum(
        1
        for other in TICKETS
        if other["service_id"] == current_ticket["service_id"]
        and other["status"] == "waiting"
        and other["number"] < current_ticket["number"]
    )
    return {
        "status": current_ticket["status"],
        "ahead": ahead,
        "station_id": current_ticket["station_id"],
        "held_until": current_ticket["held_until"].strftime("%I:%M %p") if current_ticket["held_until"] else None,
        "hold_expired": current_ticket["hold_expired"],
    }


if __name__ == "__main__":
    app.run(debug=True)
