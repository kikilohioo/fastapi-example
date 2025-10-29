"""add foreign key to posts table

Revision ID: d87569c0ecf6
Revises: 0ff235ca6774
Create Date: 2025-10-29 14:40:20.071036

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd87569c0ecf6'
down_revision: Union[str, Sequence[str], None] = '0ff235ca6774'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('posts', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key('posts_users_fk', source_table='posts', referent_table='users',
                          local_cols=['user_id'], remote_cols=['id'], ondelete='CASCADE')
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('posts_users_fk', table_name='posts')
    op.drop_column('posts', 'user_id')
    pass
