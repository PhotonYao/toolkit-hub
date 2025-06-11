# src/auth/services.py
import logging
from datetime import datetime, timedelta
from typing import Optional
import random

import pytz
from fastapi import HTTPException
from passlib.context import CryptContext
from jose import jwt
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from core.config import settings
from models.user import UserDB
from models.tool_usage import VerificationCodeDB
from auth.utils import get_password_hash, verify_password, send_verification_email

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if not user or not verify_password(password, user.password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    # 实现 token 创建逻辑
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(pytz.timezone('Asia/Shanghai')) + expires_delta
    else:
        expire = datetime.now(pytz.timezone('Asia/Shanghai')) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def register_user(db: Session, username, nickname, email, phone_number, password, code):
    # 实现注册逻辑
    db_user = db.query(UserDB).filter(UserDB.username == username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    verification = db.query(VerificationCodeDB).filter(VerificationCodeDB.email == email).first()
    if not verification or verification.code != code:
        return HTTPException(status_code=400, detail="Invalid verification code")

    if verification.expires_at < datetime.now(pytz.timezone('Asia/Shanghai')).replace(tzinfo=None):
        return HTTPException(status_code=400, detail="Verification code has expired")

    db.delete(verification)

    hashed_password = get_password_hash(password)
    # 创建用户对象
    db_user = UserDB(
        username=username,
        nickname=nickname,
        email=email,
        phone_number=phone_number,
        password=hashed_password
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logging.error("Error registering user:",e)
        return False


def send_verification_code(db: Session, email: str):
    try:
        existing_user = db.query(UserDB).filter(UserDB.email == email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        code = ''.join(random.choices('0123456789', k=6))
        expires_at = datetime.now(pytz.timezone('Asia/Shanghai')) + timedelta(minutes=3)

        db_code = db.query(VerificationCodeDB).filter(VerificationCodeDB.email == email).first()
        if db_code:
            db_code.code = code
            db_code.expires_at = expires_at
        else:
            db_code = VerificationCodeDB(email=email, code=code, expires_at=expires_at)
            db.add(db_code)

        db.commit()

        send_verification_email(email, code)

        return True
    except SQLAlchemyError as e:
        db.rollback()
        logging.error("Error sending verification code:",e)
        return False
def get_current_user_info(user: UserDB) -> dict:
    return {
        "username": user.username,
        "nickname": user.nickname,
        "email": user.email,
        "phone_number": user.phone_number
    }
