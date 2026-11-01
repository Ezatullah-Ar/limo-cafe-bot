"""
سرویس آگاه‌سازی مشتریان (services/notifications.py) در سامانه «کافی نت لیمو».
مسئول تولید پیام‌های خودکار، ساختاریافته و اطلاع‌رسانی بلادرنگ به متقاضیان در هنگام تغییر وضعیت پرونده‌ها.
"""

from typing import Optional
from core.models import Order
from core.calendar import utc_to_jalali_datetime, format_jalali_date
from services.tracking import format_order_status_persian
from bot.models import OutgoingResponse, KeyboardButton


STATUS_ACTION_TIPS = {
    "APPROVED": (
        "💡 <b>اقدام بعدی:</b> پرونده شما توسط اپراتور تایید گردید و مراحل رسمی آن در سامانه مرجع در حال پیگیری است."
    ),
    "NEED_INFO": (
        "⚠️ <b>اقدام فوری:</b> متقاضی گرامی، پرونده شما دارای نقص مدرک یا اطلاعات است. "
        "لطفاً توضیحات بالا را مطالعه نموده و از طریق ارتباط با اپراتور مدرک اصلاح‌شده را ارسال فرمایید."
    ),
    "COMPLETED": (
        "🎉 <b>تبریک:</b> خدمت درخواستی شما با موفقیت در سامانه مرجع ثبت و نهایی گردید. "
        "جهت دریافت کد صحت یا فایل نهایی، از طریق بخش پیگیری سفارش اقدام فرمایید."
    ),
    "CANCELLED": (
        "ℹ️ <b>توضیح:</b> این پرونده به دلیل قیدشده در یادداشت اپراتور لغو گردیده است. "
        "در صورت نیاز به ثبت مجدد یا رفع ابهام، می‌توانید با اپراتور در ارتباط باشید."
    )
}


class NotificationService:
    """سرویس مدیریت تولید اعلان‌های وضعیت برای متقاضیان همراه با مکانیزم جلوگیری از پیام تکراری (Idempotency)."""

    _sent_alerts = set()

    @classmethod
    def is_alert_duplicate(cls, order_id: int, status: str) -> bool:
        """بررسی اینکه آیا برای این سفارش در همین وضعیت قبلاً اعلان ارسال شده است یا خیر."""
        return (order_id, status.upper()) in cls._sent_alerts

    @classmethod
    def record_alert_sent(cls, order_id: int, status: str) -> None:
        """ثبت ارسال موفق اعلان جهت ممانعت از ارسال‌های مکرر و رگباری."""
        cls._sent_alerts.add((order_id, status.upper()))
        if len(cls._sent_alerts) > 1000:
            cls._sent_alerts.pop()

    @classmethod
    def clear_cache(cls) -> None:
        """پاکسازی حافظه اعلان‌ها (مخصوص آزمون‌های خودکار)."""
        cls._sent_alerts.clear()

    @staticmethod
    def create_customer_status_alert(
        order: Order,
        new_status: str,
        note: Optional[str] = None
    ) -> OutgoingResponse:
        """
        تولید پیام آگاه‌سازی مشتری با رعایت تقویم شمسی، زمان رسمی کشور و نکات مرتبط با وضعیت جدید.
        """
        status_meta = format_order_status_persian(new_status)
        tip_text = STATUS_ACTION_TIPS.get(new_status, "وضعیت پرونده شما به‌روزرسانی شد.")

        # تاریخ و ساعت به‌روزرسانی به وقت تهران
        now_dt = order.updated_at or order.created_at
        time_str = ""
        if now_dt:
            jy, jm, jd, hour, minute = utc_to_jalali_datetime(now_dt)
            date_str = format_jalali_date(jy, jm, jd)
            time_str = f"📅 <b>زمان ثبت رویداد:</b> {date_str} ساعت {hour:02d}:{minute:02d}\n"

        text_lines = [
            "🔔 <b>اطلاعیه تغییر وضعیت پرونده در کافی نت لیمو:</b>\n",
            f"🔖 <b>کد رهگیری:</b> <code>{order.tracking_code}</code>",
            f"📋 <b>خدمت درخواستی:</b> {order.service.title}",
            f"📌 <b>وضعیت جدید:</b> {status_meta['icon']} {status_meta['title']}\n"
        ]

        if note:
            text_lines.append(f"💬 <b>پیام اپراتور:</b>\n<i>{note}</i>\n")

        if time_str:
            text_lines.append(time_str)

        text_lines.append(tip_text)

        keyboard = [
            [KeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
        ]

        return OutgoingResponse(
            chat_id=order.user.telegram_id,
            text="\n".join(text_lines),
            reply_markup=keyboard
        )
