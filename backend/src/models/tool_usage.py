# tool_usage.py
# 工具使用记录
"""
定义工具使用记录的数据库模型，用于追踪用户对各种工具的使用情况。
例如：使用的工具名称、使用时间、用户ID等信息。
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from database import Base


class VerificationCodeDB(Base):
    __tablename__ = 'verification_codes'

    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    code = Column(String(6), nullable=False)
    expires_at = Column(DateTime, nullable=False)
