"""
سرویس مدیریت سفارشات و پرونده‌های متقاضیان در سامانه «کافی نت لیمو».
این ماژول ثبت سفارش، رهگیری، صدور کدهای یکتا و مدیریت سوابق بازرسی (Audit Log) را مدیریت می‌کند.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from core.models import Order, OrderDocument, OrderAuditLog, User, ServiceItem
from services.tracking import generate_tracking_code


class OrderService:
    """عملیات دیتابیسی و قوانین تجاری پیرامون سفارشات و پرونده‌ها."""

    @staticmethod
    def create_order(
        session: Session,
        user_id: int,
        service_id: int,
        form_data: Dict[str, Any],
        actor_telegram_id: int
    ) -> Order:
        """
        ایجاد سفارش جدید همراه با صدور کد رهگیری یکتا و ثبت در لاگ حسابرسی.
        """
        # اطمینان از یکتایی کد رهگیری با تلاش مجدد در صورت تصادم نادر
        max_attempts = 10
        tracking_code = ""
        for _ in range(max_attempts):
            candidate_code = generate_tracking_code()
            exists = session.query(Order).filter_by(tracking_code=candidate_code).first()
            if not exists:
                tracking_code = candidate_code
                break

        if not tracking_code:
            raise RuntimeError("خطا در تولید کد رهگیری یکتای سامانه.")

        order = Order(
            tracking_code=tracking_code,
            user_id=user_id,
            service_id=service_id,
            status="PENDING",
            form_data=form_data
        )
        session.add(order)
        session.flush()

        # ثبت سابقه اولیه در Audit Log
        audit_log = OrderAuditLog(
            order_id=order.id,
            actor_id=actor_telegram_id,
            from_status="NONE",
            to_status="PENDING",
            note="ثبت اولیه درخواست توسط مشتری در ربات"
        )
        session.add(audit_log)
        session.flush()

        return order

    @staticmethod
    def get_order_by_id(session: Session, order_id: int) -> Optional[Order]:
        """یافتن سفارش بر اساس شناسه عددی (ID)."""
        return session.query(Order).filter_by(id=order_id).first()

    @staticmethod
    def get_orders_for_operator(session: Session, status_filter: Optional[List[str]] = None) -> List[Order]:
        """دریافت لیست سفارشات برای کارتابل اپراتور، مرتب‌شده از جدیدترین."""
        query = session.query(Order)
        if status_filter:
            query = query.filter(Order.status.in_(status_filter))
        return query.order_by(Order.created_at.desc()).all()

    @staticmethod
    def get_order_by_tracking_code(session: Session, tracking_code: str) -> Optional[Order]:
        """یافتن سفارش بر اساس کد رهگیری (بدون حساسیت به فاصله یا حروف بزرگ/کوچک)."""
        clean_code = tracking_code.strip().upper()
        return session.query(Order).filter_by(tracking_code=clean_code).first()

    @staticmethod
    def get_user_orders(session: Session, user_id: int) -> List[Order]:
        """دریافت تمام پرونده‌های متعلق به یک کاربر به ترتیب از جدیدترین."""
        return session.query(Order).filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()

    @staticmethod
    def get_user_orders_by_telegram_id(session: Session, telegram_id: int) -> List[Order]:
        """دریافت تمام پرونده‌های کاربر بر مبنای شناسه عددی تلگرام با رعایت عایق‌بندی کامل."""
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            return []
        return session.query(Order).filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()

    @staticmethod
    def update_order_status(
        session: Session,
        order_id: int,
        new_status: str,
        actor_telegram_id: int,
        note: Optional[str] = None
    ) -> Order:
        """
        تغییر وضعیت پرونده توسط اپراتور یا مدیر به همراه ثبت لاگ تغییرات.
        """
        order = session.query(Order).filter_by(id=order_id).first()
        if not order:
            raise ValueError(f"سفارشی با شناسه {order_id} یافت نشد.")

        old_status = order.status
        order.status = new_status
        if note:
            order.operator_notes = note

        audit = OrderAuditLog(
            order_id=order.id,
            actor_id=actor_telegram_id,
            from_status=old_status,
            to_status=new_status,
            note=note
        )
        session.add(audit)
        session.flush()

        return order

    @staticmethod
    def attach_document(
        session: Session,
        order_id: int,
        file_id: str,
        file_name: Optional[str] = None,
        file_type: str = "DOCUMENT",
        file_size: Optional[int] = None
    ) -> OrderDocument:
        """پیوست کردن مدرک ارسالی متقاضی به پرونده سفارش."""
        doc = OrderDocument(
            order_id=order_id,
            file_id=file_id,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size
        )
        session.add(doc)
        session.flush()
        return doc
