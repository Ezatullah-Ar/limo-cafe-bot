"""
ماژول جامع پیگیری، تولید کد رهگیری، استپر ۴ مرحله‌ای و حریم خصوصی پرونده‌ها (services/tracking.py)
سامانه «کافی نت لیمو» - فاز ۵.
شامل استپر گرافیکی، عایق‌بندی اطلاعات مشتریان (Tenant Isolation)، تبدیل تاریخ‌های شمسی و پرتال درخواست‌های من.
"""

import secrets
import string
from typing import Dict, List, Tuple, Any, Optional
from core.calendar import utc_to_jalali_datetime, format_jalali_date

STATUS_PERSISTENT_MAP: Dict[str, Dict[str, str]] = {
    "PENDING": {
        "title": "در انتظار بررسی اپراتور",
        "icon": "⏳",
        "description": "درخواست شما ثبت شده و در نوبت بررسی اولیه توسط اپراتور کافی نت لیمو قرار دارد."
    },
    "IN_REVIEW": {
        "title": "در حال بررسی مدارک",
        "icon": "🔎",
        "description": "اپراتور در حال بررسی مدارک و تطبیق اطلاعات با سامانه‌های رسمی است."
    },
    "NEED_INFO": {
        "title": "نقص مدارک / نیازمند اطلاعات تکمیلی",
        "icon": "⚠️",
        "description": "پرونده شما دارای نقص است. لطفاً توضیحات اپراتور را مطالعه و مدارک اصلاحی را ارسال فرمایید."
    },
    "APPROVED": {
        "title": "تاییدشده و در حال انجام",
        "icon": "🟢",
        "description": "اطلاعات پرونده تایید شد و فرآیند ثبت رسمی در سامانه هدف آغاز گردیده است."
    },
    "IN_PROGRESS": {
        "title": "در حال اقدام در سامانه",
        "icon": "🔵",
        "description": "اپراتور هم‌اکنون در حال پیگیری و ثبت درخواست شما در سامانه ذی‌صلاح است."
    },
    "COMPLETED": {
        "title": "تکمیل‌شده و پایان یافته",
        "icon": "✅",
        "description": "خدمت مورد نظر با موفقیت در سامانه مرجع انجام شد و پرونده مختومه گردید."
    },
    "CANCELLED": {
        "title": "لغو شده",
        "icon": "❌",
        "description": "این درخواست به درخواست متقاضی یا به دلیل عدم احراز شرایط توسط اپراتور لغو شد."
    },
    "REJECTED": {
        "title": "رد شده",
        "icon": "🔴",
        "description": "متأسفانه امکان انجام این درخواست فراهم نگردید. علت در توضیحات اپراتور قید شده است."
    }
}


def generate_tracking_code(prefix: str = "LIMO", year: int = 1405) -> str:
    """
    تولید کد رهگیری یکتای ۵ رقمی ایمن و غیرقابل حدس با استفاده از ماژول secrets پایتون.
    نمونه خروجی: LIMO-1405-84921
    """
    random_part = "".join(secrets.choice(string.digits) for _ in range(5))
    return f"{prefix}-{year}-{random_part}"


def format_order_status_persian(status: str) -> Dict[str, str]:
    """دریافت نام و آیکون وضعیت به زبان فارسی."""
    return STATUS_PERSISTENT_MAP.get(
        (status or "").upper(),
        {
            "title": status or "نامشخص",
            "icon": "🔄",
            "description": "وضعیت پرونده در حال به‌روزرسانی است."
        }
    )


