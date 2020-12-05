"""empty message

Revision ID: 1aff9af58f7f
Revises: 
Create Date: 2020-12-05 13:59:27.514855

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1aff9af58f7f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('preference', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category1', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('category2', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('category3', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('category4', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('category5', sa.String(length=200), nullable=True))
        batch_op.drop_column('ingredient')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('preference', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ingredient', sa.VARCHAR(length=200), nullable=False))
        batch_op.drop_column('category5')
        batch_op.drop_column('category4')
        batch_op.drop_column('category3')
        batch_op.drop_column('category2')
        batch_op.drop_column('category1')

    # ### end Alembic commands ###