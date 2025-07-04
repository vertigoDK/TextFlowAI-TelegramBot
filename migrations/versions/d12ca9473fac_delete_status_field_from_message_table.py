"""Delete status field from message table

Revision ID: d12ca9473fac
Revises: 7438165fce5b
Create Date: 2025-06-22 18:30:05.602517

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd12ca9473fac'
down_revision: Union[str, Sequence[str], None] = '7438165fce5b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_messages_user_id'), table_name='messages')
    op.create_index(op.f('ix_messages_user_id'), 'messages', ['user_id'], unique=False)
    op.drop_column('messages', 'status')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('messages', sa.Column('status', postgresql.ENUM('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', name='messagestatus'), autoincrement=False, nullable=False))
    op.drop_index(op.f('ix_messages_user_id'), table_name='messages')
    op.create_index(op.f('ix_messages_user_id'), 'messages', ['user_id'], unique=False)
    # ### end Alembic commands ###
