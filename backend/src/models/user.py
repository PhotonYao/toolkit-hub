# user.py
# 用户模型
"""
定义用户数据库模型，包含用户的基本信息和认证相关字段。
例如：用户名、邮箱、密码哈希等。
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from database import Base


class UserDB(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    nickname = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone_number = Column(String(20), default='')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
