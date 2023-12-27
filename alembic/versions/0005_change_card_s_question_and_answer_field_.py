"""Change card's question and answer field to text

Revision ID: 0005
Revises: 0004
Create Date: 2023-03-12 14:16:30.591276

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('cards', 'question',
        existing_type=sa.VARCHAR(length=255),
        type_=sa.Text()
    )
    op.alter_column('cards', 'answer',
        existing_type=sa.VARCHAR(length=255),
        type_=sa.Text()
    )


def downgrade() -> None:
    op.alter_column('cards', 'question',
        existing_type=sa.Text(),
        type_=sa.VARCHAR(length=255)
    )
    op.alter_column('cards', 'answer',
        existing_type=sa.Text(),
        type_=sa.VARCHAR(length=255),
    )
