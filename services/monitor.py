"""
سرویس پایش هوشمند سایت‌های هدف (services/monitor.py) سامانه «کافی نت لیمو».
مسئول تفکیک دسترس‌پذیری سرور (Uptime) از وضعیت فعال بودن ثبت‌نام (Service Status)،
اعمال تدابیر امنیتی SSRF Shield، ثبت وقایع و ارزیابی ادواری سایت‌های هدف.
"""

from datetime import datetime, timezone
import time
import urllib.request
import urllib.error
from typing import List, Optional, Dict, Any, Callable, Tuple
from sqlalchemy.orm import Session
from core.models import WebsiteMonitor, MonitorLog
from core.ssrf import is_safe_url


INITIAL_TARGET_SITES = [
    {
        "code": "IVSF",
        "title": "سامانه دریافت نوبت تثبیت هویت",
        "url": "http://ivsf.nsia.gov.af/",
        "detection_rule": {
            "open_keywords": ["نوبت دهی", "دریافت نوبت", "ثبت نام"],
            "closed_keywords": ["تکمیل ظرفیت", "نوبتی وجود ندارد", "بسته است", "غیرفعال"]
        }
    },
    {
        "code": "ADAB_SAORG",
        "title": "سامانه امور دانشجویان بین‌الملل (ادب)",
        "url": "https://adab.saorg.ir/PortalADAB/Home/LandingPage",
        "detection_rule": {
            "open_keywords": ["ثبت نام دانشجو", "پذیرش دانشجویان", "ورود متقاضی"],
            "closed_keywords": ["مهلت به پایان رسیده", "سامانه غیرفعال است"]
        }
    },
    {
        "code": "PNU_GOLESTAN",
        "title": "سامانه گلستان دانشگاه پیام نور",
        "url": "https://osreg.pnu.ac.ir/forms/authenticateuser/main.htm",
        "detection_rule": {
            "open_keywords": ["ورود به سیستم", "شناسه کاربری", "کد امنیتی"],
            "closed_keywords": ["سیستم موقتاً قطع است", "در دست تعمیر"]
        }
    },
    {
        "code": "IAU_EDU",
        "title": "سامانه آموزشی دانشگاه آزاد (آموزشیار)",
        "url": "https://edu.iau.ac.ir/",
        "detection_rule": {
            "open_keywords": ["ورود به سامانه", "دانشجویان", "انتخاب واحد"],
            "closed_keywords": ["سیستم در حال به‌روزرسانی است", "قطع موقت"]
        }
    },
    {
        "code": "SANJESH",
        "title": "سازمان سنجش آموزش کشور",
        "url": "https://www.sanjesh.org/",
        "detection_rule": {
            "open_keywords": ["ثبت نام آزمون", "سیستم ثبت نام", "آغاز نام نویسی"],
            "closed_keywords": ["مهلت ثبت نام به پایان رسید", "پایان مهلت ثبت نام"]
        }
    },
    {
        "code": "EMT_MEDU",
        "title": "سامانه دریافت تأییدیه تحصیلی (آموزش و پرورش)",
        "url": "https://emt.medu.ir/",
        "detection_rule": {
            "open_keywords": ["ثبت نام استعلام مدارک", "ثبت تاییدیه تحصیلی", "پیگیری استعلام"],
            "closed_keywords": ["سامانه در دسترس نیست", "در حال بروزرسانی"]
        }
    }
]


def default_http_fetcher(url: str, timeout_seconds: float = 8.0) -> Tuple[int, str, int]:
    """دریافت محتوای صفحه وب با کلاینت استاندارد پایتون و ارسال User-Agent اختصاصی."""
    req = urllib.request.Request(
        url=url,
        headers={
            "User-Agent": "LimoBot-Monitor/1.0 (Smart Café Assistant; +https://t.me/LimoBot)"
        }
    )
    start_time = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
            elapsed_ms = int((time.time() - start_time) * 1000)
            code = resp.getcode()
            body = resp.read().decode("utf-8", errors="replace")
            return code, body, elapsed_ms
    except urllib.error.HTTPError as http_err:
        elapsed_ms = int((time.time() - start_time) * 1000)
        body = http_err.read().decode("utf-8", errors="replace") if hasattr(http_err, "read") else ""
        return http_err.code, body, elapsed_ms
    except Exception as exc:
        elapsed_ms = int((time.time() - start_time) * 1000)
        raise exc


