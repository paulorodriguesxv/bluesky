"""Create users table

Revision ID: 655db8882733
Revises: 
Create Date: 2019-11-11 19:02:11.206233

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils

# revision identifiers, used by Alembic.
revision = '655db8882733'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users', sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column(
            'password',
            sqlalchemy_utils.types.encrypted.encrypted_type.EncryptedType(),
            nullable=False), sa.Column('email', sa.String(255),
                                       nullable=False),
        sa.Column('picture', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'))


def downgrade():
    op.drop_table('users')
