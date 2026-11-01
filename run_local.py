"""
نقطه ورود اجرای محلی یا سرور مجازی (run_local.py) سامانه «کافی نت لیمو».
امکان اجرای مستقل ربات با مکانیزم Long-Polling بدون نیاز به وب‌هوک و کلودفلر.
"""

import os
import sys
import logging
import argparse
import signal

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from core.config import Settings
from core.security import AccessControl
from core.throttling import Throttler
from core.database import DatabaseManager
from bot.fsm import FSMManager
from bot.dispatcher import BotDispatcher
from bot.polling import PollingRunner, TelegramClient
from services.catalog import CatalogService
from services.monitor import MonitorService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("run_local")


def load_env_file(filepath: str = ".env"):
    """بارگذاری ساده متغیرهای محیطی از فایل .env در غیاب بسته‌های جانبی."""
    if not os.path.exists(filepath):
        return
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k and k not in os.environ:
                    os.environ[k] = v
    except Exception as exc:
        logger.warning("Could not read %s: %s", filepath, exc)


def start_runner(token: str, admin_id: int, db_url: str = "sqlite:///storage/limo.db", poll_interval: float = 0.5):
    """آماده‌سازی و اجرای سرویس پولینگ محلی."""
    if not token:
        logger.error("BOT_TOKEN is required. Set BOT_TOKEN environment variable or use --token.")
        sys.exit(1)

    # اطمینان از وجود پوشه storage
    if db_url.startswith("sqlite:///storage/"):
        os.makedirs("storage", exist_ok=True)

    settings = Settings(admin_id=admin_id)
    access_control = AccessControl(settings)
    throttler = Throttler(rate_limit_seconds=1.0, max_burst=5)
    fsm_manager = FSMManager()

    db_manager = DatabaseManager(db_url)
    db_manager.init_db()

    # سیدینگ اولیه دیتابیس در صورت تازه بودن
    with db_manager.get_session() as session:
        CatalogService.seed_initial_catalog(session)
        MonitorService.seed_initial_monitors(session)

    dispatcher = BotDispatcher(
        access_control=access_control,
        throttler=throttler,
        db_manager=db_manager,
        fsm_manager=fsm_manager
    )

    client = TelegramClient(token)

    # بررسی هویت بات
    try:
        me = client.call_method("getMe")
        if me.get("ok"):
            bot_user = me["result"]
            logger.info("Bot authenticated: @%s (%s, ID: %s)", bot_user.get("username"), bot_user.get("first_name"), bot_user.get("id"))
    except Exception as exc:
        logger.error("Failed to connect to Telegram: %s", exc)
        sys.exit(2)

    # در صورتی که وب‌هوک فعال باشد، برای شروع پولینگ باید حذف شود
    try:
        wh_info = client.call_method("getWebhookInfo")
        if wh_info.get("ok") and wh_info.get("result", {}).get("url"):
            active_url = wh_info["result"]["url"]
            logger.warning("Active webhook detected: %s. Deleting webhook to enable long-polling...", active_url)
            client.call_method("deleteWebhook", {"drop_pending_updates": False})
            logger.info("Webhook deleted. Polling enabled.")
    except Exception as exc:
        logger.warning("Could not check/delete webhook: %s", exc)

    runner = PollingRunner(
        bot_token=token,
        dispatcher=dispatcher,
        db_manager=db_manager,
        client=client
    )

    # مدیریت سیگنال‌های خروج
    def handle_signal(sig, frame):
        logger.info("Signal %s received. Shutting down...", sig)
        runner.stop()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    logger.info("Starting Polling Runner for Limo Cafe Bot...")
    runner.start(poll_interval=poll_interval)


def main():
    load_env_file()

    parser = argparse.ArgumentParser(description="رانر محلی و سرور ربات کافی نت لیمو (Long-Polling)")
    parser.add_argument("--token", default=os.environ.get("BOT_TOKEN"), help="توکن ربات تلگرام")
    parser.add_argument("--admin-id", type=int, default=int(os.environ.get("ADMIN_ID", "0")), help="شناسه عددی مدیر تلگرام")
    parser.add_argument("--db-url", default=os.environ.get("DATABASE_URL", "sqlite:///storage/limo.db"), help="نشانی اتصال دیتابیس")
    parser.add_argument("--interval", type=float, default=0.5, help="فاصله بین درخواست‌های پولینگ (ثانیه)")

    args = parser.parse_args()

    start_runner(
        token=args.token,
        admin_id=args.admin_id,
        db_url=args.db_url,
        poll_interval=args.interval
    )


if __name__ == "__main__":
    main()
