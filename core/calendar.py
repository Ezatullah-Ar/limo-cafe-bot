"""
ماژول اختصاصی تقویم هجری شمسی (جلالی) و منطقه زمانی تهران (Asia/Tehran).
پیاده‌سازی‌شده بر اساس الگوریتم دقیق محاسباتی بدون نیاز به کتابخانه‌های خارجی شخص ثالث.
"""

from datetime import datetime, date, timezone, timedelta
import re
from typing import Tuple, Optional


TEHRAN_TIMEZONE = timezone(timedelta(hours=3, minutes=30))

JALALI_MONTH_NAMES = (
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
)

# تناظر روزهای هفته پایتون (دوشنبه=0) با نام‌های فارسی
WEEKDAY_NAMES = {
    0: "دوشنبه",
    1: "سه‌شنبه",
    2: "چهارشنبه",
    3: "پنج‌شنبه",
    4: "جمعه",
    5: "شنبه",
    6: "یکشنبه"
}

PERSIAN_TO_ENGLISH_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def normalize_digits(text: str) -> str:
    """تبدیل کلیه ارقام فارسی و عربی به ارقام انگلیسی."""
    if not text:
        return ""
    return str(text).translate(PERSIAN_TO_ENGLISH_DIGITS)


def is_jalali_leap(jy: int) -> bool:
    """بررسی سال کبیسه هجری شمسی در دوره ۳۳ ساله حسابی."""
    return (jy % 33) in (1, 5, 9, 13, 17, 22, 26, 30)


def jalali_month_days(jy: int, jm: int) -> int:
    """محاسبه تعداد روزهای ماه هجری شمسی."""
    if jm < 1 or jm > 12:
        raise ValueError(f"شماره ماه شمسی باید بین ۱ تا ۱۲ باشد. مقدار ورودی: {jm}")
    if jm <= 6:
        return 31
    if jm <= 11:
        return 30
    return 30 if is_jalali_leap(jy) else 29


