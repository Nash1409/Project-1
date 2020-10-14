"""empty message

Revision ID: 5cfa210409e9
Revises: dc1b4085b664
Create Date: 2020-10-14 10:16:22.240864

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5cfa210409e9'
down_revision = 'dc1b4085b664'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'seeking_venue')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('seeking_venue', sa.BOOLEAN(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