class MonitorService:
    """سرویس مدیریت مانیتورها، پایش سلامت و کشف وضعیت خدمات سایت‌های هدف."""

    @staticmethod
    def seed_initial_monitors(session: Session) -> None:
        """مقداردهی اولیه سایت‌های مصوب در سند قوانین پروژه به صورت Idempotent."""
        for site_data in INITIAL_TARGET_SITES:
            existing = session.query(WebsiteMonitor).filter(WebsiteMonitor.code == site_data["code"]).first()
            if not existing:
                monitor = WebsiteMonitor(
                    code=site_data["code"],
                    title=site_data["title"],
                    url=site_data["url"],
                    detection_rule=site_data["detection_rule"],
                    uptime_status="UNKNOWN",
                    service_status="UNKNOWN",
                    status_message="در انتظار اولین بررسی"
                )
                session.add(monitor)
        session.flush()

    @staticmethod
    def get_monitors(session: Session, active_only: bool = True) -> List[WebsiteMonitor]:
        """استخراج لیست مانیتورهای ثبت‌شده در سیستم."""
        query = session.query(WebsiteMonitor)
        if active_only:
            query = query.filter(WebsiteMonitor.is_active == True)
        return query.order_by(WebsiteMonitor.id.asc()).all()

    @staticmethod
    def get_monitor_by_code(session: Session, code: str) -> Optional[WebsiteMonitor]:
        """یافتن مانیتور بر اساس کد یکتا."""
        return session.query(WebsiteMonitor).filter(WebsiteMonitor.code == code).first()

    @staticmethod
    def check_target(
        session: Session,
        monitor: WebsiteMonitor,
        http_fetcher: Optional[Callable[[str, float], Tuple[int, str, int]]] = None,
        resolve_dns: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        بررسی سلامت و وضعیت خدمت با رعایت اصل تفکیک Uptime از وضعیت ثبت‌نام و محافظت SSRF.
        """
        fetcher = http_fetcher or default_http_fetcher
        should_resolve_dns = resolve_dns if resolve_dns is not None else (http_fetcher is None)

        # ۱. آزمون امنیتی SSRF Shield قبل از هرگونه تماس شبکه‌ای
        is_safe, ssrf_reason = is_safe_url(monitor.url, resolve_dns=should_resolve_dns)
        if not is_safe:
            monitor.uptime_status = "DOWN"
            monitor.service_status = "UNKNOWN"
            monitor.last_http_code = None
            monitor.last_response_time_ms = None
            monitor.status_message = f"خطای امنیتی SSRF: {ssrf_reason}"
            monitor.last_checked_at = datetime.now(timezone.utc)

            log_entry = MonitorLog(
                monitor_id=monitor.id,
                uptime_status="DOWN",
                service_status="UNKNOWN",
                details=monitor.status_message
            )
            session.add(log_entry)
            session.flush()

            return {
                "code": monitor.code,
                "uptime": "DOWN",
                "service": "UNKNOWN",
                "message": monitor.status_message
            }

        # ۲. برقراری اتصال HTTP
        try:
            http_code, html_body, response_time_ms = fetcher(monitor.url, 8.0)
        except Exception as exc:
            monitor.uptime_status = "DOWN"
            monitor.service_status = "UNKNOWN"
            monitor.last_http_code = None
            monitor.last_response_time_ms = None
            monitor.status_message = f"عدم پاسخ سرور یا خطای اتصال: {str(exc)[:150]}"
            monitor.last_checked_at = datetime.now(timezone.utc)

            log_entry = MonitorLog(
                monitor_id=monitor.id,
                uptime_status="DOWN",
                service_status="UNKNOWN",
                details=monitor.status_message
            )
            session.add(log_entry)
            session.flush()

            return {
                "code": monitor.code,
                "uptime": "DOWN",
                "service": "UNKNOWN",
                "message": monitor.status_message
            }

        # ۳. تحلیل بُعد دسترس‌پذیری سرور (Uptime)
        if 200 <= http_code < 400:
            uptime = "DEGRADED" if response_time_ms > 4500 else "UP"
        else:
            uptime = "DOWN"

        # ۴. تحلیل بُعد وضعیت ثبت‌نام / خدمت بر اساس قوانین تشخیص اختصاصی
        rule = monitor.detection_rule or {}
        open_keywords = rule.get("open_keywords", [])
        closed_keywords = rule.get("closed_keywords", [])

        service_status = "UNKNOWN"
        msg = ""

        if uptime in ("UP", "DEGRADED"):
            found_open = any(k in html_body for k in open_keywords)
            found_closed = any(k in html_body for k in closed_keywords)

            if found_closed:
                service_status = "CLOSED"
                msg = "ثبت‌نام بسته یا تکمیل ظرفیت شناسایی شد."
            elif found_open:
                service_status = "OPEN"
                msg = "سامانه فعال و ثبت‌نام در دسترس است."
            else:
                service_status = "UNKNOWN"
                msg = "سرور پاسخگو است؛ اما نشانه قطعی باز بودن ثبت‌نام در محتوا یافت نشد (اصل تفکیک Uptime از ثبت‌نام)."
        else:
            service_status = "UNKNOWN"
            msg = f"خطای سرور (کد وضعیت: {http_code})"

        # به‌روزرسانی مانیتور
        monitor.uptime_status = uptime
        monitor.service_status = service_status
        monitor.last_http_code = http_code
        monitor.last_response_time_ms = response_time_ms
        monitor.status_message = msg
        monitor.last_checked_at = datetime.now(timezone.utc)

        # ثبت لاگ بررسی
        log_entry = MonitorLog(
            monitor_id=monitor.id,
            uptime_status=uptime,
            service_status=service_status,
            http_code=http_code,
            response_time_ms=response_time_ms,
            details=msg
        )
        session.add(log_entry)
        session.flush()

        return {
            "code": monitor.code,
            "uptime": uptime,
            "service": service_status,
            "http_code": http_code,
            "response_time_ms": response_time_ms,
            "message": msg
        }

    @staticmethod
    def check_all(
        session: Session,
        http_fetcher: Optional[Callable[[str, float], Tuple[int, str, int]]] = None,
        resolve_dns: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """بررسی ترتیبی کلیه مانیتورهای فعال."""
        monitors = MonitorService.get_monitors(session, active_only=True)
        results = []
        for m in monitors:
            res = MonitorService.check_target(session, m, http_fetcher=http_fetcher, resolve_dns=resolve_dns)
            results.append(res)
        return results

    @staticmethod
    def format_monitors_report(monitors: List[WebsiteMonitor]) -> str:
        """قالب‌بندی کارت جامع وضعیت پایش سایت‌ها برای نمایش در پنل مدیریت ربات."""
        if not monitors:
            return "🌐 هیچ سایتی در فهرست پایش فعال نیست."

        lines = [
            "🌐 <b>وضعیت زنده پایش هوشمند سامانه‌ها:</b>\n",
            "<i>راهنما: وضعیت سرور (Uptime) | وضعیت ثبت‌نام (Service)</i>\n"
        ]

        uptime_icons = {"UP": "🟢", "DEGRADED": "🟡", "DOWN": "🔴", "UNKNOWN": "⚪"}
        service_icons = {"OPEN": "🔓 باز", "CLOSED": "🔒 بسته", "UNKNOWN": "❓ نامشخص"}

        for idx, m in enumerate(monitors, 1):
            u_icon = uptime_icons.get(m.uptime_status, "⚪")
            s_str = service_icons.get(m.service_status, "❓ نامشخص")
            rt_str = f"{m.last_response_time_ms}ms" if m.last_response_time_ms is not None else "—"

            lines.append(
                f"{idx}. <b>{m.title}</b>\n"
                f"   • سرور: {u_icon} {m.uptime_status} ({rt_str})\n"
                f"   • وضعیت خدمت: {s_str}\n"
                f"   • پیام: <i>{m.status_message or '—'}</i>\n"
            )

        return "\n".join(lines)
