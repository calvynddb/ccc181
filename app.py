"""Mito: a simple queue for individual PC sessions at Arena in Tibanga."""

from datetime import datetime, timedelta
import os
import re
import sys

from dotenv import load_dotenv
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
from flask_migrate import Migrate
from models import Service, Station, Ticket, db
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

if sys.version_info.releaselevel != "final":
    raise RuntimeError(
        "Mito requires a stable Python release. This project is pinned to Python 3.13.12; "
        f"the active interpreter is {sys.version.split()[0]}. Select the workspace .venv interpreter."
    )
if sys.version_info < (3, 11):
    raise RuntimeError("Mito requires Python 3.11 or newer.")

load_dotenv()

app = Flask(__name__)
app.secret_key = "dev-only-change-me"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_ECHO"] = os.environ.get("SQLALCHEMY_ECHO") == "1"

db.init_app(app)
migrate = Migrate(app, db)

STATIONS = [
    {"id": "PC-01", "status": "free"},
    {"id": "PC-02", "status": "busy"},
    {"id": "PC-03", "status": "free"},
    {"id": "PC-04", "status": "free"},
]
HOLD_DURATION = timedelta(minutes=10)


@app.cli.command("seed")
def seed():
    """Add Mito's starting service and PC stations if they are not there yet."""
    if db.session.scalar(db.select(Service).filter_by(name="PC session")) is None:
        db.session.add(Service(name="PC session"))

    starting_stations = [
        ("PC-01", "free"),
        ("PC-02", "busy"),
        ("PC-03", "free"),
        ("PC-04", "free"),
    ]
    for station_id, status in starting_stations:
        if db.session.get(Station, station_id) is None:
            db.session.add(Station(id=station_id, status=status))

    db.session.commit()
    print("Mito's service and stations are ready.")


@app.before_request
def expire_ticket_holds():
    now = datetime.now().astimezone()
    expired_tickets = db.session.scalars(
        db.select(Ticket).where(
            Ticket.status == "on-hold",
            Ticket.held_until <= now,
        )
    ).all()
    for ticket in expired_tickets:
        ticket.status = "no-show"
        ticket.held_until = None
        ticket.hold_expired = True
    if expired_tickets:
        db.session.commit()


def all_services():
    return db.session.scalars(db.select(Service).order_by(Service.name)).all()


def active_services():
    return db.session.scalars(
        db.select(Service).filter_by(is_active=True).order_by(Service.name)
    ).all()


def station_availability():
    open_pcs = db.session.scalar(
        db.select(func.count()).select_from(Station).where(Station.status == "free")
    )
    station_count = db.session.scalar(db.select(func.count()).select_from(Station))
    updated_at = db.session.scalar(db.select(func.max(Station.updated_at)))
    return open_pcs or 0, station_count or 0, updated_at or datetime.now().astimezone()


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/join")
def join_form():
    open_pcs, station_count, updated_at = station_availability()
    return render_template(
        "join.html",
        services=active_services(),
        open_pcs=open_pcs,
        station_count=station_count,
        updated_at=updated_at,
        form={},
        errors={},
    )


@app.post("/join")
def join():
    form = request.form
    nickname = form.get("nickname", "").strip()
    phone = form.get("phone", "").strip()
    service_id = form.get("service_id", type=int)
    service = db.session.get(Service, service_id) if service_id else None
    errors = {}

    if not nickname:
        errors["nickname"] = "Enter a nickname."
    elif len(nickname) > 24:
        errors["nickname"] = "Use 24 characters or fewer."

    if phone:
        digits = re.sub(r"\D", "", phone)
        if (
            len(phone) > 32
            or not re.fullmatch(r"[0-9+() .-]+", phone)
            or not 7 <= len(digits) <= 15
        ):
            errors["phone"] = "Enter a valid phone number, or leave this optional field blank."
    if service is None or not service.is_active:
        errors["service_id"] = "Choose an active service."

    if errors:
        flash("Please fix the highlighted fields.", "danger")
        open_pcs, station_count, updated_at = station_availability()
        return (
            render_template(
                "join.html",
                services=active_services(),
                open_pcs=open_pcs,
                station_count=station_count,
                updated_at=updated_at,
                form=form,
                errors=errors,
            ),
            400,
        )

    ticket = Ticket(nickname=nickname, phone=phone or None, service=service)
    db.session.add(ticket)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("Something went wrong saving your ticket. Please try again.", "danger")
        open_pcs, station_count, updated_at = station_availability()
        return render_template(
            "join.html",
            services=active_services(),
            open_pcs=open_pcs,
            station_count=station_count,
            updated_at=updated_at,
            form=form,
            errors={},
        ), 409

    session["current_ticket_id"] = ticket.id
    flash(f"You joined the queue. Your ticket is #{ticket.id}.", "success")
    return redirect(url_for("ticket", ticket_id=ticket.id))


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
