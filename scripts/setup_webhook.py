"""
ابزار خط فرمان راه‌اندازی و مدیریت وب‌هوک تلگرام (scripts/setup_webhook.py)
سامانه «کافی نت لیمو».
این اسکریپت منحصراً با کتابخانه استاندارد پایتون پیاده‌سازی شده و از توکن به صورت کاملاً امن محافظت می‌کند.
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


TELEGRAM_API_BASE = "https://api.telegram.org/bot"


def mask_token(token: str) -> str:
    """پنهان‌سازی بخش عمده توکن جهت جلوگیری از نشت در خروجی لاگ‌ها."""
    if not token or len(token) < 10:
        return "***"
    return f"{token[:6]}...{token[-4:]}"


def execute_telegram_method(
    method: str,
    payload: Optional[Dict[str, Any]] = None,
    bot_token: Optional[str] = None,
    opener: Optional[Any] = None
) -> Dict[str, Any]:
    """
    اجرای متدهای رسمی Telegram Bot API با ارسال درخواست امن HTTPS.
    """
    token = bot_token or os.environ.get("BOT_TOKEN")
    if not token:
        raise ValueError("خطا: توکن ربات (BOT_TOKEN) مشخص نشده است. لطفاً متغیر محیطی BOT_TOKEN را تنظیم فرمایید.")

    url = f"{TELEGRAM_API_BASE}{token}/{method}"
    data = None
    headers = {"User-Agent": "LimoCafeBot-WebhookManager/1.0"}

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"

    req = urllib.request.Request(url, data=data, headers=headers)

    try:
        call_url = opener.open if opener else urllib.request.urlopen
        with call_url(req, timeout=15) as resp:
            content = resp.read().decode("utf-8")
            return json.loads(content)
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8")
        try:
            parsed = json.loads(err_body)
            desc = parsed.get("description", err_body)
        except Exception:
            desc = err_body
        raise RuntimeError(f"خطای وب‌سرویس تلگرام (HTTP {exc.code}): {desc}")
    except Exception as exc:
        raise RuntimeError(f"خطا در برقراری ارتباط با سرورهای تلگرام: {exc}")


def get_me(bot_token: Optional[str] = None, opener: Optional[Any] = None) -> Dict[str, Any]:
    """بررسی مشخصات و فعال بودن توکن ربات."""
    return execute_telegram_method("getMe", bot_token=bot_token, opener=opener)


def get_webhook_info(bot_token: Optional[str] = None, opener: Optional[Any] = None) -> Dict[str, Any]:
    """استعلام وضعیت فعلی وب‌هوک ربات."""
    return execute_telegram_method("getWebhookInfo", bot_token=bot_token, opener=opener)


def set_webhook(
    url: str,
    secret_token: Optional[str] = None,
    drop_pending_updates: bool = False,
    bot_token: Optional[str] = None,
    opener: Optional[Any] = None
) -> Dict[str, Any]:
    """
    ثبت وب‌هوک رسمی تلگرام با اعمال هدر محرمانه و فیلتر پیام‌ها.
    """
    payload: Dict[str, Any] = {
        "url": url,
        "allowed_updates": ["message", "callback_query"],
        "drop_pending_updates": drop_pending_updates
    }
    if secret_token:
        payload["secret_token"] = secret_token

    return execute_telegram_method("setWebhook", payload=payload, bot_token=bot_token, opener=opener)


def delete_webhook(
    drop_pending_updates: bool = False,
    bot_token: Optional[str] = None,
    opener: Optional[Any] = None
) -> Dict[str, Any]:
    """حذف وب‌هوک تلگرام جهت جابه‌جایی یا توقف پردازش وب‌هوک."""
    payload = {"drop_pending_updates": drop_pending_updates}
    return execute_telegram_method("deleteWebhook", payload=payload, bot_token=bot_token, opener=opener)


def main():
    parser = argparse.ArgumentParser(description="ابزار مدیریت وب‌هوک ربات تلگرام «کافی نت لیمو»")
    parser.add_argument("--token", help="توکن ربات تلگرام (پیش‌فرض: متغیر محیطی BOT_TOKEN)")
    subparsers = parser.add_subparsers(dest="action", help="عملیات موردنظر")

    # getMe
    subparsers.add_parser("me", help="تست اتصال و نمایش مشخصات ربات (getMe)")

    # getWebhookInfo
    subparsers.add_parser("info", help="مشاهده وضعیت وب‌هوک فعال (getWebhookInfo)")

    # setWebhook
    set_parser = subparsers.add_parser("set", help="ثبت وب‌هوک تلگرام (setWebhook)")
    set_parser.add_argument("--url", required=True, help="نشانی کامل اندپوینت وب‌هوک (مثال: Worker URL)")
    set_parser.add_argument("--secret", help="هدر امنیتی محرمانه (Secret Token)")
    set_parser.add_argument("--drop-pending", action="store_true", help="نادیده‌گرفتن پیام‌های معلق قدیمی")

    # deleteWebhook
    del_parser = subparsers.add_parser("delete", help="حذف وب‌هوک تلگرام (deleteWebhook)")
    del_parser.add_argument("--drop-pending", action="store_true", help="حذف تمام پیام‌های دریافت‌نشده صف")

    args = parser.parse_args()
    if not args.action:
        parser.print_help()
        sys.exit(1)

    try:
        if args.action == "me":
            res = get_me(bot_token=args.token)
            print("✅ وضعیت اتصال ربات به تلگرام: موفق")
            print(json.dumps(res, indent=2, ensure_ascii=False))

        elif args.action == "info":
            res = get_webhook_info(bot_token=args.token)
            print("📋 وضعیت وب‌هوک:")
            print(json.dumps(res, indent=2, ensure_ascii=False))

        elif args.action == "set":
            res = set_webhook(
                url=args.url,
                secret_token=args.secret,
                drop_pending_updates=args.drop_pending,
                bot_token=args.token
            )
            print(f"✅ وب‌هوک با موفقیت بر روی {args.url} تنظیم گردید.")
            print(json.dumps(res, indent=2, ensure_ascii=False))

        elif args.action == "delete":
            res = delete_webhook(drop_pending_updates=args.drop_pending, bot_token=args.token)
            print("🗑 وب‌هوک با موفقیت حذف گردید.")
            print(json.dumps(res, indent=2, ensure_ascii=False))

    except Exception as exc:
        print(f"❌ خطا: {exc}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
