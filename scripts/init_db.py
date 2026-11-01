"""
اسکریپت مقداردهی اولیه و بازآفرینی پایگاه داده محلی (scripts/init_db.py)
سامانه «کافی نت لیمو».
جداول پایگاه داده را ایجاد نموده، کاتالوگ خدمات و سایت‌های پایش را ثبت و یکپارچگی را می‌سنجد.
"""

import os
import sys
import argparse

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from core.database import DatabaseManager
from services.catalog import CatalogService
from services.monitor import MonitorService
from core.diagnostics import SystemDiagnostics


def initialize_database(db_url: str = "sqlite:///storage/limo.db", recreate: bool = False, verify_only: bool = False):
    """ایجاد جداول، سیدینگ داده‌های اولیه و سنجش سلامت دیتابیس."""
    # اطمینان از وجود پوشه storage در صورت استفاده از مسیر محلی
    if db_url.startswith("sqlite:///storage/"):
        os.makedirs("storage", exist_ok=True)

    db_manager = DatabaseManager(db_url)

    if verify_only:
        with db_manager.get_session() as session:
            diag = SystemDiagnostics.run_health_check(session)
            print("🛡 گزارش وضعیت پایگاه داده:")
            print(f"• وضعیت: {diag['status']}")
            print(f"• یکپارچگی SQLite: {diag['database_integrity']}")
            print(f"• شمارنده‌ها: {diag['metrics']}")
            return diag

    if recreate:
        print("⚠️ در حال پاکسازی جداول قبلی...")
        db_manager.drop_db()

    print(f"📦 در حال ایجاد ساختار جداول در {db_url}...")
    db_manager.init_db()

    with db_manager.get_session() as session:
        # ۱. سیدینگ کاتالوگ خدمات (EMT, Sanjesh)
        CatalogService.seed_initial_catalog(session)
        print("✅ کاتالوگ خدمات اولیه با موفقیت مقداردهی شد.")

        # ۲. سیدینگ سایت‌های هدف پایش (۶ سایت)
        MonitorService.seed_initial_monitors(session)
        print("✅ سایت‌های هدف پایش با موفقیت ثبت گردید.")

        # ۳. ارزیابی سلامت و بررسی PRAGMA integrity_check
        diag = SystemDiagnostics.run_health_check(session)
        print(f"🟢 وضعیت نهایی: {diag['status']} (یکپارچگی دیتابیس: {diag['database_integrity']})")
        print(f"🕒 زمان سرور: {diag['shamsi_time']}")

    return diag


def main():
    parser = argparse.ArgumentParser(description="ابزار راه‌اندازی و مدیریت دیتابیس سامانه «کافی نت لیمو»")
    parser.add_argument("--db-url", default=os.environ.get("DATABASE_URL", "sqlite:///storage/limo.db"), help="رشته اتصال پایگاه داده")
    parser.add_argument("--recreate", action="store_true", help="حذف و بازسازی مجدد کلیه جداول")
    parser.add_argument("--verify", action="store_true", help="صرفاً ارزیابی سلامت و آمار جداول موجود")

    args = parser.parse_args()
    try:
        initialize_database(db_url=args.db_url, recreate=args.recreate, verify_only=args.verify)
    except Exception as exc:
        print(f"❌ خطا در آماده‌سازی پایگاه داده: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
