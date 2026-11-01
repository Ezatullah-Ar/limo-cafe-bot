"""
ماژول کنترل نرخ ارسال و مهار اسپم (Throttling / Rate Limiting)
این ماژول از هجوم پیام‌های رگباری کاربران جلوگیری کرده و رفتار بات را با محدودیت‌های تلگرام هماهنگ می‌سازد.
"""

import time
from collections import defaultdict, deque
from typing import Dict, Tuple, Optional


class Throttler:
    """
    سرویس کنترل نرخ ارسال (Rate Limiter) بر پایه الگوریتم پنجره لغزان (Sliding Window).
    از ارسال رگباری پیام‌ها جلوگیری می‌کند و زمان انتظار لازم را محاسبه می‌نماید.
    """

    def __init__(self, rate_limit_seconds: float = 0.8, max_burst: int = 3):
        """
        مقداردهی اولیه:
        :param rate_limit_seconds: حداقل فاصله مجاز برحسب ثانیه بین پیام‌های متوالی
        :param max_burst: حداکثر تعداد پیام‌های مجاز در یک بازه کوتاه
        """
        self.rate_limit_seconds = rate_limit_seconds
        self.max_burst = max_burst
        self._history: Dict[int, deque] = defaultdict(deque)

    def is_allowed(self, user_id: int, current_time: Optional[float] = None) -> Tuple[bool, float]:
        """
        بررسی مجاز بودن درخواست کاربر.
        :param user_id: شناسه عددی کاربر تلگرام
        :param current_time: زمان جاری (جهت تسهیل آزمون‌های خودکار)
        :return: یک تاپل شامل (مجاز بودن: bool, زمان انتظار باقیمانده به ثانیه: float)
        """
        now = current_time if current_time is not None else time.time()
        user_history = self._history[user_id]

        # پاکسازی رویدادهای خارج از پنجره زمانی
        window_start = now - (self.rate_limit_seconds * self.max_burst)
        while user_history and user_history[0] < window_start:
            user_history.popleft()

        # بررسی فاصله با آخرین پیام
        if user_history:
            last_request_time = user_history[-1]
            elapsed = now - last_request_time
            if elapsed < self.rate_limit_seconds:
                wait_time = self.rate_limit_seconds - elapsed
                return False, round(wait_time, 2)

        # بررسی سقف پیام‌های همزمان در پنجره جاری
        if len(user_history) >= self.max_burst:
            oldest_in_window = user_history[0]
            wait_time = (oldest_in_window + (self.rate_limit_seconds * self.max_burst)) - now
            return False, round(max(wait_time, 0.1), 2)

        # ثبت زمان درخواست جدید
        user_history.append(now)
        return True, 0.0

    def reset(self, user_id: Optional[int] = None) -> None:
        """ریست کردن سوابق یک کاربر یا کل کاربران (مناسب برای محیط‌های آزمایشی)."""
        if user_id is not None:
            self._history.pop(user_id, None)
        else:
            self._history.clear()
