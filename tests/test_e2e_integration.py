"""
آزمون‌های جامع یکپارچگی سرتاسری (End-to-End System Integration Tests)
سامانه ربات تلگرام و پایش هوشمند «کافی نت لیمو».
تمام مراحل چرخه حیات مشتری، اپراتور، امنیت، ابزارهای وب‌هوک و عیب‌یابی سامانه را راستی‌آزمایی می‌کند.
"""

import unittest
import io
import json
from unittest.mock import MagicMock
from core.config import Settings
from core.security import AccessControl
from core.throttling import Throttler
from core.database import DatabaseManager
from core.models import OrderDocument
from services.catalog import CatalogService
from services.orders import OrderService
from services.monitor import MonitorService
from bot.models import TelegramUser, IncomingMessage, CallbackQuery
from bot.dispatcher import BotDispatcher
from bot.handlers import ACCESS_DENIED_TEXT, WELCOME_TEXT
from scripts.setup_webhook import (
    get_me,
    get_webhook_info,
    set_webhook,
    delete_webhook,
    mask_token
)


class TestE2ESystemIntegration(unittest.TestCase):
    """مجموعه آزمون‌های سرتاسری جریان کار مشتری و اپراتور."""

    def setUp(self):
        self.admin_id = 999888777
        self.customer_id = 111222333
        self.attacker_id = 444555666

        self.settings = Settings(admin_id=self.admin_id)
        self.access_control = AccessControl(self.settings)
        self.throttler = Throttler(rate_limit_seconds=0.0, max_burst=1000)

        # دیتابیس در حافظه
        self.db_manager = DatabaseManager("sqlite:///:memory:")
        self.db_manager.init_db()

        with self.db_manager.get_session() as session:
            CatalogService.seed_initial_catalog(session)

        self.dispatcher = BotDispatcher(
            access_control=self.access_control,
            throttler=self.throttler,
            db_manager=self.db_manager
        )

        self.customer_user = TelegramUser(
            id=self.customer_id,
            first_name="مشتری",
            last_name="تستی",
            username="test_customer"
        )
        self.admin_user = TelegramUser(
            id=self.admin_id,
            first_name="مدیر",
            last_name="لیمو",
            username="admin_limo"
        )
        self.attacker_user = TelegramUser(
            id=self.attacker_id,
            first_name="نفوذگر",
            last_name="ناشناس",
            username="attacker"
        )

    def tearDown(self):
        self.db_manager.drop_db()

    def test_customer_full_order_and_tracking_lifecycle(self):
        """
        سناریوی ۱: چرخه کامل مشتری از /start تا ثبت سفارش، بارگذاری مدرک،
        دریافت کد رهگیری و استعلام وضعیت پرونده.
        """
        # ۱.۱. ارسال /start
        msg_start = IncomingMessage(message_id=1, from_user=self.customer_user, text="/start")
        res_start = self.dispatcher.dispatch(msg_start)
        self.assertEqual(res_start.text, WELCOME_TEXT)

        # ۱.۲. انتخاب کاتالوگ خدمات (services_list)
        cb_cat = CallbackQuery(
            id="cb_1",
            from_user=self.customer_user,
            data="services_list",
            message=msg_start
        )
        res_cat = self.dispatcher.dispatch_callback(cb_cat)
        self.assertIn("فهرست خدمات فعال کافی نت لیمو", res_cat.text)

        # ۱.۳. انتخاب خدمت تاییدیه تحصیلی (svc_EMT_VERIFICATION)
        cb_srv = CallbackQuery(
            id="cb_2",
            from_user=self.customer_user,
            data="svc_EMT_VERIFICATION",
            message=msg_start
        )
        res_srv = self.dispatcher.dispatch_callback(cb_srv)
        self.assertIn("استعلام تاییدیه تحصیلی", res_srv.text)

        # ۱.۴. آغاز فرآیند ثبت درخواست (order_start_EMT_VERIFICATION)
        cb_ord_start = CallbackQuery(
            id="cb_3",
            from_user=self.customer_user,
            data="order_start_EMT_VERIFICATION",
            message=msg_start
        )
        res_f1 = self.dispatcher.dispatch_callback(cb_ord_start)
        self.assertIn("کد ملی", res_f1.text)

        # ۱.۵. وارد کردن فیلدها مرحله به مرحله (FSM)
        # کد ملی معتبر الگوریتمی
        msg_f1 = IncomingMessage(message_id=2, from_user=self.customer_user, text="0010350829")
        res_f2 = self.dispatcher.dispatch(msg_f1)
        self.assertIn("مرحله 2 از", res_f2.text)

        # مقطع تحصیلی
        msg_f2 = IncomingMessage(message_id=3, from_user=self.customer_user, text="کارشناسی")
        res_f3 = self.dispatcher.dispatch(msg_f2)
        self.assertIn("مرحله 3 از", res_f3.text)

        # نام دانشگاه
        msg_f3 = IncomingMessage(message_id=4, from_user=self.customer_user, text="دانشگاه تهران")
        res_f4 = self.dispatcher.dispatch(msg_f3)
        self.assertIn("مرحله 4 از", res_f4.text)

        # سال فراغت
        msg_f4 = IncomingMessage(message_id=5, from_user=self.customer_user, text="1402")
        res_f5 = self.dispatcher.dispatch(msg_f4)
        self.assertIn("مرحله 5 از", res_f5.text)

        # سازمان مقصد
        msg_f5 = IncomingMessage(message_id=6, from_user=self.customer_user, text="وزارت علوم")
        res_confirm_prompt = self.dispatcher.dispatch(msg_f5)
        self.assertIn("پیش‌نمایش درخواست", res_confirm_prompt.text)

        # ۱.۶. بارگذاری مدرک پیوست (فاز ۹)
        msg_doc = IncomingMessage(
            message_id=7,
            from_user=self.customer_user,
            file_id="tg_doc_diploma_999",
            file_name="diploma_scan.pdf",
            file_type="DOCUMENT",
            file_size=204800
        )
        res_doc = self.dispatcher.dispatch(msg_doc)
        self.assertIn("مدرک با موفقیت ضمیمه گردید", res_doc.text)
        self.assertIn("1 مدرک پیوست شد", res_doc.text)

        # ۱.۷. تأیید نهایی و ثبت سفارش (order_confirm)
        cb_confirm = CallbackQuery(
            id="cb_4",
            from_user=self.customer_user,
            data="order_confirm",
            message=msg_f5
        )
        res_order_saved = self.dispatcher.dispatch_callback(cb_confirm)
        self.assertIn("درخواست شما با موفقیت ثبت گردید", res_order_saved.text)
        self.assertIn("LIMO-", res_order_saved.text)

        # استخراج کد رهگیری از متن پاسخ
        import re
        match = re.search(r"LIMO-\d+-\d+", res_order_saved.text)
        self.assertIsNotNone(match)
        tracking_code = match.group(0)

        # ۱.۸. استعلام کد رهگیری توسط مشتری با دستور مستقیم /track
        msg_track = IncomingMessage(message_id=8, from_user=self.customer_user, text=f"/track {tracking_code}")
        res_track = self.dispatcher.dispatch(msg_track)
        self.assertIn(tracking_code, res_track.text)
        self.assertIn("در انتظار بررسی اپراتور", res_track.text)
        self.assertIn("1 مدرک", res_track.text)

    def test_operator_cartable_and_approval_workflow(self):
        """
        سناریوی ۲: ورود اپراتور به کارتابل سفارش‌ها (/orders)، بررسی پرونده،
        مشاهده مدارک پیوست، تغییر وضعیت به APPROVED و صدور اعلان مشتری.
        """
        # ایجاد یک سفارش نمونه با مدرک
        with self.db_manager.get_session() as session:
            user = CatalogService.get_or_create_user(
                session=session,
                telegram_id=self.customer_id,
                full_name="مشتری آزمون",
                username="customer_test"
            )
            svc = CatalogService.get_service_by_code(session, "EMT_VERIFICATION")
            order = OrderService.create_order(
                session=session,
                user_id=user.id,
                service_id=svc.id,
                form_data={"national_id": "1234567890", "phone_number": "09121112233"},
                actor_telegram_id=self.customer_id
            )
            order_id = order.id
            tracking_code = order.tracking_code

            # افزودن مدرک پیوست
            doc = OrderDocument(
                order_id=order_id,
                file_id="doc_id_sample_88",
                file_name="govahi_moaghat.jpg",
                file_type="PHOTO",
                file_size=512000
            )
            session.add(doc)
            session.commit()

        # ۲.۱. فراخوانی دستور مستقیم /orders توسط مدیر
        msg_orders = IncomingMessage(message_id=10, from_user=self.admin_user, text="/orders")
        res_orders = self.dispatcher.dispatch(msg_orders)
        self.assertIn("کارتابل سفارشات اپراتور", res_orders.text)
        self.assertIn(tracking_code, res_orders.text)

        # ۲.۲. کلیک روی پرونده جهت مشاهده جزئیات (op_view_<id>)
        cb_view = CallbackQuery(
            id="cb_v1",
            from_user=self.admin_user,
            data=f"op_view_{order_id}",
            message=msg_orders
        )
        res_view = self.dispatcher.dispatch_callback(cb_view)
        self.assertIn(tracking_code, res_view.text)
        self.assertIn("govahi_moaghat.jpg", res_view.text)
        self.assertIn("1 مدرک", res_view.text)

        # ۲.۳. تغییر وضعیت پرونده به تاییدشده (op_setstatus_<id>_APPROVED)
        cb_approve = CallbackQuery(
            id="cb_v2",
            from_user=self.admin_user,
            data=f"op_setstatus_{order_id}_APPROVED",
            message=msg_orders
        )
        res_approved = self.dispatcher.dispatch_callback(cb_approve)
        self.assertIn("تاییدشده", res_approved.text)
        self.assertIsNotNone(res_approved.notification)
        self.assertEqual(res_approved.notification.chat_id, self.customer_id)
        self.assertIn(tracking_code, res_approved.notification.text)
        self.assertIn("تایید گردید", res_approved.notification.text)

    def test_operator_direct_commands_stats_health_backup(self):
        """
        سناریوی ۳: ارزیابی دستورات مدیریتی /stats، /health و /backup.
        """
        # ۳.۱. دستور /stats
        msg_stats = IncomingMessage(message_id=20, from_user=self.admin_user, text="/stats")
        res_stats = self.dispatcher.dispatch(msg_stats)
        self.assertIn("آمار و وضعیت عمومی سامانه", res_stats.text)
        self.assertIn("خدمات فعال", res_stats.text)

        # ۳.۲. دستور /health
        msg_health = IncomingMessage(message_id=21, from_user=self.admin_user, text="/health")
        res_health = self.dispatcher.dispatch(msg_health)
        self.assertIn("گزارش سلامت و عیب‌یابی سامانه", res_health.text)
        self.assertIn("HEALTHY", res_health.text)
        self.assertIn("یکپارچگی پایگاه داده", res_health.text)

        # ۳.۳. دستور /backup
        msg_backup = IncomingMessage(message_id=22, from_user=self.admin_user, text="/backup")
        res_backup = self.dispatcher.dispatch(msg_backup)
        self.assertIn("گزارش تهیه نسخه پشتیبان", res_backup.text)
        self.assertIn("محتویات اسنپ‌شات امن", res_backup.text)

    def test_security_default_deny_for_all_admin_features(self):
        """
        سناریوی ۴: تضمین اصل پیش‌فرض انسداد (Default-Deny) در برابر کاربران غیرمجاز.
        """
        # ۴.۱. دستورات متنی غیرمجاز
        for cmd in ("/admin", "/orders", "/stats", "/health", "/backup"):
            msg = IncomingMessage(message_id=30, from_user=self.attacker_user, text=cmd)
            res = self.dispatcher.dispatch(msg)
            self.assertEqual(res.text, ACCESS_DENIED_TEXT)

        # ۴.۲. کالبک‌های دکمه‌های شیشه‌ای غیرمجاز
        for cb_data in ("admin_stats", "admin_orders", "admin_monitors", "op_view_1", "op_setstatus_1_APPROVED"):
            cb = CallbackQuery(
                id="cb_atk",
                from_user=self.attacker_user,
                data=cb_data,
                message=IncomingMessage(message_id=31, from_user=self.attacker_user, text="")
            )
            res = self.dispatcher.dispatch_callback(cb)
            self.assertEqual(res.text, ACCESS_DENIED_TEXT)
            self.assertIn("خطای دسترسی", res.callback_alert or "")

    def test_webhook_setup_script_mocked(self):
        """
        سناریوی ۵: راستی‌آزمایی اسکریپت setup_webhook با ماک کردن متدهای HTTP تلگرام.
        """
        # تست ماسک کردن توکن
        masked = mask_token("1234567890:ABCdefGhI-JKlmNoPqR")
        self.assertTrue(masked.startswith("123456"))
        self.assertTrue(masked.endswith("PqR"))
        self.assertNotIn("ABCdefGhI-JK", masked)

        # ماک Opener
        mock_opener = MagicMock()

        # تست get_me
        mock_resp_me = MagicMock()
        mock_resp_me.read.return_value = json.dumps({
            "ok": True,
            "result": {"id": 12345, "is_bot": True, "first_name": "کافی نت لیمو", "username": "LimoCafeBot"}
        }).encode("utf-8")
        mock_opener.open.return_value.__enter__.return_value = mock_resp_me

        me_info = get_me(bot_token="test_token_12345", opener=mock_opener)
        self.assertTrue(me_info["ok"])
        self.assertEqual(me_info["result"]["username"], "LimoCafeBot")

        # تست get_webhook_info
        mock_resp_info = MagicMock()
        mock_resp_info.read.return_value = json.dumps({
            "ok": True,
            "result": {"url": "https://limo-cafe-bot.workers.dev", "pending_update_count": 0}
        }).encode("utf-8")
        mock_opener.open.return_value.__enter__.return_value = mock_resp_info

        wh_info = get_webhook_info(bot_token="test_token_12345", opener=mock_opener)
        self.assertTrue(wh_info["ok"])
        self.assertEqual(wh_info["result"]["url"], "https://limo-cafe-bot.workers.dev")

        # تست set_webhook
        mock_resp_set = MagicMock()
        mock_resp_set.read.return_value = json.dumps({
            "ok": True,
            "result": True,
            "description": "Webhook was set"
        }).encode("utf-8")
        mock_opener.open.return_value.__enter__.return_value = mock_resp_set

        set_res = set_webhook(
            url="https://limo-cafe-bot.workers.dev",
            secret_token="secret_key_99",
            bot_token="test_token_12345",
            opener=mock_opener
        )
        self.assertTrue(set_res["ok"])

        # تست delete_webhook
        mock_resp_del = MagicMock()
        mock_resp_del.read.return_value = json.dumps({
            "ok": True,
            "result": True,
            "description": "Webhook was deleted"
        }).encode("utf-8")
        mock_opener.open.return_value.__enter__.return_value = mock_resp_del

        del_res = delete_webhook(bot_token="test_token_12345", opener=mock_opener)
        self.assertTrue(del_res["ok"])


if __name__ == "__main__":
    unittest.main()
