"""
آزمون‌های خودکار قابلیت‌های پیشرفته برگرفته از معماری باختر (tests/test_advanced_features.py)
سامانه «کافی نت لیمو».
راستی‌آزمایی پاسخ مستقیم مدیر به ریپلای، تحویل نهایی مدارک (/send)، استخراج فیش بانکی (OCR) و همگام‌سازی گوگل شیت.
"""

import unittest
import json
from unittest.mock import MagicMock
from core.config import Settings
from core.security import AccessControl
from core.throttling import Throttler
from core.database import DatabaseManager
from services.catalog import CatalogService
from services.orders import OrderService
from services.ocr import normalize_digits, extract_receipt_data, perform_ocr_space
from services.sheets_sync import GoogleSheetsSyncService
from bot.models import TelegramUser, IncomingMessage, OutgoingResponse
from bot.dispatcher import BotDispatcher


class TestAdvancedFeatures(unittest.TestCase):
    """مجموعه آزمون‌های قابلیت‌های ارتقایافته سامانه."""

    def setUp(self):
        self.admin_id = 999111222
        self.customer_id = 888333444

        self.settings = Settings(admin_id=self.admin_id, google_sheet_url="https://script.google.com/macros/s/mock/exec")
        self.access_control = AccessControl(self.settings)
        self.throttler = Throttler(rate_limit_seconds=0.0, max_burst=1000)

        self.db_manager = DatabaseManager("sqlite:///:memory:")
        self.db_manager.init_db()

        with self.db_manager.get_session() as session:
            CatalogService.seed_initial_catalog(session)

        self.dispatcher = BotDispatcher(
            access_control=self.access_control,
            throttler=self.throttler,
            db_manager=self.db_manager
        )

        self.admin_user = TelegramUser(id=self.admin_id, first_name="مدیر سیستم")
        self.customer_user = TelegramUser(id=self.customer_id, first_name="مشتری تستی")

    def tearDown(self):
        self.db_manager.drop_db()

    def test_ocr_digit_normalization(self):
        """آزمون تبدیل کامل اعداد فارسی و عربی فیش‌های بانکی به انگلیسی."""
        persian_str = "مبلغ ۱۲۵۰۰۰۰ ریال در تاریخ ۱۴۰۵/۰۸/۰۵ ساعت ۱۸:۳۰"
        normalized = normalize_digits(persian_str)
        self.assertIn("1250000", normalized)
        self.assertIn("1405/08/05", normalized)
        self.assertIn("18:30", normalized)

    def test_receipt_data_extraction_standard_card(self):
        """آزمون استخراج کارت ۱۶ رقمی، تاریخ، زمان و مبلغ از متن رسید."""
        receipt_text = (
            "انتقال وجه کارت به کارت شتابی\n"
            "کارت مقصد: ۶۰۳۷-۹۹۷۹-۱۲۳۴-۵۶۷۸\n"
            "مبلغ: ۵۰۰,۰۰۰ ریال\n"
            "شماره پیگیری: ۸۸۹۹۰۱\n"
            "تاریخ: ۱۴۰۵/۰۸/۰۵ ساعت ۱۵:۴۵"
        )
        parsed = extract_receipt_data(receipt_text)
        self.assertEqual(parsed["card_number"], "6037997912345678")
        self.assertEqual(parsed["amount"], "500,000")
        self.assertEqual(parsed["trace_number"], "889901")
        self.assertEqual(parsed["date"], "1405/08/05")
        self.assertEqual(parsed["time"], "15:45")

    def test_receipt_data_extraction_masked_mobile_bank_card(self):
        """آزمون استخراج کارت‌های ستاره‌دار در خروجی همراه بانک‌ها."""
        masked_text = "واریز به ۶۰۳۷-****-****-۴۴۵۵ به مبلغ ۱,۲۵۰,۰۰۰ تومان کد رهگیری TR9871"
        parsed = extract_receipt_data(masked_text)
        self.assertIsNotNone(parsed["card_number"])
        self.assertIn("4455", parsed["card_number"])
        self.assertEqual(parsed["amount"], "1,250,000")
        self.assertEqual(parsed["trace_number"], "TR9871")

    def test_ocr_space_mock_request(self):
        """آزمون ارتباط و استخراج از OCR.space با ماک کردن پاسخ HTTP."""
        mock_opener = MagicMock()
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "IsErroredOnProcessing": False,
            "ParsedResults": [
                {"ParsedText": "انتقال وجه موفق\nکارت ۶۰۳۷۹۹۷۹۱۲۳۴۵۶۷۸\nمبلغ ۷۵۰,۰۰۰ ریال"}
            ]
        }).encode("utf-8")
        mock_opener.open.return_value.__enter__.return_value = mock_resp

        res = perform_ocr_space("https://example.com/receipt.jpg", opener=mock_opener)
        self.assertTrue(res["ok"])
        self.assertEqual(res["parsed"]["card_number"], "6037997912345678")
        self.assertEqual(res["parsed"]["amount"], "750,000")

    def test_google_sheets_sync_service_mocked(self):
        """آزمون ارسال موفق مشخصات سفارش به وب‌هوک گوگل شیت."""
        mock_opener = MagicMock()
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"status": "success", "tracking_code": "LIMO-1405-99"}).encode("utf-8")
        mock_opener.open.return_value.__enter__.return_value = mock_resp

        with self.db_manager.get_session() as session:
            user = CatalogService.get_or_create_user(session, telegram_id=123, full_name="تستر شیت")
            svc = CatalogService.get_service_by_code(session, "EMT_VERIFICATION")
            order = OrderService.create_order(
                session=session,
                user_id=user.id,
                service_id=svc.id,
                form_data={"field": "val"},
                actor_telegram_id=123
            )

            res = GoogleSheetsSyncService.sync_order(
                order=order,
                sheet_url="https://script.google.com/macros/s/mock/exec",
                opener=mock_opener
            )
            self.assertEqual(res["status"], "success")

    def test_admin_direct_reply_to_customer(self):
        """آزمون ریپلای مستقیم مدیر روی پیام حاوی شناسه مشتری و ارسال خودکار به چت متقاضی."""
        # پیامی که قبلاً بات برای مدیر فرستاده بوده است
        bot_alert = IncomingMessage(
            message_id=50,
            from_user=TelegramUser(id=999, first_name="بات لیمو"),
            text="📩 پرونده جدید دریافت شد.\nمتقاضی: علی رضایی (شناسه: <code>888333444</code>)"
        )

        # مدیر روی این پیام ریپلای می‌کند
        admin_reply = IncomingMessage(
            message_id=51,
            from_user=self.admin_user,
            text="سلام، مدارک شما دریافت شد و کار پرونده در حال پیگیری است.",
            reply_to_message=bot_alert
        )

        resp = self.dispatcher.dispatch(admin_reply)
        self.assertIn("با موفقیت برای متقاضی ارسال شد", resp.text)
        self.assertIsNotNone(resp.notification)
        self.assertEqual(resp.notification.chat_id, self.customer_id)
        self.assertIn("پیام پشتیبانی کافی نت لیمو", resp.notification.text)
        self.assertIn("مدارک شما دریافت شد", resp.notification.text)

    def test_admin_send_command_completes_order_and_notifies_customer(self):
        """آزمون دستور /send <tracking_code> برای تحویل نهایی مدارک و تکمیل سفارش."""
        with self.db_manager.get_session() as session:
            user = CatalogService.get_or_create_user(session, telegram_id=self.customer_id, full_name="مشتری")
            svc = CatalogService.get_service_by_code(session, "EMT_VERIFICATION")
            order = OrderService.create_order(
                session=session,
                user_id=user.id,
                service_id=svc.id,
                form_data={},
                actor_telegram_id=self.customer_id
            )
            t_code = order.tracking_code

        # مدیر دستور ارسال فایل نهایی را صادر می‌کند
        msg_send = IncomingMessage(
            message_id=60,
            from_user=self.admin_user,
            text=f"/send {t_code} تاییدیه تحصیلی و کد صحت شما با موفقیت صادر گردید."
        )

        resp = self.dispatcher.dispatch(msg_send)
        self.assertIn("با موفقیت برای متقاضی ارسال", resp.text)
        self.assertIn("تکمیل‌شده", resp.text)
        self.assertIsNotNone(resp.notification)
        self.assertEqual(resp.notification.chat_id, self.customer_id)
        self.assertIn(t_code, resp.notification.text)
        self.assertIn("پرونده شما تکمیل و نهایی شد", resp.notification.text)

        # بررسی به‌روزرسانی وضعیت در پایگاه داده به COMPLETED
        with self.db_manager.get_session() as session:
            updated_order = OrderService.get_order_by_tracking_code(session, t_code)
            self.assertEqual(updated_order.status, "COMPLETED")

    def test_support_chat_lifecycle_customer_to_admin(self):
        """آزمون چرخه کامل گفتگوی زنده دوطرفه: ورود به چت، ارسال پیام به ادمین، پاسخ ادمین و خروج."""
        # ۱. مشتری دستور /chat را می‌زند
        msg_chat = IncomingMessage(
            message_id=70,
            from_user=self.customer_user,
            text="/chat"
        )
        resp1 = self.dispatcher.dispatch(msg_chat)
        self.assertIn("سامانه گفتگوی مستقیم", resp1.text)
        state = self.dispatcher.fsm_manager.get_state(self.customer_id)
        self.assertIsNotNone(state)
        self.assertEqual(state.step, "IN_SUPPORT_CHAT")

        # ۲. مشتری پیام می‌فرستد
        msg_question = IncomingMessage(
            message_id=71,
            from_user=self.customer_user,
            text="سلام سوالی درباره تاییدیه تحصیلی داشتم"
        )
        resp2 = self.dispatcher.dispatch(msg_question)
        self.assertIn("پیام شما برای اپراتور ارسال شد", resp2.text)
        self.assertIsNotNone(resp2.notification)
        self.assertEqual(resp2.notification.chat_id, self.admin_id)
        self.assertIn(str(self.customer_id), resp2.notification.text)
        self.assertIn("سلام سوالی درباره تاییدیه تحصیلی داشتم", resp2.notification.text)

        # ۳. مدیر پیام را ریپلای می‌کند
        reply_to_admin = IncomingMessage(
            message_id=100,
            from_user=self.admin_user,
            text=resp2.notification.text  # حاوی شناسه مشتری
        )
        msg_admin_reply = IncomingMessage(
            message_id=101,
            from_user=self.admin_user,
            text="سلام، مدارک شما در حال استعلام است و تا فردا آماده می‌شود.",
            reply_to_message=reply_to_admin
        )
        resp_admin = self.dispatcher.dispatch(msg_admin_reply)
        self.assertIn("با موفقیت برای متقاضی ارسال شد", resp_admin.text)
        self.assertIsNotNone(resp_admin.notification)
        self.assertEqual(resp_admin.notification.chat_id, self.customer_id)
        self.assertIn("سلام، مدارک شما در حال استعلام است", resp_admin.notification.text)

        # ۴. مشتری چت را با /endchat به پایان می‌رساند
        msg_end = IncomingMessage(
            message_id=72,
            from_user=self.customer_user,
            text="/endchat"
        )
        resp_end = self.dispatcher.dispatch(msg_end)
        self.assertIn("گفتگوی شما با پشتیبانی به پایان رسید", resp_end.text)
        self.assertIsNone(self.dispatcher.fsm_manager.get_state(self.customer_id))

    def test_support_chat_exit_callback(self):
        """آزمون خروج از چت دوطرفه با کالبک دکمه شیشه‌ای exit_chat."""
        from bot.models import CallbackQuery
        self.dispatcher.fsm_manager.start_chat_flow(self.customer_id)
        self.assertIsNotNone(self.dispatcher.fsm_manager.get_state(self.customer_id))

        cb = CallbackQuery(
            id="cb_exit",
            from_user=self.customer_user,
            data="exit_chat"
        )
        resp = self.dispatcher.dispatch_callback(cb)
        self.assertIn("گفتگوی شما با پشتیبانی به پایان رسید", resp.text)
        self.assertIsNone(self.dispatcher.fsm_manager.get_state(self.customer_id))


if __name__ == "__main__":
    unittest.main()
