"""
آزمون‌های خودکار سیستم پایش هوشمند سایت‌های هدف (Phase 8: Smart Website Monitoring)
"""

import unittest
from unittest.mock import patch
from core.config import Settings
from core.security import AccessControl
from core.throttling import Throttler
from core.database import DatabaseManager
from services.catalog import CatalogService
from services.monitor import MonitorService
from core.models import WebsiteMonitor
from bot.models import TelegramUser, CallbackQuery
from bot.dispatcher import BotDispatcher
from bot.handlers import ACCESS_DENIED_TEXT


class TestMonitorService(unittest.TestCase):
    """مجموعه آزمون‌های راستی‌آزمایی هسته پایش سایت‌ها، تفکیک Uptime از وضعیت خدمت و دفاع SSRF."""

    def setUp(self):
        self.admin_id = 123456789
        self.regular_user_id = 987654321

        self.admin_user = TelegramUser(id=self.admin_id, first_name="مدیر سامانه", username="admin_limo")
        self.regular_user = TelegramUser(id=self.regular_user_id, first_name="کاربر عادی", username="regular_user")

        self.settings = Settings(admin_id=self.admin_id)
        self.access_control = AccessControl(self.settings)
        self.throttler = Throttler(rate_limit_seconds=0.0, max_burst=1000)

        self.db_manager = DatabaseManager("sqlite:///:memory:")
        self.db_manager.init_db()

        with self.db_manager.get_session() as session:
            CatalogService.seed_initial_catalog(session)
            MonitorService.seed_initial_monitors(session)

        self.dispatcher = BotDispatcher(
            access_control=self.access_control,
            throttler=self.throttler,
            db_manager=self.db_manager
        )

    def tearDown(self):
        self.db_manager.drop_db()

    def test_seed_initial_monitors_and_idempotency(self):
        """آزمون ثبت ۶ سامانه اولیه مصوب در سند قوانین و عدم ایجاد داده‌های تکراری در اجرای مجدد."""
        with self.db_manager.get_session() as session:
            monitors = MonitorService.get_monitors(session)
            self.assertEqual(len(monitors), 6)
            codes = {m.code for m in monitors}
            self.assertIn("SANJESH", codes)
            self.assertIn("EMT_MEDU", codes)
            self.assertIn("PNU_GOLESTAN", codes)
            self.assertIn("IAU_EDU", codes)
            self.assertIn("ADAB_SAORG", codes)
            self.assertIn("IVSF", codes)

            # اجرای مجدد Seeding
            MonitorService.seed_initial_monitors(session)
            monitors_after = MonitorService.get_monitors(session)
            self.assertEqual(len(monitors_after), 6)

    def test_check_target_open_registration(self):
        """آزمون کشف باز بودن ثبت‌نام در صورت وجود کلمات کلیدی مجاز در محتوای سایت."""
        def mock_fetcher_open(url, timeout):
            return 200, "اطلاعیه: سیستم ثبت نام آزمون سراسری هم‌اکنون فعال است.", 350

        with self.db_manager.get_session() as session:
            sanjesh = MonitorService.get_monitor_by_code(session, "SANJESH")
            res = MonitorService.check_target(session, sanjesh, http_fetcher=mock_fetcher_open)

            self.assertEqual(res["uptime"], "UP")
            self.assertEqual(res["service"], "OPEN")
            self.assertEqual(sanjesh.uptime_status, "UP")
            self.assertEqual(sanjesh.service_status, "OPEN")
            self.assertIn("فعال", sanjesh.status_message)
            self.assertEqual(len(sanjesh.logs), 1)

    def test_check_target_closed_registration(self):
        """آزمون کشف بسته بودن ثبت‌نام در صورت وجود کلمات کلیدی پایان مهلت."""
        def mock_fetcher_closed(url, timeout):
            return 200, "هشدار: مهلت ثبت نام به پایان رسید.", 400

        with self.db_manager.get_session() as session:
            sanjesh = MonitorService.get_monitor_by_code(session, "SANJESH")
            res = MonitorService.check_target(session, sanjesh, http_fetcher=mock_fetcher_closed)

            self.assertEqual(res["uptime"], "UP")
            self.assertEqual(res["service"], "CLOSED")
            self.assertIn("بسته", sanjesh.status_message)

    def test_check_target_generic_200_is_not_assumed_open(self):
        """
        اصل حاکم بر پایش: دریافت پاسخ HTTP 200 به تنهایی اثبات‌کننده باز بودن ثبت‌نام نیست.
        در صورت عدم وجود کلمات کلیدی باز/بسته، وضعیت باید UNKNOWN بماند.
        """
        def mock_fetcher_generic(url, timeout):
            return 200, "صفحه اصلی پورتال سازمان سنجش آموزش کشور - اخبار و اطلاعیه‌ها", 200

        with self.db_manager.get_session() as session:
            sanjesh = MonitorService.get_monitor_by_code(session, "SANJESH")
            res = MonitorService.check_target(session, sanjesh, http_fetcher=mock_fetcher_generic)

            self.assertEqual(res["uptime"], "UP")
            self.assertEqual(res["service"], "UNKNOWN")
            self.assertIn("اصل تفکیک", sanjesh.status_message)

    def test_check_target_slow_response_degraded(self):
        """آزمون افت وضعیت سرور به DEGRADED در صورت پاسخ کند (بیش از ۴۵۰۰ میلی‌ثانیه)."""
        def mock_fetcher_slow(url, timeout):
            return 200, "ثبت نام استعلام مدارک", 5500

        with self.db_manager.get_session() as session:
            emt = MonitorService.get_monitor_by_code(session, "EMT_MEDU")
            res = MonitorService.check_target(session, emt, http_fetcher=mock_fetcher_slow)

            self.assertEqual(res["uptime"], "DEGRADED")
            self.assertEqual(res["service"], "OPEN")

    def test_check_target_server_error_and_timeout(self):
        """آزمون تشخیص قطعی سرور (DOWN) در اثر خطای HTTP 500 یا خطای شبکه."""
        def mock_fetcher_503(url, timeout):
            return 503, "Service Unavailable", 120

        with self.db_manager.get_session() as session:
            ivsf = MonitorService.get_monitor_by_code(session, "IVSF")
            res = MonitorService.check_target(session, ivsf, http_fetcher=mock_fetcher_503)

            self.assertEqual(res["uptime"], "DOWN")
            self.assertEqual(res["service"], "UNKNOWN")

        # خطای عدم برقراری اتصال
        def mock_fetcher_error(url, timeout):
            raise TimeoutError("Connection timed out")

        with self.db_manager.get_session() as session:
            pnu = MonitorService.get_monitor_by_code(session, "PNU_GOLESTAN")
            res = MonitorService.check_target(session, pnu, http_fetcher=mock_fetcher_error)

            self.assertEqual(res["uptime"], "DOWN")
            self.assertIn("عدم پاسخ", pnu.status_message)

    def test_ssrf_blocked_target(self):
        """آزمون مهار مانیتور دارای نشانی شبکه داخلی توسط سپر امنیتی SSRF."""
        with self.db_manager.get_session() as session:
            unsafe_monitor = WebsiteMonitor(
                code="METADATA_TEST",
                title="تست متادیتا",
                url="http://169.254.169.254/latest/meta-data/",
                uptime_status="UNKNOWN"
            )
            session.add(unsafe_monitor)
            session.flush()

            res = MonitorService.check_target(session, unsafe_monitor)
            self.assertEqual(res["uptime"], "DOWN")
            self.assertIn("SSRF", res["message"])

    @patch("services.monitor.is_safe_url", return_value=(True, "Safe in test"))
    @patch("services.monitor.default_http_fetcher", return_value=(200, "سیستم ثبت نام آزمون سراسری فعال است", 120))
    def test_admin_monitors_callbacks(self, mock_fetch, mock_ssrf):
        """آزمون مشاهده گزارش پایش و بررسی آنی از طریق منوی مدیریت ربات."""
        cb_view = CallbackQuery(id="cb_mon_view", from_user=self.admin_user, data="admin_monitors")
        resp_view = self.dispatcher.dispatch_callback(cb_view)

        self.assertIn("وضعیت زنده پایش هوشمند سامانه‌ها", resp_view.text)
        self.assertIn("سازمان سنجش", resp_view.text)
        self.assertIn("تأییدیه تحصیلی", resp_view.text)

        # کلیک روی بررسی آنی
        cb_check = CallbackQuery(id="cb_mon_check", from_user=self.admin_user, data="admin_check_monitors_now")
        resp_check = self.dispatcher.dispatch_callback(cb_check)
        self.assertEqual(resp_check.callback_alert, "پایش آنی کلیه سایت‌ها با موفقیت انجام شد.")
        self.assertIn("وضعیت زنده پایش", resp_check.text)

    def test_unauthorized_user_blocked_from_monitor_callbacks(self):
        """آزمون مهار قطعی کاربر غیرمجاز از دسترسی به اطلاعات یا اجرای پایش سایت‌ها."""
        for cb_name in ("admin_monitors", "admin_check_monitors_now"):
            cb_hack = CallbackQuery(id="cb_hack", from_user=self.regular_user, data=cb_name)
            resp = self.dispatcher.dispatch_callback(cb_hack)
            self.assertEqual(resp.text, ACCESS_DENIED_TEXT)
            self.assertIn("خطای دسترسی", resp.callback_alert)


if __name__ == "__main__":
    unittest.main()
