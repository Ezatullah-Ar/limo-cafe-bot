"""
ماژول اعتبارسنجی ورودی‌های سامانه «کافی نت لیمو».
این ماژول بررسی صحت کدهای ملی، شماره‌های تماس و فرمت‌های اطلاعاتی را به صورت بومی انجام می‌دهد.
"""

import re
from typing import Tuple


def validate_national_id(national_id: str) -> Tuple[bool, str]:
    """
    اعتبارسنجی الگوریتمی کد ملی ۱۰ رقمی جمهوری اسلامی ایران.
    بررسی طول، ارقام یکنواخت و رقم کنترل (Check Digit).
    :return: (آیا معتبر است: bool, پیام خطا: str)
    """
    if not national_id or not isinstance(national_id, str):
        return False, "کد ملی نمی‌تواند خالی باشد."

    nid = national_id.strip()

    # بررسی عددی بودن و ۱۰ رقم بودن
    if not re.match(r"^\d{10}$", nid):
        return False, "کد ملی باید دقیقاً ۱۰ رقم عددی باشد."

    # کدهای با ارقام کاملاً یکسان نامعتبر هستند (مانند 0000000000 یا 1111111111)
    if len(set(nid)) == 1:
        return False, "کد ملی وارد شده نامعتبر است (ارقام یکسان)."

    # محاسبه رقم کنترلی
    check_digit = int(nid[9])
    total_sum = sum(int(nid[i]) * (10 - i) for i in range(9))
    remainder = total_sum % 11

    if remainder < 2:
        is_valid = check_digit == remainder
    else:
        is_valid = check_digit == (11 - remainder)

    if not is_valid:
        return False, "کد ملی وارد شده با الگوریتم استاندارد کشوری مطابقت ندارد."

    return True, ""


def validate_iranian_phone(phone: str) -> Tuple[bool, str]:
    """
    اعتبارسنجی شماره تلفن همراه ایران (مانند 09123456789 یا +989123456789).
    """
    if not phone or not isinstance(phone, str):
        return False, "شماره تلفن همراه نمی‌تواند خالی باشد."

    p = phone.strip()
    pattern = r"^(09|\+989|00989)\d{9}$"
    if not re.match(pattern, p):
        return False, "فرمت شماره تلفن همراه نامعتبر است (مثال معتبر: 09123456789)."

    return True, ""


def validate_card_number(card: str) -> Tuple[bool, str]:
    """اعتبارسنجی شماره کارت بانکی ۱۶ رقمی شتاب."""
    if not card or not isinstance(card, str):
        return False, "شماره کارت بانکی نمی‌تواند خالی باشد."

    clean = re.sub(r"[\s\-]", "", card.strip())
    if not re.match(r"^\d{16}$", clean):
        return False, "شماره کارت بانکی باید دقیقاً ۱۶ رقم عددی باشد."

    return True, ""


def mask_sensitive_data(val: str, field_type: str = "general") -> str:
    """
    ماسک‌گذاری داده‌های هویتی و مالی حساس جهت محافظت در گزارش‌ها و لاگ‌ها.
    """
    if not val or not isinstance(val, str):
        return ""

    s = val.strip()
    # شماره کارت ۱۶ رقمی
    if field_type == "card" or (len(s) == 16 and s.isdigit()):
        return f"{s[:4]}-****-****-{s[-4:]}"

    # کد ملی ۱۰ رقمی
    if field_type == "national_id" or (len(s) == 10 and s.isdigit()):
        return f"{s[:3]}****{s[-3:]}"

    # شماره تلفن همراه ۱۱ رقمی
    if field_type == "phone" or (len(s) == 11 and s.startswith("09")):
        return f"{s[:4]}***{s[-4:]}"

    if len(s) > 6:
        return f"{s[:2]}***{s[-2:]}"

    return "***"

