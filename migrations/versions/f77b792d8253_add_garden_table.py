"""add garden table

Revision ID: f77b792d8253
Revises: 131e34f63026
Create Date: 2018-04-02 22:53:56.682123

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f77b792d8253'
down_revision = '131e34f63026'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('garden',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=140), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_garden_created'), 'garden', ['created'], unique=False)
    op.create_index(op.f('ix_garden_name'), 'garden', ['name'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_garden_name'), table_name='garden')
    op.drop_index(op.f('ix_garden_created'), table_name='garden')
    op.drop_table('garden')
    # ### end Alembic commands ###
