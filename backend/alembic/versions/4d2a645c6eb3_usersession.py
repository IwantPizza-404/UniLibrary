"""userSession

Revision ID: 4d2a645c6eb3
Revises: 
Create Date: 2025-05-29 23:14:31.829346

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d2a645c6eb3'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'user_sessions', ['refresh_token'])
    op.create_foreign_key(None, 'user_sessions', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user_sessions', type_='foreignkey')
    op.drop_constraint(None, 'user_sessions', type_='unique')
    # ### end Alembic commands ###
