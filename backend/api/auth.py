"""认证API"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
)
from core.database import get_db
from models.user import User
from loguru import logger

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


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
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    """用户注册"""
    try:
        logger.info(f"用户注册: {user_data.username}")

        existing_stmt = select(User).where(
            or_(User.username == user_data.username, User.email == user_data.email)
        )
        existing_user = (await db.execute(existing_stmt)).scalar_one_or_none()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="用户名或邮箱已存在",
            )

        # 密码加密
        password_hash = get_password_hash(user_data.password)

        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=password_hash,
            full_name=user_data.full_name,
            phone=user_data.phone,
            status="active",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        return {
            "code": 200,
            "message": "注册成功",
            "data": {
                "user_id": user.id,
                "username": user_data.username,
                "email": user_data.email
            }
        }

    except Exception as e:
        await db.rollback()
        logger.error(f"注册失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="注册失败"
        )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """用户登录"""
    try:
        logger.info(f"用户登录: {form_data.username}")

        stmt = select(User).where(
            or_(User.username == form_data.username, User.email == form_data.username)
        )
        user = (await db.execute(stmt)).scalar_one_or_none()

        if not user or not verify_password(form_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if user.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账户不可用",
            )

        user.last_login_at = datetime.utcnow()
        await db.commit()

        # 创建访问令牌
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "phone": user.phone,
            }
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
async def get_current_user_info(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户信息"""
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        stmt = select(User).where(User.id == int(user_id))
        user = (await db.execute(stmt)).scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
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


class UserUpdate(BaseModel):
    """用户信息更新请求"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class PasswordChange(BaseModel):
    """密码修改请求"""
    old_password: str
    new_password: str


@router.put("/profile")
async def update_profile(
    user_data: UserUpdate,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """更新用户信息"""
    try:
        logger.info(f"更新用户信息")

        # 验证token
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        stmt = select(User).where(User.id == int(user_id))
        user = (await db.execute(stmt)).scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        if user_data.phone is not None:
            user.phone = user_data.phone
        if user_data.email is not None:
            email_stmt = select(User).where(User.email == user_data.email, User.id != user.id)
            email_taken = (await db.execute(email_stmt)).scalar_one_or_none()
            if email_taken:
                raise HTTPException(status_code=409, detail="邮箱已被使用")
            user.email = user_data.email

        await db.commit()
        await db.refresh(user)

        return {
            "code": 200,
            "message": "用户信息更新成功",
            "data": {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "email": user.email,
                "phone": user.phone,
            }
        }

    except Exception as e:
        await db.rollback()
        logger.error(f"更新用户信息失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="更新失败"
        )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """修改密码"""
    try:
        logger.info("修改密码")

        # 验证token
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        stmt = select(User).where(User.id == int(user_id))
        user = (await db.execute(stmt)).scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        if not verify_password(password_data.old_password, user.password_hash):
            raise HTTPException(status_code=400, detail="旧密码不正确")

        user.password_hash = get_password_hash(password_data.new_password)
        await db.commit()

        return {
            "code": 200,
            "message": "密码修改成功，请重新登录"
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"修改密码失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码不正确或修改失败"
        )


@router.post("/avatar")
async def upload_avatar(
    token: str = Depends(oauth2_scheme)
):
    """上传头像"""
    try:
        logger.info("上传头像")

        # TODO: 处理头像上传
        # 保存图片文件
        # 更新用户头像URL

        return {
            "code": 200,
            "message": "头像上传成功",
            "data": {
                "avatar_url": "/avatars/user_1.jpg"
            }
        }

    except Exception as e:
        logger.error(f"上传头像失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="上传失败"
        )
