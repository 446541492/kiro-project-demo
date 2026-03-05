"""
SQLAlchemy 基础模型声明
所有数据模型继承此 Base 类
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy 声明式基类"""
    pass
