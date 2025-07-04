"""Ajout categorie proffession

Revision ID: a353e0499802
Revises: e4308996f903
Create Date: 2025-06-10 16:55:17.923499

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a353e0499802'
down_revision: Union[str, None] = 'e4308996f903'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('partipolitique',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('nom', sa.String(), nullable=True),
    sa.Column('date_creation', sa.Date(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('appartenanceparti',
    sa.Column('hopol_id', sa.String(), nullable=False),
    sa.Column('partie_id', sa.String(), nullable=False),
    sa.Column('date_appartenance', sa.Date(), nullable=True),
    sa.Column('date_quitte', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['hopol_id'], ['hommepolitique.hopol_id'], ),
    sa.ForeignKeyConstraint(['partie_id'], ['partipolitique.id'], ),
    sa.PrimaryKeyConstraint('hopol_id', 'partie_id')
    )
    op.add_column('organe_relation', sa.Column('date_debut', sa.Date(), nullable=True))
    op.add_column('organe_relation', sa.Column('date_fin', sa.Date(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('organe_relation', 'date_fin')
    op.drop_column('organe_relation', 'date_debut')
    op.drop_table('appartenanceparti')
    op.drop_table('partipolitique')
    # ### end Alembic commands ###
