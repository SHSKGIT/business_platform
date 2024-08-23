"""create subscribe email relationship

Revision ID: 738224e87f84
Revises: 5772edccfb1c
Create Date: 2024-08-18 14:53:51.532814

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '738224e87f84'
down_revision: Union[str, None] = '5772edccfb1c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('email', sa.Column('subscribe_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'email', 'subscribe', ['subscribe_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'email', type_='foreignkey')
    op.drop_column('email', 'subscribe_id')
    # ### end Alembic commands ###
