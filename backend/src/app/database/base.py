"""
database/base.py - ORMベースクラス
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """全SQLAlchemyモデルの基底クラス"""

    pass
