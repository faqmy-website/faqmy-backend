"""Set foreignkey cascade policy

Revision ID: 0004
Revises: 0003
Create Date: 2023-03-02 19:48:11.817773

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('conversations_stack_id_fkey', 'conversations', type_='foreignkey')
    op.create_foreign_key(None, 'conversations', 'stacks', ['stack_id'], ['id'], ondelete='cascade')
    op.drop_constraint('messages_conversation_id_fkey', 'messages', type_='foreignkey')
    op.create_foreign_key(None, 'messages', 'conversations', ['conversation_id'], ['id'], ondelete='cascade')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'messages', type_='foreignkey')
    op.create_foreign_key('messages_conversation_id_fkey', 'messages', 'conversations', ['conversation_id'], ['id'])
    op.drop_constraint(None, 'conversations', type_='foreignkey')
    op.create_foreign_key('conversations_stack_id_fkey', 'conversations', 'stacks', ['stack_id'], ['id'])
    # ### end Alembic commands ###
