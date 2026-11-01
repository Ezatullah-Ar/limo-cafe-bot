"""
سرویس مدیریت تیکت‌ها و گفتگوی زنده پشتیبانی (services/support.py)
سامانه «کافی نت لیمو».
شامل مدیریت چرخه‌حیات رشته گفتگوها، ارسال و دریافت پیام، انتساب اپراتور و تغییر وضعیت تیکت.
"""

import logging
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from core.models import User, Order, SupportThread, SupportMessage

logger = logging.getLogger("support")


class SupportService:
    """سرویس عملیات پشتیبانی و تیکتینگ مشتری و اپراتور."""

    @staticmethod
    def get_or_create_active_thread(
        session: Session,
        user_id: int,
        related_order_id: Optional[int] = None
    ) -> SupportThread:
        """یافتن گفتگوی باز فعلی متقاضی یا ایجاد تیکت گفتگوی جدید."""
        thread = (
            session.query(SupportThread)
            .filter(
                SupportThread.user_id == user_id,
                SupportThread.status.in_(["NEW", "PENDING_SUPPORT", "PENDING_CUSTOMER"])
            )
            .order_by(SupportThread.created_at.desc())
            .first()
        )

        if not thread:
            thread = SupportThread(
                user_id=user_id,
                status="NEW",
                related_order_id=related_order_id
            )
            session.add(thread)
            session.commit()
            session.refresh(thread)
            logger.info("New support thread #%d created for user_id=%d", thread.id, user_id)
        elif related_order_id and not thread.related_order_id:
            thread.related_order_id = related_order_id
            session.commit()

        return thread

    @staticmethod
    def add_customer_message(
        session: Session,
        thread_id: int,
        sender_telegram_id: int,
        message_text: Optional[str] = None,
        file_id: Optional[str] = None,
        file_type: Optional[str] = None
    ) -> SupportMessage:
        """ثبت پیام جدید از سوی متقاضی و تغییر وضعیت تیکت به در انتظار پاسخ پشتیبانی."""
        thread = session.query(SupportThread).filter_by(id=thread_id).first()
        if not thread:
            raise ValueError(f"Support thread #{thread_id} not found.")

        # اگر تیکت بسته بود، مجدداً بازگشایی شود
        thread.status = "PENDING_SUPPORT"
        thread.updated_at = datetime.now(timezone.utc)

        msg = SupportMessage(
            thread_id=thread_id,
            sender_role="CUSTOMER",
            sender_id=sender_telegram_id,
            message_text=message_text,
            file_id=file_id,
            file_type=file_type,
            is_read=False
        )
        session.add(msg)
        session.commit()
        session.refresh(msg)
        logger.info("Customer message added to thread #%d (msg_id=%d)", thread_id, msg.id)
        return msg

    @staticmethod
    def add_operator_message(
        session: Session,
        thread_id: int,
        operator_telegram_id: int,
        message_text: Optional[str] = None,
        file_id: Optional[str] = None,
        file_type: Optional[str] = None
    ) -> SupportMessage:
        """ثبت پاسخ اپراتور و تغییر وضعیت تیکت به در انتظار پاسخ مشتری."""
        thread = session.query(SupportThread).filter_by(id=thread_id).first()
        if not thread:
            raise ValueError(f"Support thread #{thread_id} not found.")

        thread.status = "PENDING_CUSTOMER"
        thread.assigned_operator_id = operator_telegram_id
        thread.updated_at = datetime.now(timezone.utc)

        # علامت‌گذاری پیام‌های قبلی متقاضی به عنوان خوانده‌شده
        session.query(SupportMessage).filter(
            SupportMessage.thread_id == thread_id,
            SupportMessage.sender_role == "CUSTOMER",
            SupportMessage.is_read.is_(False)
        ).update({"is_read": True})

        msg = SupportMessage(
            thread_id=thread_id,
            sender_role="OPERATOR",
            sender_id=operator_telegram_id,
            message_text=message_text,
            file_id=file_id,
            file_type=file_type,
            is_read=True
        )
        session.add(msg)
        session.commit()
        session.refresh(msg)
        logger.info("Operator %d replied to thread #%d", operator_telegram_id, thread_id)
        return msg

    @staticmethod
    def close_thread(session: Session, thread_id: int, actor_id: Optional[int] = None) -> SupportThread:
        """بستن پرونده گفتگو."""
        thread = session.query(SupportThread).filter_by(id=thread_id).first()
        if not thread:
            raise ValueError(f"Support thread #{thread_id} not found.")

        thread.status = "CLOSED"
        thread.updated_at = datetime.now(timezone.utc)
        session.commit()
        session.refresh(thread)
        logger.info("Thread #%d closed by actor %s", thread_id, actor_id)
        return thread

    @staticmethod
    def reopen_thread(session: Session, thread_id: int) -> SupportThread:
        """بازگشایی مجدد گفتگوی بسته‌شده."""
        thread = session.query(SupportThread).filter_by(id=thread_id).first()
        if not thread:
            raise ValueError(f"Support thread #{thread_id} not found.")

        thread.status = "PENDING_SUPPORT"
        thread.updated_at = datetime.now(timezone.utc)
        session.commit()
        session.refresh(thread)
        logger.info("Thread #%d reopened", thread_id)
        return thread

    @staticmethod
    def assign_operator(session: Session, thread_id: int, operator_id: int) -> SupportThread:
        """تخصیص اپراتور مسئول به تیکت."""
        thread = session.query(SupportThread).filter_by(id=thread_id).first()
        if not thread:
            raise ValueError(f"Support thread #{thread_id} not found.")

        thread.assigned_operator_id = operator_id
        thread.updated_at = datetime.now(timezone.utc)
        session.commit()
        session.refresh(thread)
        return thread

    @staticmethod
    def get_thread_messages(session: Session, thread_id: int) -> List[SupportMessage]:
        """دریافت پیام‌های یک تیکت بر اساس ترتیب زمانی."""
        return (
            session.query(SupportMessage)
            .filter_by(thread_id=thread_id)
            .order_by(SupportMessage.created_at.asc())
            .all()
        )

    @staticmethod
    def get_user_threads(session: Session, user_id: int) -> List[SupportThread]:
        """دریافت تمام تیکت‌های یک متقاضی مشخص (جهت حفظ ایزولاسیون و عدم مشاهده پرونده دیگران)."""
        return (
            session.query(SupportThread)
            .filter_by(user_id=user_id)
            .order_by(SupportThread.created_at.desc())
            .all()
        )

    @staticmethod
    def get_all_threads(session: Session, status: Optional[str] = None) -> List[SupportThread]:
        """دریافت کلیه تیکت‌ها جهت نمایش در پنل مدیریت."""
        q = session.query(SupportThread)
        if status and status != "ALL":
            q = q.filter(SupportThread.status == status)
        return q.order_by(SupportThread.updated_at.desc()).all()
