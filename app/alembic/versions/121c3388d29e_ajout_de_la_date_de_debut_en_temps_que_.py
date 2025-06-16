"""ajout de la date de debut en temps que primary key aussi

Revision ID: 121c3388d29e
Revises: a8bfef42f685
Create Date: 2025-06-12 15:25:19.624459

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '121c3388d29e'
down_revision: Union[str, None] = 'a8bfef42f685'
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
        ['organe_id', 'hopol_id', 'qualite','date_debut']
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the composite primary key with 'qualite'
    op.drop_constraint('organe_relation_pkey', 'organe_relation', type_='primary')

    # Recreate the original primary key constraint without 'qualite'
    op.create_primary_key(
        'organe_relation_pkey',
        'organe_relation',
        ['organe_id', 'hopol_id','qualite']
    )