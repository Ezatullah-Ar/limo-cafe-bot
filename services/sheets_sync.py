"""
سرویس همگام‌سازی ابری سفارش‌ها با گوگل شیت (services/sheets_sync.py)
سامانه «کافی نت لیمو».
مسئول ارسال مشخصات و وضعیت پرونده‌ها به Google Apps Script و ثبت در اکسل/شیت آنلاین حسابداری.
"""

import json
import logging
import urllib.request
import urllib.error
from typing import Optional, Dict, Any

logger = logging.getLogger("sheets_sync")


class GoogleSheetsSyncService:
    """ارسال امن و تکرارپذیر رویدادهای سفارش به درگاه ابری گوگل شیت."""

    @staticmethod
    def sync_order(
        order: Any,
        sheet_url: Optional[str] = None,
        opener: Optional[Any] = None,
        timeout: float = 8.0
    ) -> Dict[str, Any]:
        """
        ارسال خلاصه اطلاعات پرونده به وب‌هوک گوگل شیت.
        در صورت عدم وجود sheet_url یا بروز خطای شبکه، خطایی بالا نمی‌آید و فقط لاگ ثبت می‌شود.
        """
        if not sheet_url:
            return {"status": "skipped", "message": "No sheet URL configured"}

        try:
            created_str = order.created_at.strftime("%Y-%m-%d %H:%M:%S") if getattr(order, "created_at", None) else ""
            user = getattr(order, "user", None)
            service = getattr(order, "service", None)

            payload: Dict[str, Any] = {
                "action": "sync_order",
                "tracking_code": getattr(order, "tracking_code", ""),
                "customer_id": getattr(user, "telegram_id", 0) if user else 0,
                "customer_name": getattr(user, "full_name", "ناشناس") if user else "ناشناس",
                "service_title": getattr(service, "title", "خدمت کافی‌نت") if service else "خدمت",
                "status": getattr(order, "status", "PENDING"),
                "created_at": created_str,
                "operator_notes": getattr(order, "operator_notes", "") or "",
                "form_data": getattr(order, "form_data", {}) or {}
            }

            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url=sheet_url,
                data=data,
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "User-Agent": "LimoCafeBot-SheetsSync/1.0"
                }
            )

            call = opener.open if opener else urllib.request.urlopen
            with call(req, timeout=timeout) as resp:
                resp_body = resp.read().decode("utf-8")
                try:
                    res_json = json.loads(resp_body)
                    logger.info("Order %s synced to Google Sheets successfully.", getattr(order, "tracking_code", ""))
                    return res_json
                except Exception:
                    return {"status": "success", "raw": resp_body}

        except Exception as exc:
            logger.warning("Failed to sync order to Google Sheets (non-critical): %s", exc)
            return {"status": "failed", "error": str(exc)}
