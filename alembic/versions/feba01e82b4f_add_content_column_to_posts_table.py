"""add content column to posts table

Revision ID: feba01e82b4f
Revises: 260852ba2f36
Create Date: 2025-10-29 01:02:29.295714

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'feba01e82b4f'
down_revision: Union[str, Sequence[str], None] = '260852ba2f36'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('posts', 'content')
    pass
