"""empty message

Revision ID: acaa8f6f84b7
Revises: 74c189400a1b
Create Date: 2020-10-23 12:05:20.810780

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'acaa8f6f84b7'
down_revision = '74c189400a1b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('todos', 'todolist_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('todos', 'todolist_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
