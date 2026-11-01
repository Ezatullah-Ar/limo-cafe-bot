"""
آزمون‌های خودکار ماژول امنیت و کنترل دسترسی (core/security.py)
"""

import unittest
from core.config import Settings
from core.security import AccessControl, AccessDeniedError


class TestSecurity(unittest.TestCase):
    """مجموعه آزمون‌های رفتار سرویس کنترل دسترسی."""

    def test_default_deny_when_no_admin(self):
        """آزمون خط‌مشی Default-Deny: عدم امکان دسترسی هیچ کاربری در صورت خالی بودن شناسه مدیر."""
        settings = Settings(admin_id=None)
        ac = AccessControl(settings)

        self.assertFalse(ac.is_admin(12345))
        with self.assertRaises(AccessDeniedError):
            ac.verify_admin_access(12345, action_name="test_action")

    def test_admin_access_allowed(self):
        """آزمون احراز صلاحیت موفق برای مدیر واقعی."""
        admin_id = 555666777
        settings = Settings(admin_id=admin_id)
        ac = AccessControl(settings)

        self.assertTrue(ac.is_admin(admin_id))
        # نباید استثنا رخ دهد
        self.assertTrue(ac.verify_admin_access(admin_id, action_name="valid_action"))

    def test_unauthorized_user_blocked(self):
        """آزمون مهار کاربر غیرمجاز هنگامی که مدیر در سیستم تعریف شده است."""
        admin_id = 555666777
        intruder_id = 999000111
        settings = Settings(admin_id=admin_id)
        ac = AccessControl(settings)

        self.assertFalse(ac.is_admin(intruder_id))
        with self.assertRaises(AccessDeniedError):
            ac.verify_admin_access(intruder_id, action_name="view_sensitive_data")


if __name__ == "__main__":
    unittest.main()
