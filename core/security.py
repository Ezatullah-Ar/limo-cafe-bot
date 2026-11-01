"""
ماژول کنترل دسترسی و امنیت سامانه «کافی نت لیمو»
این ماژول قوانین امنیتی مبتنی بر نقش را اعمال کرده و از دسترسی غیرمجاز جلوگیری می‌کند.
"""

import logging
from typing import Optional
from core.config import Settings

logger = logging.getLogger("security")


class SecurityError(Exception):
    """خطای پایه امنیتی سامانه."""
    pass


class AccessDeniedError(SecurityError):
    """خطای عدم احراز صلاحیت برای انجام عملیات حساس یا مدیریتی."""
    pass


class AccessControl:
    """
    سرویس کنترل دسترسی سامانه.
    از خط‌مشی Default-Deny پیروی می‌کند: هرگونه دسترسی بدون تایید صریح شناسه مدیر مسدود است.
    """

    def __init__(self, settings: Settings):
        self._settings = settings

    @property
    def admin_id(self) -> int:
        """شناسه عددی تلگرام مدیر ارشد سامانه."""
        return self._settings.admin_id

    def is_admin(self, user_id: Optional[int]) -> bool:
        """بررسی سطح دسترسی کاربر به امکانات مدیریتی."""
        return self._settings.is_admin(user_id)

    def verify_admin_access(self, user_id: Optional[int], action_name: str = "unspecified") -> bool:
        """
        بررسی دسترسی مدیر همراه با ثبت وقایع امنیتی (Security Audit Logging).
        در صورت عدم احراز دسترسی، رویداد در لاگ امنیتی ثبت شده و خطا پرتاب می‌شود.
        """
        if self.is_admin(user_id):
            logger.info("Admin access granted: user_id=%s action=%s", user_id, action_name)
            return True

        logger.warning(
            "SECURITY ALERT: Unauthorized admin access attempt. user_id=%s action=%s",
            user_id,
            action_name
        )
        raise AccessDeniedError(
            f"دسترسی غیرمجاز: کاربر با شناسه {user_id} مجاز به انجام عملیات '{action_name}' نیست."
        )
