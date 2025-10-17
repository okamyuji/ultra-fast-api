"""Remove notifications_enabled field from user_settings

Revision ID: 003
Revises: 002
Create Date: 2025-10-16 14:30:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """通知機能フィールドを削除"""
    op.drop_column("user_settings", "notifications_enabled")


def downgrade() -> None:
    """通知機能フィールドを復元"""
    op.add_column(
        "user_settings",
        op.Column(
            "notifications_enabled",
            op.Boolean(),
            nullable=False,
            server_default="true",
        ),
    )
