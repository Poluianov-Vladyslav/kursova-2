"""empty message

Revision ID: abc1f549c487
Revises: 9360bb564be5
Create Date: 2024-05-31 15:32:46.510279

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'abc1f549c487'
down_revision = '9360bb564be5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('review', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date_posted', sa.DateTime(), nullable=False))
        batch_op.add_column(sa.Column('content', sa.Text(), nullable=False))
        batch_op.alter_column('author',
               existing_type=sa.VARCHAR(length=100),
               type_=sa.String(length=20),
               existing_nullable=False)
        batch_op.drop_column('text')
        batch_op.drop_column('timestamp')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('review', schema=None) as batch_op:
        batch_op.add_column(sa.Column('timestamp', sa.DATETIME(), nullable=False))
        batch_op.add_column(sa.Column('text', sa.TEXT(), nullable=False))
        batch_op.alter_column('author',
               existing_type=sa.String(length=20),
               type_=sa.VARCHAR(length=100),
               existing_nullable=False)
        batch_op.drop_column('content')
        batch_op.drop_column('date_posted')

    # ### end Alembic commands ###
