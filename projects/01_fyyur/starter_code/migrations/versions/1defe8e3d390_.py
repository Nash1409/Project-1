"""empty message

Revision ID: 1defe8e3d390
Revises: 5cfa210409e9
Create Date: 2020-10-14 10:16:50.512062

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1defe8e3d390'
down_revision = '5cfa210409e9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'seeking_talent')
    # ### end Alembic commands ###
