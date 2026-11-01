"""
آزمون‌های خودکار ماژول تنظیمات (core/config.py)
این آزمون‌ها بدون وابستگی به شبکه و با داده‌های تستی ایزوله اجرا می‌شوند.
"""

import unittest
from core.config import Settings


class TestConfig(unittest.TestCase):
    """مجموعه آزمون‌های اعتبارسنجی تنظیمات و خط‌مشی امنیتی مدیر."""

    def test_default_settings_security(self):
        """آزمون مقادیر پیش‌فرض: در غیاب تنظیمات، دسترسی مدیر باید کاملاً مسدود باشد."""
        settings = Settings(bot_token="", admin_id=None)
        self.assertFalse(settings.is_admin_configured())
        self.assertFalse(settings.is_admin(123456))
        self.assertFalse(settings.is_admin(None))
        self.assertFalse(settings.is_admin(0))
        self.assertEqual(settings.timezone, "Asia/Tehran")

    def test_configured_admin_access(self):
        """آزمون احراز صلاحیت مدیر هنگام پیکربندی صحیح شناسه یکتا."""
        configured_admin_id = 987654321
        settings = Settings(bot_token="fake_test_token", admin_id=configured_admin_id)

        # فقط شناسه ثبت‌شده باید تایید شود
        self.assertTrue(settings.is_admin_configured())
        self.assertTrue(settings.is_admin(configured_admin_id))

        # تمام کاربران دیگر باید اکیداً رد شوند
        self.assertFalse(settings.is_admin(111111))
        self.assertFalse(settings.is_admin(None))
        self.assertFalse(settings.is_admin(0))
        self.assertFalse(settings.is_admin(-1))

    def test_invalid_admin_id_validation(self):
        """آزمون رد شناسه نامعتبر (صفر یا منفی) در اعتبارسنجی ورودی."""
        with self.assertRaises(ValueError):
            Settings(admin_id=0)

        with self.assertRaises(ValueError):
            Settings(admin_id=-100)


if __name__ == "__main__":
    unittest.main()
