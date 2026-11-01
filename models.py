from datetime import datetime
from decimal import Decimal

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Numeric,
    SmallInteger,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class Service(db.Model):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(60), nullable=False, unique=True)
    active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )

    tickets: Mapped[list["Ticket"]] = relationship(back_populates="service")
    stations: Mapped[list["Station"]] = relationship(back_populates="service")

    __table_args__ = (
        CheckConstraint("btrim(name) <> ''", name="ck_services_name_not_blank"),
    )


class Station(db.Model):
    __tablename__ = "stations"

    id: Mapped[str] = mapped_column(String(10), primary_key=True)
    status: Mapped[str] = mapped_column(
        String(10), nullable=False, default="free", server_default="free"
    )
    service_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "services.id",
            ondelete="RESTRICT",
            name="fk_stations_service_id_services",
        )
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    floor: Mapped[int | None] = mapped_column(SmallInteger)
    map_x: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    map_y: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))

    tickets: Mapped[list["Ticket"]] = relationship(back_populates="station")
    service: Mapped["Service | None"] = relationship(back_populates="stations")

    __table_args__ = (
        CheckConstraint("id ~ '^PC-[0-9]{2}$'", name="ck_stations_id_format"),
        CheckConstraint("status IN ('free', 'busy')", name="ck_stations_status"),
        CheckConstraint("floor IS NULL OR floor IN (1, 2)", name="ck_stations_floor"),
        CheckConstraint("map_x IS NULL OR map_x BETWEEN 0 AND 100", name="ck_stations_map_x"),
        CheckConstraint("map_y IS NULL OR map_y BETWEEN 0 AND 100", name="ck_stations_map_y"),
        CheckConstraint(
            "(map_x IS NULL AND map_y IS NULL) OR "
            "(map_x IS NOT NULL AND map_y IS NOT NULL AND floor IS NOT NULL)",
            name="ck_stations_map_location_complete",
        ),
    )


class Ticket(db.Model):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    nickname: Mapped[str] = mapped_column(String(24), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32))
    service_id: Mapped[int] = mapped_column(
        ForeignKey("services.id", ondelete="RESTRICT"), nullable=False
    )
    station_id: Mapped[str | None] = mapped_column(
        ForeignKey("stations.id", ondelete="RESTRICT")
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="waiting", server_default="waiting"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    held_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    hold_expired: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    called_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    claim_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    left_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    service: Mapped["Service"] = relationship(back_populates="tickets")
    station: Mapped["Station | None"] = relationship(back_populates="tickets")

    __table_args__ = (
        CheckConstraint("btrim(nickname) <> ''", name="ck_tickets_nickname_not_blank"),
        CheckConstraint(
            "phone IS NULL OR (phone ~ '^[0-9+() .-]+$' AND "
            "length(regexp_replace(phone, '[^0-9]', '', 'g')) BETWEEN 7 AND 15)",
            name="ck_tickets_phone_valid",
        ),
        CheckConstraint(
            "status IN ('waiting', 'on-hold', 'called', 'served', 'no-show', 'left')",
            name="ck_tickets_status",
        ),
        CheckConstraint(
            "held_until IS NULL OR held_until > created_at",
            name="ck_tickets_hold_after_creation",
        ),
        CheckConstraint(
            "(status = 'on-hold' AND held_until IS NOT NULL) OR "
            "(status <> 'on-hold' AND held_until IS NULL)",
            name="ck_tickets_hold_status_consistent",
        ),
        CheckConstraint(
            "claim_until IS NULL OR "
            "(called_at IS NOT NULL AND claim_until > called_at)",
            name="ck_tickets_claim_deadline_valid",
        ),
        CheckConstraint(
            "status <> 'called' OR "
            "(station_id IS NOT NULL AND called_at IS NOT NULL AND claim_until IS NOT NULL)",
            name="ck_tickets_called_fields_required",
        ),
        CheckConstraint(
            "status <> 'served' OR (station_id IS NOT NULL AND called_at IS NOT NULL)",
            name="ck_tickets_served_fields_required",
        ),
        CheckConstraint("status <> 'left' OR left_at IS NOT NULL", name="ck_tickets_left_time"),
        CheckConstraint(
            "NOT hold_expired OR status = 'no-show'",
            name="ck_tickets_expired_hold_is_no_show",
        ),
        CheckConstraint(
            "status <> 'no-show' OR hold_expired OR called_at IS NOT NULL",
            name="ck_tickets_no_show_has_reason",
        ),
    )
