"""Edit table columns

Revision ID: 78ecb0186b17
Revises: 
Create Date: 2023-07-27 09:16:39.722863

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '78ecb0186b17'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('user_id', sa.Integer(), nullable=True))
    op.add_column('order', sa.Column('amount_paid', sa.Float(), nullable=True))
    op.create_foreign_key(None, 'order', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'order', type_='foreignkey')
    op.drop_column('order', 'amount_paid')
    op.drop_column('order', 'user_id')
    # ### end Alembic commands ###
