"""create orders table

Revision ID: 20260326_0001
Revises:
Create Date: 2026-03-26
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "20260326_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("customer_id", sa.String(length=128), nullable=False),
        sa.Column("description", sa.String(length=1024), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("is_vip", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_orders_customer_id", "orders", ["customer_id"], unique=False)
    op.create_index("ix_orders_status", "orders", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_orders_status", table_name="orders")
    op.drop_index("ix_orders_customer_id", table_name="orders")
    op.drop_table("orders")
