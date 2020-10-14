"""empty message

Revision ID: 621fec962ea3
Revises: 0d027b0b517b
Create Date: 2020-10-14 10:10:51.401671

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '621fec962ea3'
down_revision = '0d027b0b517b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'seeking_talent')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('seeking_talent', sa.BOOLEAN(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
