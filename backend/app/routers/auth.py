"""
认证 API 路由
包含注册、登录、登出、Token 刷新、用户信息、密码修改、2FA、设备管理等端点
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.core.deps import get_current_active_user
from app.core.memory_store import UserData
from app.schemas.auth import (
    ChangePasswordRequest,
    DeviceResponse,
    LoginRequest,
    LoginResponse,
    RecoveryCodesResponse,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    TwoFactorDisableRequest,
    TwoFactorEnableRequest,
    TwoFactorEnableResponse,
    TwoFactorSetupResponse,
    TwoFactorVerifyRequest,
    UserResponse,
)
from app.schemas.common import MessageResponse
from app.services.auth_service import AuthService
from app.services.two_factor_service import TwoFactorService
from app.services.user_service import UserService

router = APIRouter(prefix="/api/auth", tags=["认证"])


def _get_device_info(request: Request) -> tuple[str, str | None]:
    """从请求中提取设备信息"""
    user_agent = request.headers.get("user-agent", "未知设备")
    device_name = user_agent[:100] if user_agent else "未知设备"
    ip_address = request.client.host if request.client else None
    return device_name, ip_address


# ==================== 注册/登录/登出 ====================

@router.post("/register", response_model=TokenResponse, summary="用户注册")
async def register(data: RegisterRequest, request: Request):
    """用户注册，创建账户并返回 Token"""
    device_name, ip_address = _get_device_info(request)
    service = AuthService()
    return await service.register(
        data=data, device_id=request.headers.get("x-device-id"),
        device_name=device_name, ip_address=ip_address,
    )


@router.post("/login", response_model=LoginResponse, summary="用户登录")
async def login(data: LoginRequest, request: Request):
    """用户登录，验证密码后返回 Token"""
    device_name, ip_address = _get_device_info(request)
    service = AuthService()
    return await service.login(data=data, device_name=device_name, ip_address=ip_address)


@router.post("/2fa/verify", response_model=TokenResponse, summary="2FA 登录验证")
async def verify_2fa_login(data: TwoFactorVerifyRequest, request: Request):
    """登录时的 2FA 验证（第二步）"""
    device_name, ip_address = _get_device_info(request)
    service = AuthService()
    return await service.verify_2fa_login(
        temp_token=data.temp_token, code=data.code,
        device_id=request.headers.get("x-device-id"),
        device_name=device_name, ip_address=ip_address,
    )


@router.post("/refresh", response_model=TokenResponse, summary="刷新 Token")
async def refresh_token(data: RefreshTokenRequest):
    """使用 Refresh Token 获取新的 Access Token"""
    service = AuthService()
    return await service.refresh_token(data.refresh_token)


@router.post("/logout", response_model=MessageResponse, summary="用户登出")
async def logout(current_user: UserData = Depends(get_current_active_user)):
    """用户登出"""
    return MessageResponse(message="登出成功")


# ==================== 用户信息 ====================

@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_me(current_user: UserData = Depends(get_current_active_user)):
    """获取当前登录用户的信息"""
    service = UserService()
    return await service.get_user_info(current_user)


@router.put("/password", response_model=MessageResponse, summary="修改密码")
async def change_password(
    data: ChangePasswordRequest,
    current_user: UserData = Depends(get_current_active_user),
):
    """修改当前用户密码"""
    service = UserService()
    await service.change_password(current_user, data.old_password, data.new_password)
    return MessageResponse(message="密码修改成功")


# ==================== 2FA 管理 ====================

@router.post("/2fa/setup", response_model=TwoFactorSetupResponse, summary="设置 2FA")
async def setup_2fa(current_user: UserData = Depends(get_current_active_user)):
    """生成 2FA 密钥和二维码"""
    service = TwoFactorService()
    result = await service.setup_2fa(current_user)
    return TwoFactorSetupResponse(**result)


@router.post("/2fa/enable", response_model=TwoFactorEnableResponse, summary="启用 2FA")
async def enable_2fa(
    data: TwoFactorEnableRequest,
    current_user: UserData = Depends(get_current_active_user),
):
    """验证首次 TOTP 码并启用 2FA"""
    service = TwoFactorService()
    codes = await service.enable_2fa(current_user, data.secret, data.code)
    return TwoFactorEnableResponse(recovery_codes=codes)


@router.post("/2fa/disable", response_model=MessageResponse, summary="禁用 2FA")
async def disable_2fa(
    data: TwoFactorDisableRequest,
    current_user: UserData = Depends(get_current_active_user),
):
    """禁用两步验证"""
    service = TwoFactorService()
    await service.disable_2fa(current_user, data.code)
    return MessageResponse(message="两步验证已禁用")


@router.get("/2fa/recovery-codes", response_model=RecoveryCodesResponse, summary="获取恢复码")
async def get_recovery_codes(current_user: UserData = Depends(get_current_active_user)):
    """获取未使用的恢复码"""
    service = TwoFactorService()
    codes = await service.get_recovery_codes(current_user)
    return RecoveryCodesResponse(recovery_codes=codes)


@router.post("/2fa/recovery-codes/regenerate", response_model=RecoveryCodesResponse, summary="重新生成恢复码")
async def regenerate_recovery_codes(current_user: UserData = Depends(get_current_active_user)):
    """重新生成恢复码"""
    service = TwoFactorService()
    codes = await service.regenerate_recovery_codes(current_user)
    return RecoveryCodesResponse(recovery_codes=codes)


# ==================== 设备管理 ====================

@router.get("/devices", response_model=list[DeviceResponse], summary="获取设备列表")
async def get_devices(current_user: UserData = Depends(get_current_active_user)):
    """获取当前用户的登录设备列表"""
    service = UserService()
    return await service.get_devices(current_user.id)
