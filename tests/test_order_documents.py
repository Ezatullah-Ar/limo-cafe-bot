"""
آزمون‌های خودکار دریافت و ضمیمه‌سازی مدارک پیوست به پرونده‌ها (Order Document Handling)
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


class TestOrderDocuments(unittest.TestCase):
    """مجموعه آزمون‌های راستی‌آزمایی بارگذاری اسناد، مدارک هویتی و ثبت در دیتابیس."""

    def setUp(self):
        self.user_id = 99887766
        self.user = TelegramUser(id=self.user_id, first_name="متقاضی مدارک")

        self.settings = Settings(admin_id=123456)
        self.access_control = AccessControl(self.settings)
        self.throttler = Throttler(rate_limit_seconds=0.0, max_burst=1000)
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

    def test_document_upload_during_order_intake(self):
        """آزمون ارسال عکس/مدرک توسط متقاضی در خلال تکمیل سفارش و ذخیره نهایی در پرونده."""
        # گام ۱: کاربر فرآیند خدمت تاییدیه تحصیلی را آغاز می‌کند
        self.fsm_manager.start_order_flow(
            user_id=self.user_id,
            service_code="EMT_VERIFICATION",
            field_keys=["national_id"]
        )

        # گام ۲: ورود کدملی معتبر
        msg_nid = IncomingMessage(
            message_id=1,
            from_user=self.user,
            text="0010350829"
        )
        resp1 = self.dispatcher.dispatch(msg_nid)
        self.assertIn("پیش‌نمایش درخواست", resp1.text)

        state = self.fsm_manager.get_state(self.user_id)
        self.assertEqual(state.step, "CONFIRMATION")

        # گام ۳: کاربر تصویر دانشنامه را پیوست می‌کند
        msg_doc = IncomingMessage(
            message_id=2,
            from_user=self.user,
            file_id="telegram_file_diploma_xyz123",
            file_name="diploma_scan.pdf",
            file_type="DOCUMENT",
            file_size=204800
        )
        resp_upload = self.dispatcher.dispatch(msg_doc)
        self.assertIn("مدرک با موفقیت ضمیمه گردید", resp_upload.text)
        self.assertEqual(len(state.collected_docs), 1)

        # گام ۴: تایید نهایی سفارش توسط کاربر
        cb_confirm = CallbackQuery(
            id="cb_conf",
            from_user=self.user,
            data="order_confirm"
        )
        resp_conf = self.dispatcher.dispatch_callback(cb_confirm)
        self.assertIn("با موفقیت ثبت گردید", resp_conf.text)
        self.assertIsNone(self.fsm_manager.get_state(self.user_id))

        # بررسی ذخیره مدارک در پایگاه داده
        with self.db_manager.get_session() as session:
            orders = OrderService.get_user_orders(session, user_id=1)
            self.assertEqual(len(orders), 1)
            saved_order = orders[0]
            self.assertEqual(len(saved_order.documents), 1)
            doc = saved_order.documents[0]
            self.assertEqual(doc.file_id, "telegram_file_diploma_xyz123")
            self.assertEqual(doc.file_name, "diploma_scan.pdf")
            self.assertEqual(doc.file_type, "DOCUMENT")
            self.assertEqual(doc.file_size, 204800)


if __name__ == "__main__":
    unittest.main()
