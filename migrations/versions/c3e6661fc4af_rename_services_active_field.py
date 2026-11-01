"""rename services active field

Revision ID: c3e6661fc4af
Revises: c192066da265
Create Date: 2026-10-31 20:28:23.503883

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3e6661fc4af'
down_revision = 'c192066da265'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'services',
        'is_active',
        new_column_name='active',
        existing_type=sa.Boolean(),
        existing_server_default=sa.text('true'),
        existing_nullable=False,
    )


def downgrade():
    op.alter_column(
        'services',
        'active',
        new_column_name='is_active',
        existing_type=sa.Boolean(),
        existing_server_default=sa.text('true'),
        existing_nullable=False,
    )
