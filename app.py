"""Mito: a simple queue for individual PC sessions at Arena in Tibanga."""

from datetime import datetime
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
    },
    {
        "number": 2,
        "nickname": "Ben",
        "phone": None,
        "service_id": 1,
        "status": "waiting",
        "station_id": None,
    },
]


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
        }
    )
    session["current_ticket_id"] = number
    flash(f"You joined the queue. Your ticket is #{number}.", "success")
    return redirect(url_for("ticket", ticket_id=number))


@app.get("/staff")
def staff_dashboard():
    return render_template("staff.html")


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
            "called": "text-bg-success",
            "served": "text-bg-secondary",
            "no-show": "text-bg-danger",
        },
    )


@app.post("/queue/<int:ticket_id>/leave")
def leave_queue(ticket_id):
    current_ticket = next(
        (ticket for ticket in TICKETS if ticket["number"] == ticket_id), None
    )
    if current_ticket is None:
        abort(404)
    if current_ticket["status"] in ("waiting", "called"):
        current_ticket["status"] = "no-show"
        flash(f"Ticket #{ticket_id} has left the queue.", "info")
    else:
        flash(f"Ticket #{ticket_id} is already {current_ticket['status']}.", "info")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