def generate_order_stepper(status: str) -> Dict[str, Any]:
    """
    تولید استپر بصری ۴ مرحله‌ای واقعی بر مبنای آخرین وضعیت پرونده:
      ۱. ثبت درخواست
      ۲. بررسی مدارک
      ۳. پردازش در سامانه
      ۴. صدور رسید و تحویل
    """
    st = (status or "PENDING").upper()

    if st == "PENDING":
        steps = [
            ("1️⃣ ثبت درخواست", "🔵 تکمیل و ثبت شد"),
            ("2️⃣ بررسی مدارک", "⏳ در نوبت بررسی"),
            ("3️⃣ پردازش سامانه", "⚪ در انتظار"),
            ("4️⃣ صدور و تحویل", "⚪ در انتظار"),
        ]
        action = "پرونده شما در صف بررسی اولیه توسط اپراتور قرار دارد. نیازی به اقدام خاصی از سوی شما نیست."
        current_step = 1

    elif st == "NEED_INFO":
        steps = [
            ("1️⃣ ثبت درخواست", "🟢 انجام شد"),
            ("2️⃣ بررسی مدارک", "⚠️ نقص مدرک / نیازمند اصلاح"),
            ("3️⃣ پردازش سامانه", "⚪ متوقف"),
            ("4️⃣ صدور و تحویل", "⚪ متوقف"),
        ]
        action = "متقاضی گرامی، پرونده شما دارای نقص مدرک است. لطفاً توضیحات اپراتور را مطالعه کرده و مدارک لازم را از طریق ارتباط با اپراتور ارسال فرمایید."
        current_step = 2

    elif st in ("IN_REVIEW", "APPROVED"):
        steps = [
            ("1️⃣ ثبت درخواست", "🟢 انجام شد"),
            ("2️⃣ بررسی مدارک", "🟢 تایید مدارک"),
            ("3️⃣ پردازش سامانه", "⏳ در نوبت ثبت رسمی"),
            ("4️⃣ صدور و تحویل", "⚪ در انتظار"),
        ]
        action = "مدارک و اطلاعات هویتی شما تایید شده و پرونده جهت ثبت نهایی در سامانه هدف آماده‌سازی گردیده است."
        current_step = 2

    elif st in ("IN_PROGRESS", "PROCESSING"):
        steps = [
            ("1️⃣ ثبت درخواست", "🟢 انجام شد"),
            ("2️⃣ بررسی مدارک", "🟢 تایید مدارک"),
            ("3️⃣ پردازش سامانه", "🔵 در حال اقدام و پیگیری"),
            ("4️⃣ صدور و تحویل", "⚪ در انتظار"),
        ]
        action = "اپراتور هم‌اکنون در سامانه مرجع در حال ثبت و پیگیری درخواست شما می‌باشد."
        current_step = 3

    elif st == "COMPLETED":
        steps = [
            ("1️⃣ ثبت درخواست", "🟢 انجام شد"),
            ("2️⃣ بررسی مدارک", "🟢 تایید مدارک"),
            ("3️⃣ پردازش سامانه", "🟢 انجام موفق در سامانه"),
            ("4️⃣ صدور و تحویل", "✅ تکمیل نهایی و مختومه"),
        ]
        action = "خدمت درخواستی شما با موفقیت به پایان رسید و پرونده مختومه شد."
        current_step = 4

    elif st in ("CANCELLED", "REJECTED"):
        steps = [
            ("1️⃣ ثبت درخواست", "🟢 انجام شد"),
            ("2️⃣ بررسی مدارک", "❌ رد شده / لغو"),
            ("3️⃣ پردازش سامانه", "⛔ متوقف"),
            ("4️⃣ صدور و تحویل", "⛔ پرونده بسته شد"),
        ]
        action = "این درخواست لغو یا رد گردیده است. علت در پیام اپراتور قید شده است."
        current_step = 2

    else:
        steps = [
            ("1️⃣ ثبت درخواست", "🟢 انجام شد"),
            ("2️⃣ بررسی مدارک", "🔄 در حال بررسی"),
            ("3️⃣ پردازش سامانه", "⚪ در انتظار"),
            ("4️⃣ صدور و تحویل", "⚪ در انتظار"),
        ]
        action = "وضعیت پرونده در حال بررسی است."
        current_step = 2

    return {
        "current_step": current_step,
        "steps": steps,
        "action_required": action
    }


