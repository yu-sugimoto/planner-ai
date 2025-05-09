"""first local_migration

Revision ID: b1aa4b815054
Revises: c6ddb2ac6330
Create Date: 2025-03-08 08:24:27.284207

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1aa4b815054'
down_revision: Union[str, None] = 'c6ddb2ac6330'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('destinations',
    sa.Column('destination_id', sa.Integer(), nullable=False),
    sa.Column('destination_name', sa.String(), nullable=False),
    sa.Column('destination_category', sa.String(), nullable=False),
    sa.Column('destination_fare', sa.Integer(), nullable=False),
    sa.Column('destination_staytime', sa.Integer(), nullable=False),
    sa.Column('destination_rating', sa.Float(), nullable=False),
    sa.Column('destination_description', sa.Text(), nullable=False),
    sa.Column('destination_address', sa.String(), nullable=False),
    sa.Column('destination_latitude', sa.Float(), nullable=False),
    sa.Column('destination_longitude', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('destination_id')
    )
    op.create_index(op.f('ix_destinations_destination_id'), 'destinations', ['destination_id'], unique=False)
    op.create_table('transportations',
    sa.Column('transportation_id', sa.Integer(), nullable=False),
    sa.Column('start_destination_id', sa.Integer(), nullable=False),
    sa.Column('end_destination_id', sa.Integer(), nullable=False),
    sa.Column('transportation_fare', sa.Integer(), nullable=False),
    sa.Column('transportation_method', sa.String(), nullable=False),
    sa.Column('transportation_time', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['end_destination_id'], ['destinations.destination_id'], ),
    sa.ForeignKeyConstraint(['start_destination_id'], ['destinations.destination_id'], ),
    sa.PrimaryKeyConstraint('transportation_id')
    )
    op.create_index(op.f('ix_transportations_transportation_id'), 'transportations', ['transportation_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_transportations_transportation_id'), table_name='transportations')
    op.drop_table('transportations')
    op.drop_index(op.f('ix_destinations_destination_id'), table_name='destinations')
    op.drop_table('destinations')
    # ### end Alembic commands ###
