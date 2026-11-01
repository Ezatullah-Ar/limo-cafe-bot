"""
سرویس مدیریت پرونده مشتریان (CRM)، سوابق و تخصیص اپراتور سامانه «کافی نت لیمو».
این ماژول پرونده هویتی، مالی، سفارشات و گفت‌وگوهای مشتریان را با رعایت عایق‌بندی داده‌ها مدیریت می‌کند.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from core.models import User, Order, Wallet, WalletTransaction, SupportThread, OrderAuditLog, ServiceItem


class CRMService:
    """سرویس مدیریت پرونده مشتریان و اپراتورهای کافی‌نت لیمو."""

    @staticmethod
    def get_customers(
        session: Session,
        query_str: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        دریافت فهرست مشتریان به همراه شمارش سفارش‌ها، موجودی کیف پول و تیکت‌ها با فیلتر جست‌وجو.
        """
        query = session.query(User)
        if query_str:
            clean_q = query_str.strip()
            like_pattern = f"%{clean_q}%"
            if clean_q.isdigit():
                query = query.filter(
                    (User.telegram_id == int(clean_q)) |
                    (User.full_name.ilike(like_pattern)) |
                    (User.username.ilike(like_pattern))
                )
            else:
                query = query.filter(
                    (User.full_name.ilike(like_pattern)) |
                    (User.username.ilike(like_pattern))
                )

        users = query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()

        results = []
        for u in users:
            orders_count = session.query(Order).filter_by(user_id=u.id).count()
            wallet = session.query(Wallet).filter_by(user_id=u.id).first()
            wallet_balance = wallet.balance if wallet else 0
            active_tickets = session.query(SupportThread).filter(
                SupportThread.user_id == u.id,
                SupportThread.status != "CLOSED"
            ).count()

            results.append({
                "id": u.id,
                "telegram_id": u.telegram_id,
                "full_name": u.full_name,
                "username": u.username,
                "role": u.role,
                "orders_count": orders_count,
                "wallet_balance": wallet_balance,
                "active_tickets": active_tickets,
                "created_at": u.created_at.isoformat() if u.created_at else None
            })
        return results

    @staticmethod
    def get_customer_dossier(session: Session, user_id: int) -> Optional[Dict[str, Any]]:
        """
        استخراج پرونده جامع و کامل یک مشتری شامل اطلاعات فردی، سفارش‌ها، کیف پول و تیکت‌های پشتیبانی.
        """
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return None

        # اطلاعات کیف پول و تراکنش‌ها
        wallet = session.query(Wallet).filter_by(user_id=user.id).first()
        transactions = []
        if wallet:
            tx_rows = session.query(WalletTransaction).filter_by(wallet_id=wallet.id).order_by(
                WalletTransaction.created_at.desc()
            ).limit(20).all()
            for tx in tx_rows:
                transactions.append({
                    "id": tx.id,
                    "tracking_ref": tx.tracking_ref,
                    "transaction_type": tx.transaction_type,
                    "amount": tx.amount,
                    "balance_after": tx.balance_after,
                    "notes": tx.notes,
                    "created_at": tx.created_at.isoformat() if tx.created_at else None
                })

        # سوابق سفارشات متقاضی
        orders = session.query(Order).filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
        orders_list = []
        order_ids = [o.id for o in orders]
        for o in orders:
            orders_list.append({
                "id": o.id,
                "tracking_code": o.tracking_code,
                "service_code": o.service.code if o.service else None,
                "service_title": o.service.title if o.service else "خدمت نامشخص",
                "status": o.status,
                "operator_notes": o.operator_notes,
                "form_data": o.form_data or {},
                "created_at": o.created_at.isoformat() if o.created_at else None,
                "updated_at": o.updated_at.isoformat() if o.updated_at else None
            })

        # تیکت‌های پشتیبانی
        threads = session.query(SupportThread).filter_by(user_id=user.id).order_by(SupportThread.updated_at.desc()).all()
        threads_list = []
        for th in threads:
            threads_list.append({
                "id": th.id,
                "status": th.status,
                "subject": th.subject,
                "last_message_at": th.last_message_at.isoformat() if th.last_message_at else None,
                "created_at": th.created_at.isoformat() if th.created_at else None
            })

        # لاگ‌های حسابرسی مرتبط با سفارشات این مشتری
        audit_logs = []
        if order_ids:
            logs = session.query(OrderAuditLog).filter(OrderAuditLog.order_id.in_(order_ids)).order_by(
                OrderAuditLog.created_at.desc()
            ).limit(30).all()
            for l in logs:
                audit_logs.append({
                    "id": l.id,
                    "order_id": l.order_id,
                    "actor_id": l.actor_id,
                    "action": "ASSIGN_OPERATOR" if "تخصیص به اپراتور" in (l.note or "") else "STATUS_CHANGE",
                    "from_status": l.from_status,
                    "to_status": l.to_status,
                    "note": l.note,
                    "created_at": l.created_at.isoformat() if l.created_at else None
                })

        return {
            "user": {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "full_name": user.full_name,
                "username": user.username,
                "role": user.role,
                "created_at": user.created_at.isoformat() if user.created_at else None
            },
            "wallet": {
                "balance": wallet.balance if wallet else 0,
                "is_frozen": wallet.is_frozen if wallet else False
            },
            "orders": orders_list,
            "transactions": transactions,
            "support_threads": threads_list,
            "audit_logs": audit_logs
        }

    @staticmethod
    def assign_operator_to_order(
        session: Session,
        order_id: int,
        operator_name: str,
        actor_id: Optional[int] = None,
        note: Optional[str] = None
    ) -> Optional[Order]:
        """
        تخصیص یا تغییر اپراتور مسئول پرونده و ثبت رسمی در لاگ‌های حسابرسی.
        """
        order = session.query(Order).filter_by(id=order_id).first()
        if not order:
            return None

        assign_note = f"تخصیص به اپراتور مسئول: {operator_name}"
        if note:
            assign_note += f" | {note}"

        order.operator_notes = assign_note
        session.flush()

        # ثبت تاریخچه عملیات در جدول حسابرسی
        audit = OrderAuditLog(
            order_id=order.id,
            actor_id=actor_id or 1,
            from_status=order.status,
            to_status=order.status,
            note=assign_note
        )
        session.add(audit)
        session.flush()
        return order
