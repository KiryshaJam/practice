"""init

Revision ID: 6ef5b688ceee
Revises: 
Create Date: 2025-05-03 19:02:03.348892

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '6ef5b688ceee'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('api_sources',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('api_url', sa.String(length=500), nullable=True),
    sa.Column('api_key', sa.String(length=200), nullable=True),
    sa.Column('last_sync', sa.DateTime(), nullable=True),
    sa.Column('sync_interval', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('cars',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('make', sa.String(length=50), nullable=False),
    sa.Column('model', sa.String(length=50), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('body_type', sa.String(length=50), nullable=True),
    sa.Column('engine_type', sa.String(length=50), nullable=True),
    sa.Column('transmission', sa.String(length=50), nullable=True),
    sa.Column('fuel_type', sa.String(length=50), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('image_url', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=False),
    sa.Column('first_name', sa.String(length=64), nullable=True),
    sa.Column('last_name', sa.String(length=64), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('usage_goals', sa.String(length=256), nullable=True),
    sa.Column('budget', sa.Integer(), nullable=True),
    sa.Column('body_type', sa.String(length=32), nullable=True),
    sa.Column('fuel_type', sa.String(length=32), nullable=True),
    sa.Column('transmission', sa.String(length=32), nullable=True),
    sa.Column('drivetrain', sa.String(length=32), nullable=True),
    sa.Column('engine_power', sa.Integer(), nullable=True),
    sa.Column('fuel_consumption', sa.Float(), nullable=True),
    sa.Column('safety_features', sa.String(length=256), nullable=True),
    sa.Column('comfort_features', sa.String(length=256), nullable=True),
    sa.Column('criteria', sa.String(length=512), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('car_reviews',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('car_id', sa.Integer(), nullable=False),
    sa.Column('rating', sa.Float(), nullable=True),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.Column('source', sa.String(length=100), nullable=True),
    sa.Column('author', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['car_id'], ['cars.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('car_specifications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('car_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('value', sa.String(length=200), nullable=False),
    sa.Column('source', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['car_id'], ['cars.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('crash_tests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('car_id', sa.Integer(), nullable=False),
    sa.Column('organization', sa.String(length=100), nullable=True),
    sa.Column('rating', sa.String(length=10), nullable=True),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('details', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['car_id'], ['cars.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('criteria',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('value', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('criterion',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('weight', sa.Float(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('pairwise_comparisons',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('criterion_id', sa.Integer(), nullable=False),
    sa.Column('first_image', sa.String(length=255), nullable=False),
    sa.Column('second_image', sa.String(length=255), nullable=False),
    sa.Column('comparison_value', sa.Float(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['criterion_id'], ['criterion.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('pairwise_comparisons')
    op.drop_table('criterion')
    op.drop_table('criteria')
    op.drop_table('crash_tests')
    op.drop_table('car_specifications')
    op.drop_table('car_reviews')
    op.drop_table('users')
    op.drop_table('cars')
    op.drop_table('api_sources')
