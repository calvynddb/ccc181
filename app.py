"""Mito: an individual PC queue for internet cafés such as Arena."""

from datetime import datetime, timedelta, timezone
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
from sqlalchemy import and_, func, or_
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

HOLD_DURATION = timedelta(minutes=10)
CLAIM_DURATION = timedelta(minutes=5)
PH_TIME = timezone(timedelta(hours=8))


@app.cli.command("seed")
def seed():
    """Add Mito's two PC types and twelve starting stations if missing."""
    for name in ("Standard PCs", "VIP PCs"):
        if db.session.scalar(db.select(Service).filter_by(name=name)) is None:
            db.session.add(Service(name=name))
    db.session.flush()
    standard = db.session.scalar(db.select(Service).filter_by(name="Standard PCs"))
    vip = db.session.scalar(db.select(Service).filter_by(name="VIP PCs"))

    for number in range(1, 13):
        station_id = f"PC-{number:02d}"
        service = standard if number <= 8 else vip
        station = db.session.get(Station, station_id)
        if station is None:
            db.session.add(
                Station(
                    id=station_id,
                    status="busy" if station_id == "PC-02" else "free",
                    service=service,
                )
            )
        elif station.service_id is None:
            station.service = service

    db.session.commit()
    print("Mito's PC types and stations are ready.")


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

    expired_calls = db.session.scalars(
        db.select(Ticket).where(
            Ticket.status == "called",
            Ticket.claim_until <= now,
        )
    ).all()
    for ticket in expired_calls:
        ticket.status = "no-show"
        if ticket.station is not None:
            ticket.station.status = "free"

    if expired_tickets or expired_calls:
        db.session.commit()


def all_services():
    return db.session.scalars(db.select(Service).order_by(Service.name)).all()


def active_services():
    return db.session.scalars(
        db.select(Service).filter_by(active=True).order_by(Service.name)
    ).all()


def station_availability():
    open_pcs = db.session.scalar(
        db.select(func.count()).select_from(Station).where(Station.status == "free")
    )
    station_count = db.session.scalar(db.select(func.count()).select_from(Station))
    updated_at = db.session.scalar(db.select(func.max(Station.updated_at)))
    return open_pcs or 0, station_count or 0, updated_at or datetime.now().astimezone()


def open_pcs_by_type():
    statement = (
        db.select(Service.name, func.count(Station.id))
        .outerjoin(
            Station,
            and_(Station.service_id == Service.id, Station.status == "free"),
        )
        .where(Service.active.is_(True))
        .group_by(Service.id)
        .order_by(Service.name)
    )
    return [
        {"name": name, "open_count": count}
        for name, count in db.session.execute(statement)
    ]


def people_ahead(ticket):
    """Count earlier waiting tickets for the same service."""
    earlier = or_(
        Ticket.created_at < ticket.created_at,
        and_(Ticket.created_at == ticket.created_at, Ticket.id < ticket.id),
    )
    statement = (
        db.select(func.count())
        .select_from(Ticket)
        .where(
            Ticket.service_id == ticket.service_id,
            Ticket.status == "waiting",
            earlier,
        )
    )
    return db.session.scalar(statement)


