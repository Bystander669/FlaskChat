"""added the sqlmessagedatabase

Revision ID: 39363c514488
Revises: f57c3046483d
Create Date: 2023-12-26 22:53:28.542721

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '39363c514488'
down_revision = 'f57c3046483d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('custom_message_store')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('custom_message_store',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('session_id', mysql.TEXT(), nullable=True),
    sa.Column('type', mysql.TEXT(), nullable=True),
    sa.Column('content', mysql.TEXT(), nullable=True),
    sa.Column('created_at', mysql.DATETIME(), nullable=True),
    sa.Column('author_email', mysql.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###