def gregorian_to_jalali(gy: int, gm: int, gd: int) -> Tuple[int, int, int]:
    """تبدیل تاریخ میلادی به تاریخ هجری شمسی با الگوریتم استاندارد نجومی."""
    g_d_m = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if (gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0):
        g_d_m[2] = 29

    gy2 = gy - 1600
    gm2 = gm - 1
    gd2 = gd - 1

    g_day_no = 365 * gy2 + (gy2 + 3) // 4 - (gy2 + 99) // 100 + (gy2 + 399) // 400
    for i in range(gm2):
        g_day_no += g_d_m[i + 1]
    g_day_no += gd2

    j_day_no = g_day_no - 79
    j_np = j_day_no // 12053
    j_day_no %= 12053

    jy = 979 + 33 * j_np + 4 * (j_day_no // 1461)
    j_day_no %= 1461

    if j_day_no >= 366:
        jy += (j_day_no - 1) // 365
        j_day_no = (j_day_no - 1) % 365

    for i in range(6):
        if j_day_no < 31:
            return (jy, i + 1, j_day_no + 1)
        j_day_no -= 31

    for i in range(6, 11):
        if j_day_no < 30:
            return (jy, i + 1, j_day_no + 1)
        j_day_no -= 30

    return (jy, 12, j_day_no + 1)


def jalali_to_gregorian(jy: int, jm: int, jd: int) -> Tuple[int, int, int]:
    """تبدیل تاریخ هجری شمسی به تاریخ میلادی."""
    jy2 = jy - 979
    jm2 = jm - 1
    jd2 = jd - 1

    j_day_no = 365 * jy2 + (jy2 // 33) * 8 + ((jy2 % 33) + 3) // 4
    for i in range(jm2):
        if i < 6:
            j_day_no += 31
        else:
            j_day_no += 30
    j_day_no += jd2

    g_day_no = j_day_no + 79
    gy = 1600 + 400 * (g_day_no // 146097)
    g_day_no = g_day_no % 146097

    leap = True
    if g_day_no >= 36525:
        g_day_no -= 1
        gy += 100 * (g_day_no // 36524)
        g_day_no = g_day_no % 36524
        if g_day_no >= 365:
            g_day_no += 1
        else:
            leap = False

    gy += 4 * (g_day_no // 1461)
    g_day_no %= 1461

    if g_day_no >= 366:
        leap = False
        g_day_no -= 1
        gy += g_day_no // 365
        g_day_no = g_day_no % 365

    g_d_m = [0, 31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    gm = 0
    while gm < 12 and g_day_no >= g_d_m[gm + 1]:
        g_day_no -= g_d_m[gm + 1]
        gm += 1

    return (gy, gm + 1, g_day_no + 1)


def parse_jalali_date(date_str: str) -> Tuple[int, int, int]:
    """
    تجزیه و اعتبارسنجی رشته تاریخ شمسی در قالب‌های YYYY/MM/DD یا YYYY-MM-DD.
    همچنین پشتیبانی از ارقام فارسی و ماه‌های تک‌رقمی.
    """
    clean_str = normalize_digits(date_str).strip()
    match = re.match(r"^(\d{4})[/-](\d{1,2})[/-](\d{1,2})$", clean_str)
    if not match:
        raise ValueError("قالب تاریخ نامعتبر است. لطفاً تاریخ را به صورت سال/ماه/روز وارد فرمایید (مثال: 1405/08/15).")

    jy, jm, jd = int(match.group(1)), int(match.group(2)), int(match.group(3))

    if jy < 1350 or jy > 1450:
        raise ValueError(f"سال شمسی {jy} خارج از بازه مجاز (1350 تا 1450) است.")

    if jm < 1 or jm > 12:
        raise ValueError(f"شماره ماه باید بین ۱ تا ۱۲ باشد. مقدار واردشده: {jm}")

    max_days = jalali_month_days(jy, jm)
    if jd < 1 or jd > max_days:
        month_name = JALALI_MONTH_NAMES[jm - 1]
        raise ValueError(f"ماه {month_name} در سال {jy} حداکثر {max_days} روز دارد. روز واردشده: {jd}")

    return (jy, jm, jd)


def format_jalali_date(jy: int, jm: int, jd: int, with_day_name: bool = True) -> str:
    """قالب‌بندی زیبای تاریخ شمسی به همراه نام روز و نام ماه فارسی."""
    gy, gm, gd = jalali_to_gregorian(jy, jm, jd)
    dt = date(gy, gm, gd)
    weekday_str = WEEKDAY_NAMES[dt.weekday()]
    month_name = JALALI_MONTH_NAMES[jm - 1]

    if with_day_name:
        return f"{weekday_str} {jd} {month_name} {jy} ({jy}/{jm:02d}/{jd:02d})"
    return f"{jd} {month_name} {jy}"


def jalali_to_utc_datetime(
    jy: int,
    jm: int,
    jd: int,
    hour: int = 9,
    minute: int = 0
) -> datetime:
    """
    تبدیل تاریخ و ساعت اعلامی بر اساس منطقه زمانی تهران (Asia/Tehran) به آبجکت datetime آگاه از UTC.
    ساعت پیش‌فرض: ۹ صبح به وقت تهران.
    """
    gy, gm, gd = jalali_to_gregorian(jy, jm, jd)
    tehran_dt = datetime(gy, gm, gd, hour, minute, tzinfo=TEHRAN_TIMEZONE)
    return tehran_dt.astimezone(timezone.utc)


def utc_to_jalali_datetime(dt: datetime) -> Tuple[int, int, int, int, int]:
    """تبدیل زمان UTC به سال، ماه، روز، ساعت و دقیقه در منطقه زمانی تهران."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    tehran_dt = dt.astimezone(TEHRAN_TIMEZONE)
    jy, jm, jd = gregorian_to_jalali(tehran_dt.year, tehran_dt.month, tehran_dt.day)
    return (jy, jm, jd, tehran_dt.hour, tehran_dt.minute)


def get_current_jalali(now_utc: Optional[datetime] = None) -> Tuple[int, int, int]:
    """دریافت تاریخ امروز شمسی در منطقه زمانی تهران."""
    if now_utc is None:
        now_utc = datetime.now(timezone.utc)
    jy, jm, jd, _, _ = utc_to_jalali_datetime(now_utc)
    return (jy, jm, jd)
