"""create posts table

Revision ID: 260852ba2f36
Revises: 
Create Date: 2025-10-29 00:44:01.598131

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '260852ba2f36'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'posts',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
        # sa.Column('content', sa.String(), nullable=False), # Comentado a propósito para agregar una columna más tarde
        sa.Column('published', sa.Boolean(), nullable=False, server_default=sa.text('TRUE')),
        # sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False), # Comentado a propósito para evitar errores de clave foránea
        sa.Column('created_at', sa.TIMESTAMP(timezone=False), nullable=False, server_default=sa.text('now()')))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('posts')
    pass
