"""Remove language field from user_settings

Revision ID: 002
Revises: 001
Create Date: 2025-10-16 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """言語フィールドを削除"""
    op.drop_column('user_settings', 'language')


def downgrade() -> None:
    """言語フィールドを復元"""
    op.add_column(
        'user_settings',
        op.Column('language', op.String(length=10), nullable=False, server_default='ja')
    )
