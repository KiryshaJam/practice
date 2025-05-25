"""remove description

Revision ID: a3d5f28d16d3
Revises: 6ef5b688ceee
Create Date: 2025-05-03 19:05:42.331560

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a3d5f28d16d3'
down_revision: Union[str, None] = '6ef5b688ceee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column('cars', 'description')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('cars', sa.Column('description', sa.TEXT(), nullable=True))
