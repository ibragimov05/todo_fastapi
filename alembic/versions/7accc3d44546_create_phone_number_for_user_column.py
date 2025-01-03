"""CREATE phone number for user column

Revision ID: 7accc3d44546
Revises: 
Create Date: 2025-01-03 19:17:50.126206

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '7accc3d44546'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.add_column('users', sa.Column('phone_number', sa.String(), nullable=True))


def downgrade() -> None:
	op.drop_column('users', 'phone_number')
