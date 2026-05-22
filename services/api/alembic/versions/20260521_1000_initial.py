"""initial schema — все таблицы UMRABOR v1

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-21 10:00:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # ─── users_umrabor ───
    op.create_table(
        "users_umrabor",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("login", sa.String(64), unique=True, nullable=False, index=True),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("email", sa.String(200), unique=True, nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="admin"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_login_ip", sa.String(45), nullable=True),
        sa.Column("last_login_ua", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ─── partners ───
    op.create_table(
        "partners",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("legal_name", sa.String(255), nullable=False),
        sa.Column("brand", sa.String(120), nullable=False, index=True),
        sa.Column("slug", sa.String(120), unique=True, nullable=False, index=True),
        sa.Column("logo_url", sa.String(500), nullable=True),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("founded_year", sa.Integer, nullable=True),
        sa.Column("license_no", sa.String(50), nullable=True),
        sa.Column("license_authority", sa.String(200), nullable=False, server_default="Госкомтуризм РУз"),
        sa.Column("license_issued_at", sa.Date, nullable=True),
        sa.Column("license_until", sa.Date, nullable=True, index=True),
        sa.Column("license_file_url", sa.String(500), nullable=True),
        sa.Column("inn", sa.String(20), nullable=True, index=True),
        sa.Column("oked", sa.String(20), nullable=True),
        sa.Column("bank_account", sa.String(40), nullable=True),
        sa.Column("bank_name", sa.String(200), nullable=True),
        sa.Column("bank_mfo", sa.String(10), nullable=True),
        sa.Column("vat_code", sa.String(20), nullable=True),
        sa.Column("legal_address", sa.String(500), nullable=True),
        sa.Column("actual_address", sa.String(500), nullable=True),
        sa.Column("contact_full_name", sa.String(200), nullable=True),
        sa.Column("contact_position", sa.String(120), nullable=True),
        sa.Column("contact_phone", sa.String(20), nullable=True),
        sa.Column("contact_email", sa.String(200), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active", index=True),
        sa.Column("status_changed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("internal_note", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "partner_status_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("partner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("partners.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("changed_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users_umrabor.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "partner_employees",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("partner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("partners.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("login", sa.String(64), unique=True, nullable=False, index=True),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=True),
        sa.Column("last_name", sa.String(100), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("email", sa.String(200), nullable=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("must_change_password", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("role", sa.String(20), nullable=False, server_default="operator"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_login_ip", sa.String(45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ─── customers ───
    op.create_table(
        "customers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("phone", sa.String(20), unique=True, nullable=False, index=True),
        sa.Column("email", sa.String(200), unique=True, nullable=True),
        sa.Column("full_name", sa.String(200), nullable=True),
        sa.Column("first_name", sa.String(100), nullable=True),
        sa.Column("last_name", sa.String(100), nullable=True),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("birth_date", sa.Date, nullable=True),
        sa.Column("gender", sa.String(2), nullable=True),
        sa.Column("locale", sa.String(10), nullable=False, server_default="uz-Cyrl"),
        sa.Column("click_user_id", sa.String(64), unique=True, nullable=True),
        sa.Column("notifications_push", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("notifications_geo", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("notifications_marketing", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "pilgrims",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("middle_name", sa.String(100), nullable=True),
        sa.Column("full_name", sa.String(300), nullable=False),
        sa.Column("gender", sa.String(2), nullable=False),
        sa.Column("birth_date", sa.Date, nullable=False),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("document_type", sa.String(20), nullable=False, server_default="zagran"),
        sa.Column("document_series_number", sa.String(40), nullable=True),
        sa.Column("document_valid_until", sa.Date, nullable=True),
        sa.Column("document_file_url", sa.String(500), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("mahram_pilgrim_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("pilgrims.id", ondelete="SET NULL"), nullable=True),
        sa.Column("mahram_relation", sa.String(20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ─── 8 справочников ───
    op.create_table(
        "dir_hotels",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False, index=True),
        sa.Column("slug", sa.String(200), unique=True, nullable=False),
        sa.Column("city", sa.String(20), nullable=False, index=True),
        sa.Column("stars", sa.Integer, nullable=False, server_default="5"),
        sa.Column("distance_value", sa.Numeric(8, 2), nullable=True),
        sa.Column("distance_unit", sa.String(2), nullable=False, server_default="м"),
        sa.Column("walk_minutes", sa.Integer, nullable=True),
        sa.Column("transport_minutes", sa.Integer, nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("address", sa.String(500), nullable=True),
        sa.Column("lat", sa.Numeric(10, 7), nullable=True),
        sa.Column("lng", sa.Numeric(10, 7), nullable=True),
        sa.Column("photos", postgresql.ARRAY(sa.String), nullable=False, server_default="{}"),
        sa.Column("amenities", postgresql.ARRAY(sa.String), nullable=False, server_default="{}"),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "dir_airlines",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False, index=True),
        sa.Column("iata", sa.String(3), unique=True, nullable=False, index=True),
        sa.Column("country", sa.String(80), nullable=True),
        sa.Column("base_iata", sa.String(3), nullable=True),
        sa.Column("base_city", sa.String(80), nullable=True),
        sa.Column("logo_url", sa.String(500), nullable=True),
        sa.Column("logo_color", sa.String(8), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "dir_services",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("icon", sa.String(10), nullable=True),
        sa.Column("name", sa.String(120), nullable=False, index=True),
        sa.Column("description", sa.String(300), nullable=True),
        sa.Column("category", sa.String(20), nullable=False, server_default="other"),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "dir_gifts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("icon", sa.String(10), nullable=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.String(300), nullable=True),
        sa.Column("cost_uzs", sa.Integer, nullable=True),
        sa.Column("brand", sa.String(20), nullable=False, server_default="standard"),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "dir_meal_types",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False, unique=True),
        sa.Column("description", sa.String(300), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "dir_package_types",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(80), nullable=False, unique=True),
        sa.Column("description", sa.String(300), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "dir_transfer_types",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("icon", sa.String(10), nullable=True),
        sa.Column("name", sa.String(120), nullable=False, unique=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "dir_reject_reasons",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False, unique=True),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "dir_inventory_types",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(20), unique=True, nullable=False, index=True),
        sa.Column("label", sa.String(120), nullable=False),
        sa.Column("capacity", sa.Integer, nullable=False),
        sa.Column("gender_constraint", sa.String(2), nullable=True),
        sa.Column("description", sa.String(300), nullable=True),
        sa.Column("is_globally_enabled", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "partner_inventory_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("partner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("partners.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("inventory_type_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("dir_inventory_types.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("is_enabled", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("meta", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ─── packages + departures + inventory ───
    op.create_table(
        "packages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("partner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("partners.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(200), nullable=False, index=True),
        sa.Column("package_type_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("dir_package_types.id", ondelete="SET NULL"), nullable=True),
        sa.Column("route", postgresql.ARRAY(sa.String), nullable=False, server_default="{}"),
        sa.Column("duration_days", sa.Integer, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("photos", postgresql.ARRAY(sa.String), nullable=False, server_default="{}"),
        sa.Column("airline_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("dir_airlines.id", ondelete="SET NULL"), nullable=True),
        sa.Column("transfer_type_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("dir_transfer_types.id", ondelete="SET NULL"), nullable=True),
        sa.Column("meal_type_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("dir_meal_types.id", ondelete="SET NULL"), nullable=True),
        sa.Column("price_sgl", sa.Integer, nullable=True),
        sa.Column("price_dbl", sa.Integer, nullable=True),
        sa.Column("price_trpl", sa.Integer, nullable=True),
        sa.Column("price_quad", sa.Integer, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft", index=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("moderated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("moderation_note", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "package_hotels",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("package_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("packages.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("hotel_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("dir_hotels.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("nights", sa.Integer, nullable=False),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "package_services",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("package_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("packages.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("service_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("dir_services.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("package_id", "service_id"),
    )
    op.create_table(
        "package_gifts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("package_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("packages.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("gift_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("dir_gifts.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("package_id", "gift_id"),
    )

    op.create_table(
        "departures",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("package_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("packages.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("date_out", sa.Date, nullable=False, index=True),
        sa.Column("date_in", sa.Date, nullable=False),
        sa.Column("flight_out", sa.String(20), nullable=True),
        sa.Column("flight_in", sa.String(20), nullable=True),
        sa.Column("aircraft", sa.String(120), nullable=True),
        sa.Column("baggage", sa.String(50), nullable=True),
        sa.Column("capacity_total", sa.Integer, nullable=False, server_default="0"),
        sa.Column("sold_total", sa.Integer, nullable=False, server_default="0"),
        sa.Column("price_sgl", sa.Integer, nullable=True),
        sa.Column("price_dbl", sa.Integer, nullable=True),
        sa.Column("price_trpl", sa.Integer, nullable=True),
        sa.Column("price_quad", sa.Integer, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "departure_inventory",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("departure_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("departures.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("room_type", sa.String(20), nullable=False),
        sa.Column("capacity", sa.Integer, nullable=False, server_default="0"),
        sa.Column("sold", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_enabled", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("departure_id", "room_type"),
    )

    op.create_table(
        "package_moderation_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("package_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("packages.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("moderator_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users_umrabor.id", ondelete="SET NULL"), nullable=True),
        sa.Column("decision", sa.String(20), nullable=False),
        sa.Column("comment", sa.Text, nullable=True),
        sa.Column("diff", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ─── bookings ───
    op.create_table(
        "bookings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(32), unique=True, nullable=False, index=True),
        sa.Column("partner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("partners.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("package_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("packages.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("departure_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("departures.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("source", sa.String(20), nullable=False, server_default="web"),
        sa.Column("click_id", sa.String(32), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="new", index=True),
        sa.Column("sla_deadline_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_uzs", sa.Integer, nullable=False, server_default="0"),
        sa.Column("cashback_uzs", sa.Integer, nullable=False, server_default="0"),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancellation_reason_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("dir_reject_reasons.id", ondelete="SET NULL"), nullable=True),
        sa.Column("cancellation_comment", sa.Text, nullable=True),
        sa.Column("assigned_operator_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("partner_employees.id", ondelete="SET NULL"), nullable=True),
        sa.Column("voucher_url", sa.String(500), nullable=True),
        sa.Column("meta", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "placements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("room_type", sa.String(20), nullable=False),
        sa.Column("capacity", sa.Integer, nullable=False),
        sa.Column("price_per_person_uzs", sa.Integer, nullable=False),
        sa.Column("total_uzs", sa.Integer, nullable=False, server_default="0"),
        sa.Column("awaiting_co_lodger", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "booking_pilgrims",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("pilgrim_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("pilgrims.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("placement_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("placements.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("booking_id", "pilgrim_id"),
    )

    op.create_table(
        "booking_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("event_type", sa.String(40), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("actor_kind", sa.String(20), nullable=True),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("actor_name", sa.String(200), nullable=True),
        sa.Column("meta", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ─── chat ───
    op.create_table(
        "chat_threads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("thread_type", sa.String(30), nullable=False, index=True),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("partner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("partners.id", ondelete="CASCADE"), nullable=True),
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bookings.id", ondelete="SET NULL"), nullable=True),
        sa.Column("last_message_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("customer_unread", sa.Integer, nullable=False, server_default="0"),
        sa.Column("partner_unread", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "chat_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("thread_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("chat_threads.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("sender_kind", sa.String(20), nullable=False),
        sa.Column("sender_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("sender_name", sa.String(200), nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("attachments", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ─── payments ───
    op.create_table(
        "payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(32), unique=True, nullable=False, index=True),
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bookings.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("partner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("partners.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("channel", sa.String(20), nullable=False, server_default="click"),
        sa.Column("amount_uzs", sa.Integer, nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="UZS"),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending", index=True),
        sa.Column("click_trans_id", sa.String(64), nullable=True, index=True),
        sa.Column("click_paydoc_id", sa.String(64), nullable=True),
        sa.Column("click_phone", sa.String(20), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("refund_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("refund_reason", sa.Text, nullable=True),
        sa.Column("raw", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ─── audit + notifications ───
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("actor_kind", sa.String(20), nullable=False, index=True),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column("actor_name", sa.String(200), nullable=True),
        sa.Column("scope_partner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("partners.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(30), nullable=False, index=True),
        sa.Column("object_kind", sa.String(40), nullable=False),
        sa.Column("object_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("object_label", sa.String(255), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("ip", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("meta", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("recipient_kind", sa.String(20), nullable=False, index=True),
        sa.Column("recipient_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("channel", sa.String(20), nullable=False),
        sa.Column("trigger", sa.String(40), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("payload", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("read_at", sa.String(40), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ─── auth helpers ───
    op.create_table(
        "otp_codes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("phone", sa.String(20), nullable=False, index=True),
        sa.Column("code_hash", sa.String(255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attempts", sa.Integer, nullable=False, server_default="0"),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("purpose", sa.String(20), nullable=False, server_default="login"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "refresh_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("subject_kind", sa.String(20), nullable=False, index=True),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("jti", sa.String(64), unique=True, nullable=False, index=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("ip", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    for t in [
        "refresh_tokens",
        "otp_codes",
        "notifications",
        "audit_logs",
        "payments",
        "chat_messages",
        "chat_threads",
        "booking_events",
        "booking_pilgrims",
        "placements",
        "bookings",
        "package_moderation_events",
        "departure_inventory",
        "departures",
        "package_gifts",
        "package_services",
        "package_hotels",
        "packages",
        "partner_inventory_settings",
        "dir_inventory_types",
        "dir_reject_reasons",
        "dir_transfer_types",
        "dir_package_types",
        "dir_meal_types",
        "dir_gifts",
        "dir_services",
        "dir_airlines",
        "dir_hotels",
        "pilgrims",
        "customers",
        "partner_employees",
        "partner_status_history",
        "partners",
        "users_umrabor",
    ]:
        op.drop_table(t)
