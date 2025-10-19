"""Add benefits, procedure, duration, price fields to Service

Revision ID: 9925b4bde808
Revises: 52320ff0eb22
Create Date: 2025-10-12 13:20:17.040876

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9925b4bde808'
down_revision = '52320ff0eb22'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('services', schema=None) as batch_op:
        # Use sa.JSON for MySQL
        batch_op.add_column(sa.Column('benefits', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('procedure', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('duration', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('price', sa.Float(), nullable=True))
        batch_op.alter_column('full_price',
               existing_type=mysql.FLOAT(),
               nullable=True)


def downgrade():
    with op.batch_alter_table('services', schema=None) as batch_op:
        batch_op.alter_column('full_price',
               existing_type=mysql.FLOAT(),
               nullable=False)
        batch_op.drop_column('price')
        batch_op.drop_column('duration')
        batch_op.drop_column('procedure')
        batch_op.drop_column('benefits')
