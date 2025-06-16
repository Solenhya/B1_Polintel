"""Qualité de mandats en clef primaire

Revision ID: a8bfef42f685
Revises: 7018c222f7f6
Create Date: 2025-06-12 15:15:05.554151

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a8bfef42f685'
down_revision: Union[str, None] = '7018c222f7f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    # Drop the existing primary key constraint
    op.drop_constraint('organe_relation_pkey', 'organe_relation', type_='primary')

    # Create a new primary key constraint including 'qualite'
    op.create_primary_key(
        'organe_relation_pkey',
        'organe_relation',
        ['organe_id', 'hopol_id', 'qualite']
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the composite primary key with 'qualite'
    op.drop_constraint('organe_relation_pkey', 'organe_relation', type_='primary')

    # Recreate the original primary key constraint without 'qualite'
    op.create_primary_key(
        'organe_relation_pkey',
        'organe_relation',
        ['organe_id', 'hopol_id']
    )