"""
آزمون‌های خودکار ماژول کنترل نرخ ارسال و مهار اسپم (core/throttling.py)
"""

import unittest
from core.throttling import Throttler


class TestThrottler(unittest.TestCase):
    """مجموعه آزمون‌های رفتار الگوریتم کنترل نرخ ارسال."""

    def setUp(self):
        # ساخت نمونه با تنظیمات معین: حداقل 1 ثانیه بین پیام‌ها، سقف 3 پیام در بازه
        self.throttler = Throttler(rate_limit_seconds=1.0, max_burst=3)
        self.user_a = 1001
        self.user_b = 2002

    def test_single_request_allowed(self):
        """آزمون ارسال تک‌درخواست اول: باید بدون وقفه تایید شود."""
        allowed, wait_time = self.throttler.is_allowed(self.user_a, current_time=100.0)
        self.assertTrue(allowed)
        self.assertEqual(wait_time, 0.0)

    def test_immediate_second_request_throttled(self):
        """آزمون ارسال رگباری بلافاصله پس از درخواست اول: باید مسدود شود."""
        self.throttler.is_allowed(self.user_a, current_time=100.0)

        # درخواست دوم پس از 0.2 ثانیه (کمتر از حد مجاز 1.0 ثانیه)
        allowed, wait_time = self.throttler.is_allowed(self.user_a, current_time=100.2)
        self.assertFalse(allowed)
        self.assertGreater(wait_time, 0.0)
        self.assertAlmostEqual(wait_time, 0.8, places=1)

    def test_request_allowed_after_interval(self):
        """آزمون ارسال درخواست با رعایت فاصله زمانی قانونی: باید تایید شود."""
        self.throttler.is_allowed(self.user_a, current_time=100.0)

        # درخواست دوم پس از 1.1 ثانیه
        allowed, wait_time = self.throttler.is_allowed(self.user_a, current_time=101.1)
        self.assertTrue(allowed)
        self.assertEqual(wait_time, 0.0)

    def test_users_are_isolated(self):
        """آزمون ایزوله بودن کاربران: مهار کاربر A نباید مانع ارسال کاربر B شود."""
        # کاربر A درخواست می‌دهد
        self.throttler.is_allowed(self.user_a, current_time=100.0)

        # بلافاصله کاربر A مجدداً درخواست می‌دهد و مسدود می‌شود
        allowed_a, _ = self.throttler.is_allowed(self.user_a, current_time=100.1)
        self.assertFalse(allowed_a)

        # اما در همان لحظه، کاربر B باید مجاز باشد
        allowed_b, wait_b = self.throttler.is_allowed(self.user_b, current_time=100.1)
        self.assertTrue(allowed_b)
        self.assertEqual(wait_b, 0.0)

    def test_burst_limit_enforced(self):
        """آزمون سقف هجوم (Burst Limit): حداکثر 3 پیام در پنجره 3 ثانیه‌ای."""
        # سه پیام با رعایت فواصل 1 ثانیه‌ای
        self.assertTrue(self.throttler.is_allowed(self.user_a, current_time=100.0)[0])
        self.assertTrue(self.throttler.is_allowed(self.user_a, current_time=101.1)[0])
        self.assertTrue(self.throttler.is_allowed(self.user_a, current_time=102.2)[0])

        # پیام چهارم در ثانیه 102.5 (پر شدن ظرفیت 3 در پنجره)
        allowed, wait_time = self.throttler.is_allowed(self.user_a, current_time=102.5)
        self.assertFalse(allowed)
        self.assertGreater(wait_time, 0.0)

    def test_reset_clears_history(self):
        """آزمون ریست کردن سوابق اسپم کاربر."""
        self.throttler.is_allowed(self.user_a, current_time=100.0)
        self.throttler.reset(self.user_a)

        # پس از ریست، بلافاصله باید بتواند پیام ارسال کند
        allowed, _ = self.throttler.is_allowed(self.user_a, current_time=100.1)
        self.assertTrue(allowed)


if __name__ == "__main__":
    unittest.main()
