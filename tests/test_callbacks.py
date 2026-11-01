"""
آزمون‌های خودکار ماژول تعاملات دکمه‌های شیشه‌ای و ناوبری منوها (bot/callbacks.py)
"""

import unittest
from core.config import Settings
from core.security import AccessControl
from core.throttling import Throttler
from core.database import DatabaseManager
from services.catalog import CatalogService
from bot.models import TelegramUser, CallbackQuery
from bot.dispatcher import BotDispatcher
from bot.callbacks import (
    SERVICES_HEADER_TEXT,
    TRACKING_INFO_TEXT,
    REMINDERS_INFO_TEXT,
    OPERATOR_CONTACT_TEXT,
    ADMIN_STATS_TEXT,
    ADMIN_ORDERS_TEXT,
    ADMIN_MONITORS_TEXT
)
from bot.handlers import WELCOME_TEXT, ACCESS_DENIED_TEXT


class TestCallbacks(unittest.TestCase):
    """مجموعه آزمون‌های رفتار ناوبری دکمه‌های شیشه‌ای و کنترل دسترسی کالبک‌ها."""

    def setUp(self):
        self.admin_id = 123456789
        self.regular_user_id = 987654321

        self.admin_user = TelegramUser(
            id=self.admin_id,
            first_name="مدیر سیستم",
            username="admin_user"
        )
        self.regular_user = TelegramUser(
            id=self.regular_user_id,
            first_name="مشتری",
            username="regular_user"
        )

        self.settings = Settings(admin_id=self.admin_id)
        self.access_control = AccessControl(self.settings)
        self.throttler = Throttler(rate_limit_seconds=0.5, max_burst=5)

        # ساخت دیتابیس حافظه‌ای و بارگذاری کاتالوگ خدمات
        self.db_manager = DatabaseManager("sqlite:///:memory:")
        self.db_manager.init_db()
        with self.db_manager.get_session() as session:
            CatalogService.seed_initial_catalog(session)

        self.dispatcher = BotDispatcher(self.access_control, self.throttler, self.db_manager)

    def tearDown(self):
        self.db_manager.drop_db()

    def test_services_list_callback_dynamic(self):
        """آزمون کلیک روی فهرست خدمات: استخراج پویا از دیتابیس و نمایش دکمه‌ها."""
        query = CallbackQuery(
            id="cb_1",
            from_user=self.regular_user,
            data="services_list"
        )
        response = self.dispatcher.dispatch_callback(query, current_time=10.0)

        self.assertEqual(response.chat_id, self.regular_user_id)
        self.assertEqual(response.text, SERVICES_HEADER_TEXT)
        self.assertIsNotNone(response.reply_markup)

        button_callbacks = [btn.callback_data for row in response.reply_markup for btn in row]
        self.assertIn("svc_EMT_VERIFICATION", button_callbacks)
        self.assertIn("svc_SANJESH_REGISTRATION", button_callbacks)
        self.assertIn("back_to_main", button_callbacks)

    def test_service_details_emt(self):
        """آزمون مشاهده جزئیات خدمت تاییدیه تحصیلی (مدارک، فیلدها و لینک رسمی)."""
        query = CallbackQuery(
            id="cb_emt",
            from_user=self.regular_user,
            data="svc_EMT_VERIFICATION"
        )
        response = self.dispatcher.dispatch_callback(query, current_time=15.0)

        self.assertIn("استعلام تاییدیه تحصیلی و کد صحت", response.text)
        self.assertIn("https://emt.medu.ir/", response.text)
        self.assertIn("کد ملی ۱۰ رقمی", response.text)
        self.assertIn("تصویر باکیفیت مدرک تحصیلی", response.text)

    def test_service_details_sanjesh(self):
        """آزمون مشاهده جزئیات خدمت سازمان سنجش."""
        query = CallbackQuery(
            id="cb_sanjesh",
            from_user=self.regular_user,
            data="svc_SANJESH_REGISTRATION"
        )
        response = self.dispatcher.dispatch_callback(query, current_time=16.0)

        self.assertIn("ثبت‌نام آزمون‌های سراسری سازمان سنجش", response.text)
        self.assertIn("https://www.sanjesh.org/", response.text)
        self.assertIn("عکس پرسنلی", response.text)

    def test_order_tracking_callback(self):
        """آزمون کلیک روی پیگیری سفارش: توضیحات کد رهگیری یکتا و دکمه بازگشت."""
        query = CallbackQuery(
            id="cb_2",
            from_user=self.regular_user,
            data="order_tracking"
        )
        response = self.dispatcher.dispatch_callback(query, current_time=20.0)

        self.assertEqual(response.text, TRACKING_INFO_TEXT)
        self.assertEqual(response.reply_markup[0][0].callback_data, "back_to_main")

    def test_reminders_callback(self):
        """آزمون کلیک روی یادآورها: نمایش توضیحات یادآور تقویمی."""
        query = CallbackQuery(
            id="cb_3",
            from_user=self.regular_user,
            data="reminders_menu"
        )
        response = self.dispatcher.dispatch_callback(query, current_time=30.0)

        self.assertEqual(response.text, REMINDERS_INFO_TEXT)

    def test_contact_operator_callback(self):
        """آزمون کلیک روی ارتباط با اپراتور: راهنمای هماهنگی مستقیم."""
        query = CallbackQuery(
            id="cb_4",
            from_user=self.regular_user,
            data="contact_operator"
        )
        response = self.dispatcher.dispatch_callback(query, current_time=40.0)

        self.assertEqual(response.text, OPERATOR_CONTACT_TEXT)

    def test_back_to_main_callback(self):
        """آزمون کلیک روی دکمه بازگشت به منوی اصلی."""
        query = CallbackQuery(
            id="cb_5",
            from_user=self.regular_user,
            data="back_to_main"
        )
        response = self.dispatcher.dispatch_callback(query, current_time=50.0)

        self.assertEqual(response.text, WELCOME_TEXT)
        self.assertEqual(len(response.reply_markup), 4)

    def test_admin_callbacks_authorized(self):
        """آزمون دسترسی مدیر به گزینه‌های مدیریتی (آمار، کارتابل، پایش)."""
        # آمار
        q_stats = CallbackQuery(id="cb_adm1", from_user=self.admin_user, data="admin_stats")
        resp_stats = self.dispatcher.dispatch_callback(q_stats, current_time=60.0)
        self.assertEqual(resp_stats.text, ADMIN_STATS_TEXT)

        # کارتابل
        q_orders = CallbackQuery(id="cb_adm2", from_user=self.admin_user, data="admin_orders")
        resp_orders = self.dispatcher.dispatch_callback(q_orders, current_time=61.0)
        self.assertEqual(resp_orders.text, ADMIN_ORDERS_TEXT)

        # پایش
        q_monitors = CallbackQuery(id="cb_adm3", from_user=self.admin_user, data="admin_monitors")
        resp_monitors = self.dispatcher.dispatch_callback(q_monitors, current_time=62.0)
        self.assertEqual(resp_monitors.text, ADMIN_MONITORS_TEXT)

    def test_admin_callback_blocked_for_regular_user(self):
        """آزمون مسدودسازی قطعی کالبک ادمین هنگامی که کاربر عادی سعی در فراخوانی آن دارد."""
        intruder_query = CallbackQuery(
            id="cb_hack",
            from_user=self.regular_user,
            data="admin_stats"
        )
        response = self.dispatcher.dispatch_callback(intruder_query, current_time=70.0)

        self.assertEqual(response.text, ACCESS_DENIED_TEXT)
        self.assertIn("خطای دسترسی", response.callback_alert)

    def test_callback_throttling_enforced(self):
        """آزمون مهار کلیک‌های رگباری روی دکمه‌ها توسط ماژول Throttling."""
        query = CallbackQuery(
            id="cb_fast",
            from_user=self.regular_user,
            data="services_list"
        )
        # کلیک اول موفق
        resp1 = self.dispatcher.dispatch_callback(query, current_time=80.0)
        self.assertEqual(resp1.text, SERVICES_HEADER_TEXT)

        # کلیک دوم بلافاصله پس از 0.1 ثانیه (باید مسدود شود)
        resp2 = self.dispatcher.dispatch_callback(query, current_time=80.1)
        self.assertIn("ارسال بیش از حد مجاز", resp2.text)
        self.assertIsNotNone(resp2.callback_alert)


if __name__ == "__main__":
    unittest.main()
