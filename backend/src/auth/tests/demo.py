# import logging
#
# from fastapi import FastAPI, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from jose import JWTError, jwt
# from pydantic import BaseModel, ConfigDict
# from datetime import datetime, timedelta
# import pytz
# from typing import Optional
#
# # SQLAlchemy 相关导入
# from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, func
# from sqlalchemy.orm import declarative_base
# from sqlalchemy.orm import sessionmaker, Session
#
# # 密码哈希
# from passlib.context import CryptContext
#
# # 邮件相关
# import smtplib
# from email.mime.text import MIMEText
# from email.header import Header
# import random
#
# # ---------------------------
# # 配置部分
# # ---------------------------
#
# # 设置 root logger 的级别为 INFO
# logging.basicConfig(level=logging.INFO)
#
# # 加密密钥和算法
# SECRET_KEY = "your-secret-key-here"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30
#
# # 数据库连接配置（请根据你的数据库信息修改）
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:123456@127.0.0.1:3306/toolkit_hub?charset=utf8mb4"
#
# engine = create_engine(SQLALCHEMY_DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()
#
# # 密码哈希工具
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#
# # OAuth2 配置
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
#
# app = FastAPI()
#
#
# # ---------------------------
# # 数据模型定义 (Pydantic)
# # ---------------------------
#
# class Token(BaseModel):
#     access_token: str
#     token_type: str
#
#
# class TokenData(BaseModel):
#     username: Optional[str] = None
#
#
# class UserBase(BaseModel):
#     username: str
#     nickname: str
#     email: str
#     phone_number: str
#
#
# class UserCreate(UserBase):
#     password: str
#
#
# class VerificationCodeRequest(BaseModel):
#     email: str
#
#
# class RegisterRequest(UserCreate):
#     code: str
#
#
# class User(BaseModel):
#     id: int
#     username: str
#     nickname: str
#     email: str
#     phone_number: str
#     is_active: bool
#     created_at: datetime
#     updated_at: datetime
#
#     model_config = ConfigDict(from_attributes=True)
#
#
# class UserInLogin(BaseModel):
#     username: str
#     password: str
#
#
# # ---------------------------
# # 数据库模型定义 (SQLAlchemy)
# # ---------------------------
#
# class UserDB(Base):
#     __tablename__ = 'users'
#
#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String(50), unique=True, index=True, nullable=False)
#     nickname = Column(String(100), nullable=False)
#     password = Column(String(255), nullable=False)
#     email = Column(String(100), unique=True, index=True, nullable=False)
#     phone_number = Column(String(20), default='')
#     is_active = Column(Boolean, default=True)
#     created_at = Column(DateTime, default=func.now())
#     updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
#
#
# class VerificationCodeDB(Base):
#     __tablename__ = 'verification_codes'
#
#     id = Column(Integer, primary_key=True)
#     email = Column(String(100), unique=True, nullable=False)
#     code = Column(String(6), nullable=False)
#     expires_at = Column(DateTime, nullable=False)
#
#
# # ---------------------------
# # 工具函数
# # ---------------------------
#
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#
#
# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)
#
#
# def get_password_hash(password):
#     return pwd_context.hash(password)
#
#
# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.now(pytz.timezone('Asia/Shanghai')) + expires_delta
#     else:
#         expire = datetime.now(pytz.timezone('Asia/Shanghai')) + timedelta(minutes=15)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt
#
#
# def get_user_by_username(db: Session, username: str):
#     return db.query(UserDB).filter(UserDB.username == username).first()
#
#
# def authenticate_user(db: Session, username: str, password: str):
#     user = get_user_by_username(db, username)
#     if not user:
#         return None
#     if not verify_password(password, user.password):
#         return None
#     return user
#
#
# async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception
#     user = get_user_by_username(db, username=username)
#     if user is None:
#         raise credentials_exception
#     return user
#
#
# # ---------------------------
# # 邮件服务
# # ---------------------------
#
# def send_verification_email(email: str, code: str):
#     sender = "your@qq.com"  # 替换为你的 QQ 邮箱
#     password = "your_authorization_code"  # 替换为你的授权码
#
#     msg = MIMEText(f"你的验证码是：{code}", 'plain', 'utf-8')
#     logging.info("Sending verification email to %s with code %s", email, code)
#     msg['From'] = Header(sender)
#     msg['To'] = Header(email)
#     msg['Subject'] = Header("注册验证码")
#
#     try:
#         server = smtplib.SMTP_SSL("smtp.qq.com", 465)
#         server.login(sender, password)
#         server.sendmail(sender, [email], msg.as_string())
#         server.quit()
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
#
#
# # ---------------------------
# # 路由接口
# # ---------------------------
#
# @app.post("/send-code")
# def send_verification_code(request: VerificationCodeRequest, db: Session = Depends(get_db)):
#     email = request.email
#
#     existing_user = db.query(UserDB).filter(UserDB.email == email).first()
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
#
#     code = ''.join(random.choices('0123456789', k=6))
#     expires_at = datetime.now(pytz.timezone('Asia/Shanghai')) + timedelta(minutes=3)
#
#     db_code = db.query(VerificationCodeDB).filter(VerificationCodeDB.email == email).first()
#     if db_code:
#         db_code.code = code
#         db_code.expires_at = expires_at
#     else:
#         db_code = VerificationCodeDB(email=email, code=code, expires_at=expires_at)
#         db.add(db_code)
#
#     db.commit()
#
#     send_verification_email(email, code)
#
#     return {"message": "Verification code sent"}
#
#
# @app.post("/register", response_model=User)
# def register(request: RegisterRequest, db: Session = Depends(get_db)):
#     user = request
#     code = request.code
#
#     db_user = get_user_by_username(db, user.username)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Username already registered")
#
#     verification = db.query(VerificationCodeDB).filter(VerificationCodeDB.email == user.email).first()
#     if not verification or verification.code != code:
#         raise HTTPException(status_code=400, detail="Invalid or missing verification code")
#
#     if verification.expires_at < datetime.now(pytz.timezone('Asia/Shanghai')).replace(tzinfo=None):
#         raise HTTPException(status_code=400, detail="Verification code expired")
#
#     db.delete(verification)
#
#     hashed_password = get_password_hash(user.password)
#     db_user = UserDB(**user.model_dump(exclude={'password', 'code'}), password=hashed_password)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user
#
#
# @app.post("/login", response_model=Token)
# def login_for_access_token(login_data: UserInLogin, db: Session = Depends(get_db)):
#     user = authenticate_user(db, login_data.username, login_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.username},
#         expires_delta=access_token_expires
#     )
#     return {"access_token": access_token, "token_type": "bearer"}
#
#
# @app.get("/users/me/", response_model=User)
# def read_users_me(current_user: User = Depends(get_current_user)):
#     return current_user
#
#
# # 启动命令
# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run(app, host="127.0.0.1", port=8000)
