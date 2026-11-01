"""
آزمون‌های خودکار ماژول اعتبارسنجی ورودی‌ها (core/validators.py)
"""

import unittest
from core.validators import validate_national_id, validate_iranian_phone


class TestValidators(unittest.TestCase):
    """مجموعه آزمون‌های الگوریتم کد ملی و اعتبارسنجی شماره تلفن همراه."""

    def test_valid_national_ids(self):
        """آزمون کدهای ملی معتبر بر اساس الگوریتم کنترل کشوری."""
        valid_ids = [
            "0010350829",
            "0499370899",
            "0012345679",
            "1234567891"
        ]
        for nid in valid_ids:
            is_valid, msg = validate_national_id(nid)
            self.assertTrue(is_valid, f"کد ملی {nid} باید معتبر باشد اما خطا داد: {msg}")
            self.assertEqual(msg, "")

    def test_invalid_national_ids(self):
        """آزمون کدهای ملی نامعتبر (طول اشتباه، ارقام یکنواخت، رقم کنترل ناصحیح)."""
        invalid_ids = [
            "",             # خالی
            "12345",        # کوتاه
            "12345678901",  # بلند
            "abcdefghij",   # حروف
            "0000000000",   # ارقام یکسان
            "1111111111",   # ارقام یکسان
            "0010350828"    # رقم کنترل اشتباه
        ]
        for nid in invalid_ids:
            is_valid, msg = validate_national_id(nid)
            self.assertFalse(is_valid, f"کد ملی {nid} باید نامعتبر باشد!")
            self.assertGreater(len(msg), 0)

    def test_valid_iranian_phones(self):
        """آزمون شماره‌های همراه معتبر با پیش‌شماره‌های مجاز."""
        valid_phones = [
            "09123456789",
            "09351234567",
            "+989123456789",
            "00989123456789"
        ]
        for p in valid_phones:
            is_valid, msg = validate_iranian_phone(p)
            self.assertTrue(is_valid, f"شماره {p} باید معتبر باشد اما خطا داد: {msg}")

    def test_invalid_iranian_phones(self):
        """آزمون شماره‌های همراه نامعتبر."""
        invalid_phones = [
            "",
            "08123456789",  # پیش‌شماره نامعتبر
            "0912345",      # کوتاه
            "091234567890", # بلند
            "0912abcd789"   # شامل حروف
        ]
        for p in invalid_phones:
            is_valid, msg = validate_iranian_phone(p)
            self.assertFalse(is_valid, f"شماره {p} باید نامعتبر باشد!")


if __name__ == "__main__":
    unittest.main()
