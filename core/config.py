"""
ماژول پیکربندی و تنظیمات سامانه «کافی نت لیمو»
این ماژول متغیرهای محیطی را با استفاده از Pydantic Settings بارگذاری و اعتبارسنجی می‌کند.
اطلاعات حساس (مانند توکن ربات و شناسه مدیر) خارج از کد نگهداری می‌شوند.
"""

from functools import lru_cache
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    کلاس تنظیمات سامانه.
    تمام مقادیر به صورت پیش‌فرض امن طراحی شده‌اند و دسترسی‌ها پیش‌فرض-بسته (Default-Deny) هستند.
    """
    bot_token: str = Field(
        default="",
        description="توکن ربات تلگرام دریافت شده از BotFather"
    )
    admin_id: Optional[int] = Field(
        default=None,
        description="شناسه عددی یکتای مدیر سیستم در تلگرام"
    )
    timezone: str = Field(
        default="Asia/Tehran",
        description="منطقه زمانی استاندارد سامانه"
    )
    environment: str = Field(
        default="development",
        description="محیط اجرا: development | production | test"
    )
    database_url: str = Field(
        default="sqlite:///storage/limo.db",
        description="نشانی اتصال به پایگاه داده (پیش‌فرض محلی: SQLite در پوشه storage)"
    )
    google_sheet_url: Optional[str] = Field(
        default=None,
        description="نشانی وب‌هوک Google Apps Script جهت همگام‌سازی ابری سفارش‌ها با اکسل/گوگل شیت"
    )
    webapp_url: Optional[str] = Field(
        default=None,
        description="نشانی دامنه میزبانی مینی‌اپلیکیشن تلگرام (WebApps)"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator("admin_id")
    @classmethod
    def validate_admin_id(cls, v: Optional[int]) -> Optional[int]:
        """اعتبارسنجی شناسه مدیر: شناسه عددی باید یک عدد صحیح مثبت باشد."""
        if v is not None and v <= 0:
            raise ValueError("شناسه مدیر (admin_id) باید یک عدد صحیح مثبت معتبر باشد.")
        return v

    def is_admin_configured(self) -> bool:
        """بررسی اینکه آیا مدیر سیستم صریحاً پیکربندی شده است یا خیر."""
        return self.admin_id is not None and self.admin_id > 0

    def is_admin(self, user_id: Optional[int]) -> bool:
        """
        بررسی دسترسی مدیریتی کاربر بر اساس خط‌مشی Default-Deny.
        تنها در صورتی که شناسه مدیر صریحاً تنظیم شده باشد و شناسه کاربر دقیقاً برابر آن باشد،
        دسترسی تایید می‌شود. در تمامی موارد دیگر (عدم تنظیم مدیر، شناسه نامعتبر، عدم تطابق)، دسترسی رد می‌شود.
        """
        if not self.is_admin_configured():
            return False
        if user_id is None or user_id <= 0:
            return False
        return user_id == self.admin_id


@lru_cache
def get_settings() -> Settings:
    """دریافت نمونه سراسری تنظیمات به صورت کش‌شده."""
    return Settings()
