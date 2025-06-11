# src/auth/routers.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from auth.services import (
    authenticate_user,
    register_user,
    send_verification_code,
    create_access_token,
    get_current_user_info,
)
from database import get_db
from models.user import UserDB
from schemas.auth import UserLoginRequest, RegisterRequest, VerificationCodeRequest, Token, User, UserLoginResponse, \
    UserBase
from schemas.result import Result

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/send-code")
def send_code(request: VerificationCodeRequest, db: Session = Depends(get_db)):
    send_verification_code(db, request.email)
    return Result.succ(data="Verification code sent successfully")


@router.post("/login", response_model=Result[UserLoginResponse])
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return Result.succ(
        data=UserLoginResponse(
            username=user.username,
            nickname=user.nickname,
            token_type="bearer",
            access_token=access_token
        )
    )


@router.post("/register", response_model=Result[str])
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    register_status = register_user(
        db=db,
        username=request.username,
        nickname=request.nickname,
        email=request.email,
        phone_number=request.phone_number,
        password=request.password,
        code=request.code
    )
    if register_status:
        return Result.succ(data="User registered successfully")
    else:
        return Result.failed(msg="User registration failed")


@router.get("/users/me/", response_model=Result[UserBase])
def read_users_me(current_user: UserDB = Depends(get_current_user)):
    return Result.succ(data=get_current_user_info(current_user))
