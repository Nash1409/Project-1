"""empty message

Revision ID: 60a8cf59c8e0
Revises: f9909b6e6147
Create Date: 2020-10-13 22:04:33.339444

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '60a8cf59c8e0'
down_revision = 'f9909b6e6147'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('start_time', sa.DateTime(), nullable=False))
    op.drop_column('Show', 'StartTime')
    op.drop_column('Show', 'id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"Show_id_seq"\'::regclass)'), autoincrement=True, nullable=False))
    op.add_column('Show', sa.Column('StartTime', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('Show', 'start_time')
    # ### end Alembic commands ###