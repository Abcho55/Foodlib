"""Initial migration.

Revision ID: 7acdc1de6894
Revises: 
Create Date: 2023-12-11 22:46:15.613499

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '7acdc1de6894'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('nutrition', schema=None) as batch_op:
        batch_op.add_column(sa.Column('nutrition', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('nutrition_data', sa.JSON(), nullable=True))
        batch_op.drop_column('ingredients')
        batch_op.drop_column('recipe_data')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('nutrition', schema=None) as batch_op:
        batch_op.add_column(sa.Column('recipe_data', mysql.JSON(), nullable=True))
        batch_op.add_column(sa.Column('ingredients', mysql.VARCHAR(length=500), nullable=True))
        batch_op.drop_column('nutrition_data')
        batch_op.drop_column('nutrition')

    # ### end Alembic commands ###