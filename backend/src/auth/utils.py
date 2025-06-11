# utils.py
import logging
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr

from core.config import settings
from fastapi import HTTPException
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def send_verification_email(email: str, code: str):
    sender = settings.SMTP_USER
    sender_name = settings.SMTP_NAME
    password = settings.SMTP_PASSWORD

    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>Toolkit Hub 验证码</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f9f9f9;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background-color: #ffffff;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                padding: 30px;
            }}
            .header {{
                text-align: center;
                color: #333333;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
            }}
            .code {{
                display: inline-block;
                font-size: 22px;
                font-weight: bold;
                color: #007BFF;
                letter-spacing: 2px;
                margin: 20px 0;
                padding: 10px 20px;
                border: 1px dashed #007BFF;
                border-radius: 5px;
            }}
            .footer {{
                margin-top: 30px;
                font-size: 12px;
                color: #888888;
            }}
            a {{
                color: #007BFF;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">Toolkit Hub 验证码</div>

            <p>你好！你正在通过邮箱验证进行操作，你的验证码为：</p>

            <p class="code">{code}</p>

            <p>该验证码用于确认你的邮箱地址，仅限一次性使用，请勿泄露给他人。</p>

            <p>如果你未进行此操作，请忽略本邮件。</p>

            <div class="footer">
                <p>© 2025 Toolkit Hub. All rights reserved.</p>
                <p>站点地址：<a href="https://tool.kangyaocoding.top" target="_blank">Toolkit Hub</a></p>
                <p>开源地址：<a href="https://github.com/PhotonYao/toolkit-hub" target="_blank">GitHub</a></p>
            </div>
        </div>
    </body>
    </html>
    """

    msg = MIMEText(html_content, 'html', 'utf-8')
    logging.info("Sending verification email to %s with code %s", email, code)
    msg['From'] = formataddr((Header(sender_name, 'utf-8').encode(), sender))
    msg['To'] = Header(email)
    msg['Subject'] = Header("Toolkit Hub 邮箱验证码，请查收")

    try:
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)
        server.login(sender, password)
        server.sendmail(sender, [email], msg.as_string())
        server.quit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
