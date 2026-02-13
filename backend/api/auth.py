"""认证API"""
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import timedelta
from core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token
)
from core.config import settings
from loguru import logger

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


class UserRegister(BaseModel):
    """用户注册请求"""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserLogin(BaseModel):
    """用户登录请求"""
    username: str
    password: str


class Token(BaseModel):
    """令牌响应"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    phone: Optional[str]


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """用户注册"""
    try:
        logger.info(f"用户注册: {user_data.username}")

        # TODO: 检查用户名和邮箱是否已存在
        # from models.user import User
        # from core.database import AsyncSessionLocal
        # async with AsyncSessionLocal() as session:
        #     # 检查逻辑...

        # 密码加密
        password_hash = get_password_hash(user_data.password)

        # TODO: 保存用户到数据库
        # user = User(
        #     username=user_data.username,
        #     email=user_data.email,
        #     password_hash=password_hash,
        #     full_name=user_data.full_name,
        #     phone=user_data.phone
        # )
        # session.add(user)
        # await session.commit()
        # await session.refresh(user)

        # 返回结果（临时返回模拟数据）
        return {
            "code": 200,
            "message": "注册成功",
            "data": {
                "user_id": 1,
                "username": user_data.username,
                "email": user_data.email
            }
        }

    except Exception as e:
        logger.error(f"注册失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="注册失败"
        )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """用户登录"""
    try:
        logger.info(f"用户登录: {form_data.username}")

        # TODO: 从数据库验证用户
        # from models.user import User
        # from core.database import AsyncSessionLocal
        # async with AsyncSessionLocal() as session:
        #     # 查询用户逻辑...

        # 临时：模拟用户验证
        # 实际应该从数据库查询并验证密码
        if form_data.username == "admin" and form_data.password == "admin123":
            user_id = 1
            user_data_mock = {
                "id": 1,
                "username": "admin",
                "email": "admin@example.com"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 创建访问令牌
        access_token = create_access_token(
            data={"sub": str(user_id), "username": form_data.username}
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_data_mock
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"登录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(token: str = Depends(oauth2_scheme)):
    """获取当前用户信息"""
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        # TODO: 从数据库获取用户信息
        # from models.user import User
        # from core.database import AsyncSessionLocal
        # async with AsyncSessionLocal() as session:
        #     # 查询用户逻辑...

        # 临时返回模拟数据
        return UserResponse(
            id=int(user_id),
            username=payload.get("username"),
            email="admin@example.com",
            full_name="管理员",
            phone=None
        )

    except Exception as e:
        logger.error(f"获取用户信息失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据"
        )


@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    """用户登出"""
    try:
        # TODO: 将token加入黑名单（如果需要）
        logger.info("用户登出")
        return {
            "code": 200,
            "message": "登出成功"
        }
    except Exception as e:
        logger.error(f"登出失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登出失败"
        )
