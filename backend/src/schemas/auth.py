# auth.py
# 认证相关 Pydantic 模型
"""
定义认证相关的数据模型，用于请求和响应的数据验证。
例如：登录请求、注册请求、令牌响应等模型。
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(BaseModel):
    username: str
    nickname: str
    email: str
    phone_number: str


class UserCreate(UserBase):
    password: str


class VerificationCodeRequest(BaseModel):
    email: str


class RegisterRequest(UserCreate):
    code: str


class User(BaseModel):
    id: int
    username: str
    nickname: str
    email: str
    phone_number: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        model_config = ConfigDict(from_attributes=True)


class UserLoginRequest(BaseModel):
    username: str
    password: str


class UserLoginResponse(BaseModel):
    username: str
    nickname: str
    token_type: str = "bearer"
    access_token: str