@app.template_filter("local")
def local_time(value):
    """Show a database time in Philippine time."""
    return value.astimezone(PH_TIME).strftime("%b %d, %I:%M %p") if value else ""


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/join")
def join_form():
    open_pcs, station_count, updated_at = station_availability()
    return render_template(
        "join.html",
        services=active_services(),
        open_pcs_by_type=open_pcs_by_type(),
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
    if service is None or not service.active:
        errors["service_id"] = "Choose an active PC type."

    if errors:
        flash("Please fix the highlighted fields.", "danger")
        open_pcs, station_count, updated_at = station_availability()
        return (
            render_template(
                "join.html",
                services=active_services(),
                open_pcs_by_type=open_pcs_by_type(),
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
            open_pcs_by_type=open_pcs_by_type(),
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
    if service_id and db.session.get(Service, service_id) is None:
        service_id = None

    statement = (
        db.select(Ticket)
        .where(Ticket.status.in_(("waiting", "called", "on-hold")))
        .order_by(Ticket.created_at, Ticket.id)
    )
    if service_id:
        statement = statement.where(Ticket.service_id == service_id)
    queue = db.session.scalars(statement).all()
    services = all_services()
    next_ticket = next((ticket for ticket in queue if ticket.status == "waiting"), None)
    stations = db.session.scalars(db.select(Station).order_by(Station.id)).all()
    open_pcs = sum(station.status == "free" for station in stations)
    free_stations = [
        station
        for station in stations
        if station.status == "free"
        and next_ticket is not None
        and station.service_id == next_ticket.service_id
    ]
    updated_at = db.session.scalar(db.select(func.max(Station.updated_at)))
    return render_template(
        "staff.html",
        queue=queue,
        services=services,
        open_pcs_by_type=open_pcs_by_type(),
        selected=service_id,
        next_ticket=next_ticket,
        free_stations=free_stations,
        stations=stations,
        open_pcs=open_pcs,
        unclassified_pcs=sum(station.service_id is None for station in stations),
        waiting_count=sum(ticket.status == "waiting" for ticket in queue),
        called_count=sum(ticket.status == "called" for ticket in queue),
        held_count=sum(ticket.status == "on-hold" for ticket in queue),
        updated_at=updated_at or datetime.now().astimezone(),
    )


@app.post("/staff/call-next")
def call_next():
    service_id = request.form.get("service_id", type=int)
    station_id = request.form.get("station_id", "").strip()
    if service_id is None or db.session.get(Service, service_id) is None:
        flash("Choose a valid PC type before calling the next ticket.", "warning")
        return redirect(url_for("staff_dashboard"))

    station = db.session.scalar(
        db.select(Station)
        .where(Station.id == station_id, Station.service_id == service_id)
        .with_for_update()
    )
    if station is None or station.status != "free":
        db.session.rollback()
        flash("Choose a free PC of the same type as the waiting ticket.", "warning")
        return redirect(url_for("staff_dashboard", service_id=service_id))

    statement = (
        db.select(Ticket)
        .where(Ticket.status == "waiting", Ticket.service_id == service_id)
        .order_by(Ticket.created_at, Ticket.id)
        .limit(1)
        .with_for_update(skip_locked=True)
    )
    next_ticket = db.session.scalar(statement)
    if next_ticket is None:
        db.session.rollback()
        flash("There are no waiting tickets for this PC type.", "info")
    else:
        called_at = datetime.now().astimezone()
        next_ticket.status = "called"
        next_ticket.station = station
        next_ticket.called_at = called_at
        next_ticket.claim_until = called_at + CLAIM_DURATION
        station.status = "busy"
        db.session.commit()
        flash(f"Ticket #{next_ticket.id} called to {station.id}.", "success")
    return redirect(url_for("staff_dashboard", service_id=service_id))


@app.post("/staff/stations/<station_id>/toggle")
def toggle_station(station_id):
    station = db.get_or_404(Station, station_id)
    station.status = "busy" if station.status == "free" else "free"
    db.session.commit()
    flash(f"{station.id} marked {station.status}.", "info")
    return redirect(url_for("staff_dashboard"))


@app.post("/staff/stations")
def station_create():
    station_id = request.form.get("station_id", "").strip().upper()
    service_id = request.form.get("service_id", type=int)
    service = db.session.get(Service, service_id) if service_id else None
    if not re.fullmatch(r"PC-[0-9]{2}", station_id):
        flash("Enter a PC ID in the format PC-05.", "danger")
        return redirect(url_for("staff_dashboard"))
    if service is None or not service.active:
        flash("Choose an active PC type for this station.", "danger")
        return redirect(url_for("staff_dashboard"))

    db.session.add(Station(id=station_id, status="free", service=service))
    try:
        db.session.commit()
        flash(f"{station_id} added as free.", "success")
    except IntegrityError:
        db.session.rollback()
        flash(f"{station_id} already exists.", "danger")
    return redirect(url_for("staff_dashboard"))


@app.post("/staff/stations/<station_id>/type")
def station_set_type(station_id):
    station = db.get_or_404(Station, station_id)
    service_id = request.form.get("service_id", type=int)
    service = db.session.get(Service, service_id) if service_id else None
    if service is None or not service.active:
        flash("Choose an active PC type.", "danger")
    elif station.status != "free":
        flash("Mark the PC free before changing its type.", "warning")
    else:
        station.service = service
        db.session.commit()
        flash(f"{station.id} assigned to {service.name}.", "success")
    return redirect(url_for("staff_dashboard"))


@app.post("/staff/tickets/<int:ticket_id>/<action>")
def staff_action(ticket_id, action):
    if action not in ("serve", "no-show"):
        abort(404)
    ticket = db.get_or_404(Ticket, ticket_id)
    service_id = request.form.get("service_id", type=int)
    if ticket.status != "called":
        flash(f"Call ticket #{ticket_id} before marking it served.", "warning")
    else:
        ticket.status = "served" if action == "serve" else "no-show"
        if action == "no-show" and ticket.station is not None:
            ticket.station.status = "free"
        db.session.commit()
        flash(f"Ticket #{ticket_id} marked {ticket.status}.", "info")
    return redirect(url_for("staff_dashboard", service_id=service_id))


@app.post("/staff/tickets/<int:ticket_id>/delete")
def delete_ticket(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)
    if ticket.station is not None and ticket.status == "called":
        ticket.station.status = "free"
    db.session.delete(ticket)
    db.session.commit()
    flash(f"Ticket #{ticket_id} was deleted.", "warning")
    return redirect(url_for("staff_dashboard"))


@app.get("/staff/services")
def services_list():
    return render_template("services.html", services=all_services())


@app.post("/staff/services")
def service_create():
    name = request.form.get("name", "").strip()
    if not name or len(name) > 60:
        flash("Enter a PC type name with 60 characters or fewer.", "danger")
        return redirect(url_for("services_list"))

    db.session.add(Service(name=name))
    try:
        db.session.commit()
        flash(f"PC type “{name}” added.", "success")
    except IntegrityError:
        db.session.rollback()
        flash(f"A PC type named “{name}” already exists.", "danger")
    return redirect(url_for("services_list"))


@app.post("/staff/services/<int:service_id>/edit")
def service_edit(service_id):
    service = db.get_or_404(Service, service_id)
    name = request.form.get("name", "").strip()
    if not name or len(name) > 60:
        flash("Enter a PC type name with 60 characters or fewer.", "danger")
        return redirect(url_for("services_list"))

    service.name = name
    service.active = request.form.get("active") == "on"
    try:
        db.session.commit()
        flash(f"PC type “{name}” updated.", "success")
    except IntegrityError:
        db.session.rollback()
        flash(f"A PC type named “{name}” already exists.", "danger")
    return redirect(url_for("services_list"))


@app.post("/staff/services/<int:service_id>/delete")
def service_delete(service_id):
    service = db.get_or_404(Service, service_id)
    if service.tickets:
        flash(f"“{service.name}” has tickets, so it cannot be deleted. Turn it off instead.", "danger")
        return redirect(url_for("services_list"))
    if service.stations:
        flash(f"“{service.name}” has assigned PCs, so it cannot be deleted. Reassign them or turn the type off.", "danger")
        return redirect(url_for("services_list"))
    db.session.delete(service)
    db.session.commit()
    flash(f"Service “{service.name}” deleted.", "warning")
    return redirect(url_for("services_list"))


@app.route("/queue/<int:ticket_id>")
def ticket(ticket_id):
    current_ticket = db.get_or_404(Ticket, ticket_id)
    return render_template(
        "ticket.html",
        ticket=current_ticket,
        service=current_ticket.service,
        ahead=people_ahead(current_ticket),
        status_classes={
            "waiting": "text-bg-warning",
            "on-hold": "text-bg-info",
            "called": "text-bg-success",
            "served": "text-bg-secondary",
            "no-show": "text-bg-danger",
        },
        held_until=current_ticket.held_until,
        hold_expired=current_ticket.hold_expired,
    )


@app.post("/queue/<int:ticket_id>/leave")
def leave_queue(ticket_id):
    current_ticket = db.get_or_404(Ticket, ticket_id)
    if current_ticket.status in ("waiting", "called", "on-hold"):
        if current_ticket.status == "called" and current_ticket.station is not None:
            current_ticket.station.status = "free"
        current_ticket.status = "left"
        current_ticket.held_until = None
        current_ticket.left_at = datetime.now().astimezone()
        db.session.commit()
        flash(f"Ticket #{ticket_id} has left the queue.", "info")
    else:
        flash(f"Ticket #{ticket_id} is already {current_ticket.status}.", "info")
    if session.get("current_ticket_id") == ticket_id:
        session.pop("current_ticket_id", None)
    return redirect(url_for("index"))


@app.post("/queue/<int:ticket_id>/hold")
def hold_queue_place(ticket_id):
    current_ticket = db.get_or_404(Ticket, ticket_id)
    if current_ticket.status == "waiting":
        current_ticket.status = "on-hold"
        current_ticket.held_until = datetime.now().astimezone() + HOLD_DURATION
        db.session.commit()
        flash("Your place is on hold for 10 minutes. Resume before it expires to keep your ticket order.", "info")
    else:
        flash("Only a waiting ticket can be put on hold.", "warning")
    return redirect(url_for("ticket", ticket_id=ticket_id))


@app.post("/queue/<int:ticket_id>/resume")
def resume_queue_place(ticket_id):
    current_ticket = db.get_or_404(Ticket, ticket_id)
    if current_ticket.status == "on-hold":
        current_ticket.status = "waiting"
        current_ticket.held_until = None
        db.session.commit()
        flash("Your place is back in the queue in its original ticket order.", "success")
    else:
        flash("This ticket is no longer on hold.", "info")
    return redirect(url_for("ticket", ticket_id=ticket_id))


@app.get("/queue/<int:ticket_id>/status.json")
def ticket_status(ticket_id):
    current_ticket = db.get_or_404(Ticket, ticket_id)
    return {
        "status": current_ticket.status,
        "ahead": people_ahead(current_ticket),
        "station_id": current_ticket.station_id,
        "held_until": local_time(current_ticket.held_until),
        "claim_until": local_time(current_ticket.claim_until),
        "hold_expired": current_ticket.hold_expired,
        "was_called": current_ticket.called_at is not None,
    }


if __name__ == "__main__":
    app.run(debug=True)
