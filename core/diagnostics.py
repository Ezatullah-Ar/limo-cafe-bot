"""
ماژول پایش سلامت، عیب‌یابی و پشتیبان‌گیری (core/diagnostics.py) سامانه «کافی نت لیمو».
مسئول بررسی یکپارچگی پایگاه داده، ارزیابی آماری و تهیه نسخه‌های پشتیبان ساختاریافته (Disaster Recovery).
"""

from typing import Dict, Any, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import text
from core.models import User, ServiceItem, Order, Reminder, WebsiteMonitor, OrderAuditLog
from core.calendar import utc_to_jalali_datetime, format_jalali_date


class SystemDiagnostics:
    """ابزار تشخیصی جامع و ارزیابی سلامت زیرساخت سامانه."""

    @staticmethod
    def run_health_check(session: Session) -> Dict[str, Any]:
        """
        بررسی یکپارچگی و سلامت عمومی دیتابیس و مولفه‌های کلیدی.
        """
        # ۱. بررسی یکپارچگی SQLite (Integrity Check)
        db_integrity = "OK"
        try:
            result = session.execute(text("PRAGMA integrity_check")).scalar()
            if result != "ok":
                db_integrity = f"FAIL: {result}"
        except Exception as exc:
            db_integrity = f"ERROR: {exc}"

        # ۲. شمارش آماری موجودیت‌ها
        users_count = session.query(User).count()
        services_count = session.query(ServiceItem).count()
        orders_count = session.query(Order).count()
        pending_orders = session.query(Order).filter(Order.status == "PENDING").count()
        active_reminders = session.query(Reminder).filter(Reminder.is_sent == False).count()
        monitors_count = session.query(WebsiteMonitor).count()

        now_utc = datetime.now(timezone.utc)
        jy, jm, jd, h, m = utc_to_jalali_datetime(now_utc)
        shamsi_timestamp = f"{format_jalali_date(jy, jm, jd)} {h:02d}:{m:02d}"

        is_healthy = db_integrity == "OK"

        return {
            "status": "HEALTHY" if is_healthy else "UNHEALTHY",
            "shamsi_time": shamsi_timestamp,
            "database_integrity": db_integrity,
            "metrics": {
                "total_users": users_count,
                "active_services": services_count,
                "total_orders": orders_count,
                "pending_orders": pending_orders,
                "active_reminders": active_reminders,
                "monitored_sites": monitors_count
            }
        }

    @staticmethod
    def create_backup_snapshot(session: Session) -> Dict[str, Any]:
        """
        تولید نسخه پشتیبان امن (Backup Snapshot) بدون افشای کلیدهای محرمانه و توکن‌ها.
        """
        now_utc = datetime.now(timezone.utc)
        jy, jm, jd, h, m = utc_to_jalali_datetime(now_utc)

        snapshot: Dict[str, Any] = {
            "version": "1.0.0",
            "created_at_utc": now_utc.isoformat(),
            "created_at_shamsi": f"{format_jalali_date(jy, jm, jd)} {h:02d}:{m:02d}",
            "users": [],
            "orders": [],
            "reminders": [],
            "monitors": []
        }

        # کاربران
        for u in session.query(User).all():
            snapshot["users"].append({
                "telegram_id": u.telegram_id,
                "full_name": u.full_name,
                "username": u.username,
                "role": u.role
            })

        # سفارشات و لاگ‌ها
        for o in session.query(Order).all():
            snapshot["orders"].append({
                "tracking_code": o.tracking_code,
                "user_telegram_id": o.user.telegram_id,
                "service_code": o.service.code,
                "status": o.status,
                "form_data": o.form_data,
                "operator_notes": o.operator_notes,
                "documents_count": len(o.documents)
            })

        # یادآورها
        for r in session.query(Reminder).all():
            snapshot["reminders"].append({
                "user_telegram_id": r.user.telegram_id,
                "title": r.title,
                "shamsi_date": r.shamsi_date,
                "is_sent": r.is_sent
            })

        # مانیتورها
        for m in session.query(WebsiteMonitor).all():
            snapshot["monitors"].append({
                "code": m.code,
                "title": m.title,
                "url": m.url,
                "uptime_status": m.uptime_status,
                "service_status": m.service_status
            })

        return snapshot
