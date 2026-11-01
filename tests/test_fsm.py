"""
آزمون‌های یکپارچگی ماشین وضعیت (FSM)، چرخه ثبت سفارش و رهگیری پرونده (bot/fsm.py و bot/dispatcher.py)
"""

import unittest
from core.config import Settings
from core.security import AccessControl
from core.throttling import Throttler
from core.database import DatabaseManager
from services.catalog import CatalogService
from services.orders import OrderService
from bot.models import TelegramUser, IncomingMessage, CallbackQuery
from bot.dispatcher import BotDispatcher
from bot.fsm import FSMManager


class TestFSMIntegration(unittest.TestCase):
    """مجموعه آزمون‌های چندمرحله‌ای ثبت درخواست و رهگیری پرونده."""

    def setUp(self):
        self.user_id = 987654321
        self.user = TelegramUser(
            id=self.user_id,
            first_name="محمد",
            last_name="کریمی",
            username="m_karimi"
        )

        self.settings = Settings(admin_id=123456789)
        self.access_control = AccessControl(self.settings)
        self.throttler = Throttler(rate_limit_seconds=0.0, max_burst=1000)  # غیرفعال‌سازی تاخیر برای تست‌های پرسرعت
        self.fsm_manager = FSMManager()

        self.db_manager = DatabaseManager("sqlite:///:memory:")
        self.db_manager.init_db()
        with self.db_manager.get_session() as session:
            CatalogService.seed_initial_catalog(session)

        self.dispatcher = BotDispatcher(
            access_control=self.access_control,
            throttler=self.throttler,
            db_manager=self.db_manager,
            fsm_manager=self.fsm_manager
        )

    def tearDown(self):
        self.db_manager.drop_db()

    def test_full_order_intake_flow_and_tracking(self):
        """
        سناریوی کامل:
        ۱. انتخاب خدمت تاییدیه تحصیلی
        ۲. کلیک روی ثبت درخواست
        ۳. ارسال کد ملی نامعتبر و مهار آن با پیام خطا
        ۴. ارسال کد ملی صحیح و پیشروی در فیلدها
        ۵. تایید نهایی و دریافت کد رهگیری یکتا
        ۶. استعلام کد رهگیری و مشاهده وضعیت پرونده
        """
        # گام ۱: کلیک روی شروع ثبت درخواست تاییدیه تحصیلی
        cb_start = CallbackQuery(
            id="cb_start",
            from_user=self.user,
            data="order_start_EMT_VERIFICATION"
        )
        resp1 = self.dispatcher.dispatch_callback(cb_start)
        self.assertIn("مرحله ۱ از", resp1.text)
        self.assertIn("کد ملی", resp1.text)
        self.assertEqual(self.fsm_manager.get_state(self.user_id).step, "FIELD_INPUT")

        # گام ۲: ارسال کد ملی نامعتبر (طول اشتباه)
        msg_invalid_nid = IncomingMessage(
            message_id=10,
            from_user=self.user,
            text="12345"
        )
        resp2 = self.dispatcher.dispatch(msg_invalid_nid)
        self.assertIn("خطای اعتبارسنجی", resp2.text)
        # هنوز باید در مرحله اول باشد
        self.assertEqual(self.fsm_manager.get_state(self.user_id).current_field_index, 0)

        # گام ۳: ارسال کد ملی معتبر (الگوریتمی)
        msg_valid_nid = IncomingMessage(
            message_id=11,
            from_user=self.user,
            text="0010350829"
        )
        resp3 = self.dispatcher.dispatch(msg_valid_nid)
        self.assertIn("مرحله 2 از", resp3.text)
        self.assertIn("مقطع تحصیلی", resp3.text)

        # گام ۴: ارسال فیلدهای باقیمانده
        # فیلد ۲: مقطع تحصیلی
        self.dispatcher.dispatch(IncomingMessage(message_id=12, from_user=self.user, text="کارشناسی"))
        # فیلد ۳: نام دانشگاه
        self.dispatcher.dispatch(IncomingMessage(message_id=13, from_user=self.user, text="دانشگاه تهران"))
        # فیلد ۴: سال فراغت
        self.dispatcher.dispatch(IncomingMessage(message_id=14, from_user=self.user, text="1402"))
        # فیلد ۵: سازمان مقصد
        resp_preview = self.dispatcher.dispatch(IncomingMessage(message_id=15, from_user=self.user, text="وزارت بهداشت"))

        # باید به پیش‌نمایش و مرحله CONFIRMATION برسد
        self.assertIn("پیش‌نمایش درخواست", resp_preview.text)
        self.assertTrue("0010350829" in resp_preview.text or "001****829" in resp_preview.text)
        self.assertIn("دانشگاه تهران", resp_preview.text)
        self.assertEqual(self.fsm_manager.get_state(self.user_id).step, "CONFIRMATION")

        # گام ۵: کلیک روی تایید نهایی درخواست
        cb_confirm = CallbackQuery(
            id="cb_conf",
            from_user=self.user,
            data="order_confirm"
        )
        resp_success = self.dispatcher.dispatch_callback(cb_confirm)
        self.assertIn("درخواست شما با موفقیت ثبت گردید", resp_success.text)
        self.assertIn("LIMO-1405-", resp_success.text)
        # وضعیت FSM باید پاک شده باشد
        self.assertIsNone(self.fsm_manager.get_state(self.user_id))

        # استخراج کد رهگیری از متن پاسخ
        import re
        match = re.search(r"LIMO-1405-\d{5}", resp_success.text)
        self.assertIsNotNone(match)
        tracking_code = match.group(0)

        # گام ۶: استعلام کد رهگیری از طریق منوی رهگیری
        cb_track = CallbackQuery(
            id="cb_track",
            from_user=self.user,
            data="order_tracking"
        )
        resp_prompt = self.dispatcher.dispatch_callback(cb_track)
        self.assertIn("کد رهگیری", resp_prompt.text)
        self.assertEqual(self.fsm_manager.get_state(self.user_id).step, "AWAITING_TRACKING_CODE")

        # ارسال کد رهگیری
        msg_code = IncomingMessage(
            message_id=20,
            from_user=self.user,
            text=tracking_code
        )
        resp_report = self.dispatcher.dispatch(msg_code)
        self.assertIn(tracking_code, resp_report.text)
        self.assertIn("در انتظار بررسی اپراتور", resp_report.text)
        self.assertIn("استعلام تاییدیه تحصیلی", resp_report.text)

    def test_order_cancellation_via_callback(self):
        """آزمون لغو فرآیند ثبت سفارش با دکمه انصراف."""
        cb_start = CallbackQuery(
            id="cb_s",
            from_user=self.user,
            data="order_start_EMT_VERIFICATION"
        )
        self.dispatcher.dispatch_callback(cb_start)
        self.assertIsNotNone(self.fsm_manager.get_state(self.user_id))

        # کلیک روی انصراف
        cb_cancel = CallbackQuery(
            id="cb_c",
            from_user=self.user,
            data="order_cancel"
        )
        resp = self.dispatcher.dispatch_callback(cb_cancel)
        self.assertIn("لغو گردید", resp.text)
        self.assertIsNone(self.fsm_manager.get_state(self.user_id))

    def test_order_cancellation_via_command(self):
        """آزمون لغو فرآیند با ارسال دستور متنی /cancel."""
        cb_start = CallbackQuery(
            id="cb_s2",
            from_user=self.user,
            data="order_start_SANJESH_REGISTRATION"
        )
        self.dispatcher.dispatch_callback(cb_start)
        self.assertIsNotNone(self.fsm_manager.get_state(self.user_id))

        # ارسال دستور /cancel
        resp = self.dispatcher.dispatch(IncomingMessage(message_id=30, from_user=self.user, text="/cancel"))
        self.assertIn("لغو گردید", resp.text)
        self.assertIsNone(self.fsm_manager.get_state(self.user_id))

    def test_direct_track_command(self):
        """آزمون دستور رهگیری مستقیم (/track <code?>)."""
        # ایجاد یک سفارش آزمایشی در دیتابیس
        with self.db_manager.get_session() as session:
            user = CatalogService.get_or_create_user(session, 987654321, "تست")
            svc = CatalogService.get_service_by_code(session, "EMT_VERIFICATION")
            order = OrderService.create_order(session, user.id, svc.id, {}, 987654321)
            code = order.tracking_code

        # ارسال دستور /track با کد
        resp = self.dispatcher.dispatch(IncomingMessage(message_id=40, from_user=self.user, text=f"/track {code}"))
        self.assertIn(code, resp.text)
        self.assertIn("در انتظار بررسی", resp.text)

        # ارسال دستور /track با کد نامعتبر
        resp_bad = self.dispatcher.dispatch(IncomingMessage(message_id=41, from_user=self.user, text="/track LIMO-0000-00000"))
        self.assertIn("یافت نشد", resp_bad.text)


if __name__ == "__main__":
    unittest.main()
