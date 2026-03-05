"""
自定义异常类层次
统一的业务异常定义，配合全局异常处理器使用
"""


class AppException(Exception):
    """应用异常基类"""

    def __init__(self, detail: str, code: str, status_code: int = 400):
        self.detail = detail
        self.code = code
        self.status_code = status_code
        super().__init__(detail)


class AuthenticationError(AppException):
    """认证失败异常 (401)"""

    def __init__(self, detail: str = "认证失败", code: str = "UNAUTHORIZED"):
        super().__init__(detail=detail, code=code, status_code=401)


class AuthorizationError(AppException):
    """权限不足异常 (403)"""

    def __init__(self, detail: str = "权限不足", code: str = "FORBIDDEN"):
        super().__init__(detail=detail, code=code, status_code=403)


class ConflictError(AppException):
    """资源冲突异常 (409)"""

    def __init__(self, detail: str = "资源冲突", code: str = "CONFLICT"):
        super().__init__(detail=detail, code=code, status_code=409)


class LockedError(AppException):
    """账户锁定异常 (423)"""

    def __init__(self, detail: str = "账户已锁定", code: str = "ACCOUNT_LOCKED"):
        super().__init__(detail=detail, code=code, status_code=423)


class PreconditionError(AppException):
    """前置条件异常 (428)，如需要验证码"""

    def __init__(self, detail: str = "需要满足前置条件", code: str = "PRECONDITION_REQUIRED"):
        super().__init__(detail=detail, code=code, status_code=428)


class RateLimitError(AppException):
    """频率限制异常 (429)"""

    def __init__(self, detail: str = "请求过于频繁，请稍后重试", code: str = "RATE_LIMITED"):
        super().__init__(detail=detail, code=code, status_code=429)
