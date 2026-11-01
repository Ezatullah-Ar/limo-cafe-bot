"""
سرویس مدیریت یادآورهای هوشمند مهلت‌ها (services/reminders.py) سامانه «کافی نت لیمو».
مسئول ایجاد، اعتبارسنجی تقویمی، استعلام، حذف و پردازش سررسید یادآورها بر مبنای تقویم شمسی.
"""

from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from core.models import Reminder, User
from core.calendar import (
    parse_jalali_date,
    jalali_to_utc_datetime,
    format_jalali_date,
    utc_to_jalali_datetime
)


class ReminderService:
    """سرویس مدیریت چرخه حیات یادآورهای تقویمی متقاضیان."""

    @staticmethod
    def create_reminder(
        session: Session,
        user_id: int,
        title: str,
        shamsi_date: str,
        target_hour: int = 9,
        target_minute: int = 0,
        description: Optional[str] = None,
        now_utc: Optional[datetime] = None
    ) -> Reminder:
        """
        ایجاد و اعتبارسنجی یک یادآور جدید بر مبنای تاریخ شمسی و ساعت تهران.
        جلوگیری سخت‌گیرانه از ثبت تاریخ‌های گذشته.
        """
        if not title or not title.strip():
            raise ValueError("عنوان یادآور نمی‌تواند خالی باشد.")

        clean_title = title.strip()
        jy, jm, jd = parse_jalali_date(shamsi_date)
        target_utc = jalali_to_utc_datetime(jy, jm, jd, hour=target_hour, minute=target_minute)

        current_time = now_utc if now_utc is not None else datetime.now(timezone.utc)
        if target_utc <= current_time:
            formatted_date = format_jalali_date(jy, jm, jd)
            raise ValueError(f"تاریخ سررسید ({formatted_date}) در گذشته قرار دارد. لطفاً تاریخی در آینده انتخاب فرمایید.")

        formatted_shamsi = f"{jy}/{jm:02d}/{jd:02d}"

        reminder = Reminder(
            user_id=user_id,
            title=clean_title,
            description=description.strip() if description else None,
            shamsi_date=formatted_shamsi,
            target_date=target_utc,
            is_sent=False
        )
        session.add(reminder)
        session.flush()
        return reminder

    @staticmethod
    def get_user_reminders(
        session: Session,
        user_id: int,
        active_only: bool = True
    ) -> List[Reminder]:
        """استخراج لیست یادآورهای کاربر مرتب‌شده بر اساس تاریخ سررسید."""
        query = session.query(Reminder).filter(Reminder.user_id == user_id)
        if active_only:
            query = query.filter(Reminder.is_sent == False)
        return query.order_by(Reminder.target_date.asc()).all()

    @staticmethod
    def get_reminder_by_id(
        session: Session,
        reminder_id: int,
        user_id: Optional[int] = None
    ) -> Optional[Reminder]:
        """یافتن یک یادآور مشخص با امکان بررسی مالکیت کاربر."""
        query = session.query(Reminder).filter(Reminder.id == reminder_id)
        if user_id is not None:
            query = query.filter(Reminder.user_id == user_id)
        return query.first()

    @staticmethod
    def delete_reminder(
        session: Session,
        reminder_id: int,
        user_id: int
    ) -> bool:
        """حذف یک یادآور توسط مالک آن."""
        reminder = ReminderService.get_reminder_by_id(session, reminder_id=reminder_id, user_id=user_id)
        if not reminder:
            return False
        session.delete(reminder)
        session.flush()
        return True

    @staticmethod
    def get_due_reminders(
        session: Session,
        current_utc_time: datetime
    ) -> List[Reminder]:
        """استخراج کلیه یادآورهای موعد سررسیدشده که هنوز ارسال نشده‌اند."""
        if current_utc_time.tzinfo is None:
            current_utc_time = current_utc_time.replace(tzinfo=timezone.utc)

        return (
            session.query(Reminder)
            .filter(
                Reminder.is_sent == False,
                Reminder.target_date <= current_utc_time
            )
            .order_by(Reminder.target_date.asc())
            .all()
        )

    @staticmethod
    def mark_as_sent(
        session: Session,
        reminder_id: int,
        sent_at: Optional[datetime] = None
    ) -> Optional[Reminder]:
        """علامت‌گذاری یادآور به عنوان ارسال‌شده برای جلوگیری از ارسال تکراری."""
        reminder = session.query(Reminder).filter(Reminder.id == reminder_id).first()
        if reminder:
            reminder.is_sent = True
            reminder.sent_at = sent_at if sent_at else datetime.now(timezone.utc)
            session.flush()
        return reminder

    @staticmethod
    def format_reminder_notification(reminder: Reminder) -> str:
        """قالب‌بندی پیام آگاه‌سازی سررسید یادآور برای ارسال به تلگرام کاربر."""
        jy, jm, jd, hour, minute = utc_to_jalali_datetime(reminder.target_date)
        persian_date_str = format_jalali_date(jy, jm, jd)

        text = (
            "⏰ <b>سررسید یادآور کافی نت لیمو</b>\n\n"
            f"📌 <b>موضوع:</b> {reminder.title}\n"
            f"📅 <b>موعد:</b> {persian_date_str}\n"
        )
        if reminder.description:
            text += f"📝 <b>توضیحات:</b> {reminder.description}\n"

        text += (
            "\n💡 متقاضی گرامی، مهلت یا زمان ثبت‌نام مربوط به این پرونده فرارسیده است. "
            "جهت اقدام و پیگیری، می‌توانید از طریق منوی خدمات اقدام فرمایید."
        )
        return text

    @staticmethod
    def process_due_reminders(
        session: Session,
        current_utc_time: datetime
    ) -> List[Tuple[int, str]]:
        """
        پردازش دوره‌ای یادآورهای سررسیدشده: استخراج، تولید متن و علامت‌گذاری قطعی به عنوان ارسال‌شده.
        خروجی: لیستی از توپل‌های (telegram_id, message_text)
        """
        due_list = ReminderService.get_due_reminders(session, current_utc_time)
        dispatched: List[Tuple[int, str]] = []

        for rem in due_list:
            telegram_id = rem.user.telegram_id
            msg_text = ReminderService.format_reminder_notification(rem)
            rem.is_sent = True
            rem.sent_at = current_utc_time
            dispatched.append((telegram_id, msg_text))

        if due_list:
            session.flush()

        return dispatched
