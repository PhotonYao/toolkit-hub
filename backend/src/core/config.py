# config.py
# 全局配置加载
"""
全局配置文件，用于加载和管理应用的所有配置参数。
可以使用环境变量、配置文件等方式实现。
"""
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
import os

# 加载环境变量
load_dotenv()


class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-default-key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    DATABASE_URL: str = os.getenv("DATABASE_URL",
                                  "mysql+pymysql://root:password@127.0.0.1:3306/database?charset=utf8mb4")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.example.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 465))
    SMTP_USER: str = os.getenv("SMTP_USER", "your-smtp-user")
    SMTP_NAME: str = os.getenv("SMTP_NAME", "your-smtp-name")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "your-smtp-password")


settings = Settings()
