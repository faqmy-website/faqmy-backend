"""Added stack's new fields: color and widget_delay

Revision ID: 0002
Revises: 0001
Create Date: 2023-02-25 00:13:18.874885

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('stacks', sa.Column('widget_delay', sa.Integer(), nullable=True))
    op.add_column('stacks', sa.Column('color', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('stacks', 'color')
    op.drop_column('stacks', 'widget_delay')
    # ### end Alembic commands ###
