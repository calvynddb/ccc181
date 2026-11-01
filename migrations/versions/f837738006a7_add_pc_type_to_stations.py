"""add PC type to stations

Revision ID: f837738006a7
Revises: c3e6661fc4af
Create Date: 2026-10-31 21:02:03.551001

"""
from alembic import op
import sqlalchemy as sa


revision = 'f837738006a7'
down_revision = 'c3e6661fc4af'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('stations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('service_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_stations_service_id_services',
            'services',
            ['service_id'],
            ['id'],
            ondelete='RESTRICT',
        )

    op.execute("UPDATE services SET name = 'Standard PCs' WHERE name = 'PC session'")
    op.execute("UPDATE services SET name = 'VIP PCs' WHERE name = 'Week 4 demo service'")


def downgrade():
    with op.batch_alter_table('stations', schema=None) as batch_op:
        batch_op.drop_constraint('fk_stations_service_id_services', type_='foreignkey')
        batch_op.drop_column('service_id')

    op.execute("UPDATE services SET name = 'PC session' WHERE name = 'Standard PCs'")
    op.execute("UPDATE services SET name = 'Week 4 demo service' WHERE name = 'VIP PCs'")
