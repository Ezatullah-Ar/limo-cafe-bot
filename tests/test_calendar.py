"""
آزمون‌های خودکار ماژول محاسبات تقویم هجری شمسی و منطقه زمانی تهران (core/calendar.py)
"""

import unittest
from datetime import datetime, timezone, timedelta
from core.calendar import (
    gregorian_to_jalali,
    jalali_to_gregorian,
    is_jalali_leap,
    jalali_month_days,
    normalize_digits,
    parse_jalali_date,
    format_jalali_date,
    jalali_to_utc_datetime,
    utc_to_jalali_datetime,
    TEHRAN_TIMEZONE
)


class TestCalendar(unittest.TestCase):
    """مجموعه آزمون‌های محاسباتی تقویم شمسی جلالی، اعتبارسنجی و تبدیل مناطق زمانی."""

    def test_gregorian_jalali_conversion_known_dates(self):
        """آزمون تبدیل تاریخ‌های میلادی و شمسی شناخته‌شده و تطابق با تقویم رسمی."""
        test_cases = [
            # (gy, gm, gd, jy, jm, jd)
            (2024, 3, 20, 1403, 1, 1),    # آغاز سال ۱۴۰۳
            (2025, 3, 21, 1404, 1, 1),    # آغاز سال ۱۴۰۴
            (2026, 3, 21, 1405, 1, 1),    # آغاز سال ۱۴۰۵
            (2026, 10, 26, 1405, 8, 4),   # زمان جاری سیستم
        ]

        for gy, gm, gd, expected_jy, expected_jm, expected_jd in test_cases:
            res_j = gregorian_to_jalali(gy, gm, gd)
            self.assertEqual(res_j, (expected_jy, expected_jm, expected_jd))

            res_g = jalali_to_gregorian(expected_jy, expected_jm, expected_jd)
            self.assertEqual(res_g, (gy, gm, gd))

    def test_roundtrip_conversion_span(self):
        """آزمون دورگشت (Round-trip) ۵۰۰ روز متوالی بدون حتی یک روز انحراف."""
        start_date = datetime(2025, 1, 1)
        for offset in range(500):
            cur = start_date + timedelta(days=offset)
            jy, jm, jd = gregorian_to_jalali(cur.year, cur.month, cur.day)
            gy, gm, gd = jalali_to_gregorian(jy, jm, jd)
            self.assertEqual((cur.year, cur.month, cur.day), (gy, gm, gd))

    def test_jalali_leap_year_detection(self):
        """آزمون شناسایی صحیح سال‌های کبیسه هجری شمسی."""
        self.assertTrue(is_jalali_leap(1403))   # ۱۴۰۳ کبیسه است
        self.assertFalse(is_jalali_leap(1404))  # ۱۴۰۴ عادی است
        self.assertFalse(is_jalali_leap(1405))  # ۱۴۰۵ عادی است
        self.assertFalse(is_jalali_leap(1406))  # ۱۴۰۶ عادی است
        self.assertTrue(is_jalali_leap(1408))   # ۱۴۰۸ کبیسه است

    def test_jalali_month_days(self):
        """آزمون تعداد روزهای هر ماه شمسی (شش ماه اول ۳۱ روز، پنج ماه دوم ۳۰ روز، اسفند ۲۹ یا ۳۰ روز)."""
        # ماه‌های ۱ تا ۶
        for m in range(1, 7):
            self.assertEqual(jalali_month_days(1405, m), 31)

        # ماه‌های ۷ تا ۱۱
        for m in range(7, 12):
            self.assertEqual(jalali_month_days(1405, m), 30)

        # اسفند در سال عادی
        self.assertEqual(jalali_month_days(1405, 12), 29)
        # اسفند در سال کبیسه
        self.assertEqual(jalali_month_days(1403, 12), 30)

        # بررسی شماره ماه نامعتبر
        with self.assertRaises(ValueError):
            jalali_month_days(1405, 0)
        with self.assertRaises(ValueError):
            jalali_month_days(1405, 13)

    def test_normalize_digits(self):
        """آزمون تبدیل ارقام فارسی و عربی به ارقام انگلیسی."""
        persian_str = "۱۴۰۵/۰۸/۱۵"
        arabic_str = "١٤٠٥/٠٨/١٥"
        mixed_str = "کد ۱۲۳ و ٤٥٦"

        self.assertEqual(normalize_digits(persian_str), "1405/08/15")
        self.assertEqual(normalize_digits(arabic_str), "1405/08/15")
        self.assertEqual(normalize_digits(mixed_str), "کد 123 و 456")
        self.assertEqual(normalize_digits(""), "")

    def test_parse_jalali_date_valid(self):
        """آزمون تجزیه رشته تاریخ‌های شمسی معتبر با خط مورب یا خط فاصله."""
        self.assertEqual(parse_jalali_date("1405/08/15"), (1405, 8, 15))
        self.assertEqual(parse_jalali_date("1405-08-15"), (1405, 8, 15))
        self.assertEqual(parse_jalali_date("  ۱۴۰۵/۸/۵  "), (1405, 8, 5))

    def test_parse_jalali_date_invalid(self):
        """آزمون رد تاریخ‌های شمسی با قالب نامعتبر یا مقادیر خارج از محدوده."""
        invalid_inputs = [
            "invalid_date",
            "1405/13/01",     # ماه ۱۳ نامعتبر
            "1405/00/01",     # ماه ۰ نامعتبر
            "1405/07/31",     # مهرماه فقط ۳۰ روز دارد
            "1405/12/30",     # اسفند سال ۱۴۰۵ عادی است و ۳۰ روز ندارد
            "1200/01/01",     # سال خارج از محدوده
        ]
        for bad_date in invalid_inputs:
            with self.assertRaises(ValueError):
                parse_jalali_date(bad_date)

    def test_format_jalali_date(self):
        """آزمون قالب‌بندی فارسی تاریخ با نام روز هفته و نام ماه."""
        formatted = format_jalali_date(1405, 8, 4, with_day_name=True)
        self.assertIn("آبان", formatted)
        self.assertIn("1405", formatted)
        self.assertIn("دوشنبه", formatted)

    def test_tehran_timezone_utc_roundtrip(self):
        """آزمون تبدیل ساعت به وقت تهران (+03:30) به UTC و برعکس."""
        utc_dt = jalali_to_utc_datetime(1405, 8, 15, hour=9, minute=0)
        # ۹ صبح تهران باید معادل ۰۵:۳۰ صبح UTC باشد (اختلاف ۳ ساعت و نیم)
        self.assertEqual(utc_dt.hour, 5)
        self.assertEqual(utc_dt.minute, 30)
        self.assertEqual(utc_dt.tzinfo, timezone.utc)

        # بازگشت به زمان شمسی تهران
        jy, jm, jd, h, m = utc_to_jalali_datetime(utc_dt)
        self.assertEqual((jy, jm, jd), (1405, 8, 15))
        self.assertEqual((h, m), (9, 0))


if __name__ == "__main__":
    unittest.main()
