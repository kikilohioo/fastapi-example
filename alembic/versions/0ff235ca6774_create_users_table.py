"""create users table

Revision ID: 0ff235ca6774
Revises: feba01e82b4f
Create Date: 2025-10-29 01:50:02.600698

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0ff235ca6774'
down_revision: Union[str, Sequence[str], None] = 'feba01e82b4f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False, unique=True),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False, server_default='player'),
        sa.Column('avatar_url', sa.String(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=False), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=False), nullable=False,
                  server_default=sa.text('now()'),
                  onupdate=sa.text('now()')))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('users')
    pass