def render_order_card(order: Any, requester_telegram_id: int, is_admin_or_op: bool = False) -> Tuple[bool, str]:
    """
    تولید گزارش رسمی وضعیت پرونده به همراه استپر ۴ مرحله‌ای و بررسی ایزولاسیون کامل حریم خصوصی.
    در صورتی که متقاضی مجاز نباشد، خطای دسترسی بازگردانده شده و هیچ اطلاعاتی افشا نمی‌شود.
    """
    # بررسی عایق‌بندی اطلاعات مشتریان (Tenant Isolation)
    if order.user and order.user.telegram_id != requester_telegram_id and not is_admin_or_op:
        return False, (
            "🔒 <b>خطای دسترسی:</b>\n"
            "این پرونده به حساب کاربری دیگری تعلق دارد و اطلاعات آن محرمانه می‌باشد.\n"
            "شما صرفاً مجاز به پیگیری سفارشات ثبت‌شده توسط خود هستید."
        )

    stepper_info = generate_order_stepper(order.status)
    status_meta = format_order_status_persian(order.status)

    # تاریخ و ساعت شمسی
    time_str = "—"
    dt = getattr(order, "updated_at", None) or getattr(order, "created_at", None)
    if dt:
        jy, jm, jd, h, m = utc_to_jalali_datetime(dt)
        date_str = format_jalali_date(jy, jm, jd)
        time_str = f"{date_str} ساعت {h:02d}:{m:02d}"

    service_title = order.service.title if getattr(order, "service", None) else "سفارش کافی نت"

    lines = [
        f"🔖 <b>شناسنامه و وضعیت پرونده {order.tracking_code}</b>\n",
        f"📋 <b>خدمت درخواستی:</b> {service_title}",
        f"📌 <b>وضعیت کنونی:</b> {status_meta['icon']} {status_meta['title']}",
        f"🕒 <b>آخرین به‌روزرسانی:</b> <code>{time_str}</code>\n",
        "📊 <b>روند پیشرفت مراحل (استپر پرونده):</b>"
    ]

    for title, status_text in stepper_info["steps"]:
        lines.append(f"  ▪️ <b>{title}:</b> {status_text}")

    lines.append(f"\n💡 <b>اقدام مورد نیاز شما:</b>\n{stepper_info['action_required']}")

    docs = getattr(order, "documents", None)
    if docs:
        lines.append(f"\n📎 <b>مدارک ضمیمه پرونده:</b> {len(docs)} مدرک ثبت‌شده")

    notes = getattr(order, "operator_notes", None)
    if notes:
        lines.append(f"\n💬 <b>یادداشت اپراتور مسئول:</b>\n<i>{notes}</i>")

    return True, "\n".join(lines)


def render_user_orders_list(orders: List[Any]) -> str:
    """
    تولید لیست نمایشی «درخواست‌های من» با آیکون‌های وضعیت و کدهای رهگیری.
    """
    if not orders:
        return (
            "📂 <b>پرتال پرونده‌های من</b>\n\n"
            "شما در حال حاضر هیچ سفارش یا پرونده فعالی در سامانه ندارید.\n"
            "برای ثبت سفارش جدید، گزینه «📋 فهرست خدمات» را انتخاب فرمایید."
        )

    lines = [
        "📂 <b>پرتال پرونده‌های من در کافی‌نت لیمو</b>\n",
        "لیست کلیه پرونده‌ها و سوابق ثبت‌نام شما به شرح زیر است:\n"
    ]

    for idx, ord_item in enumerate(orders, 1):
        status_meta = format_order_status_persian(ord_item.status)
        dt = getattr(ord_item, "created_at", None)
        date_str = "—"
        if dt:
            jy, jm, jd, _, _ = utc_to_jalali_datetime(dt)
            date_str = f"{jy}/{jm:02d}/{jd:02d}"

        svc_title = ord_item.service.title if getattr(ord_item, "service", None) else "خدمت"
        lines.append(
            f"{idx}. {status_meta['icon']} <b>{svc_title}</b>\n"
            f"   ▫️ کد رهگیری: <code>{ord_item.tracking_code}</code>\n"
            f"   ▫️ وضعیت: {status_meta['title']}\n"
            f"   ▫️ تاریخ ثبت: {date_str}\n"
        )

    lines.append("<i>جهت مشاهده جزئیات و استپر هر پرونده، کد رهگیری آن را لمس یا ارسال نمایید.</i>")
    return "\n".join(lines)
