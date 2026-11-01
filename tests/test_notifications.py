"""
آزمون‌های خودکار سرویس آگاه‌سازی مشتریان (Phase 9: Customer Notifications Engine)
"""

import unittest
from core.config import Settings
from core.security import AccessControl
from core.throttling import Throttler
from core.database import DatabaseManager
from services.catalog import CatalogService
from services.orders import OrderService
from services.notifications import NotificationService
from bot.models import TelegramUser, IncomingMessage, CallbackQuery
from bot.dispatcher import BotDispatcher
from bot.fsm import FSMManager


class TestNotifications(unittest.TestCase):
    """مجموعه آزمون‌های راستی‌آزمایی اعلان‌های تغییر وضعیت و اطلاع‌رسانی به مشتریان."""

    def setUp(self):
        self.admin_id = 123456789
        self.customer_id = 987654321

        self.admin_user = TelegramUser(id=self.admin_id, first_name="اپراتور")
        self.customer_user = TelegramUser(id=self.customer_id, first_name="متقاضی", username="customer_x")

        self.settings = Settings(admin_id=self.admin_id)
        self.access_control = AccessControl(self.settings)
        self.throttler = Throttler(rate_limit_seconds=0.0, max_burst=1000)
        self.fsm_manager = FSMManager()

        self.db_manager = DatabaseManager("sqlite:///:memory:")
        self.db_manager.init_db()

        with self.db_manager.get_session() as session:
            CatalogService.seed_initial_catalog(session)
            customer = CatalogService.get_or_create_user(session, self.customer_id, "متقاضی")
            svc = CatalogService.get_service_by_code(session, "EMT_VERIFICATION")
            self.test_order = OrderService.create_order(
                session=session,
                user_id=customer.id,
                service_id=svc.id,
                form_data={"national_id": "0010350829"},
                actor_telegram_id=self.customer_id
            )
            self.test_order_id = self.test_order.id
            self.test_tracking_code = self.test_order.tracking_code

        self.dispatcher = BotDispatcher(
            access_control=self.access_control,
            throttler=self.throttler,
            db_manager=self.db_manager,
            fsm_manager=self.fsm_manager
        )

    def tearDown(self):
        self.db_manager.drop_db()

    def test_create_customer_status_alert_texts(self):
        """آزمون تولید متن اعلان متناسب با هر وضعیت برای متقاضی."""
        with self.db_manager.get_session() as session:
            order = OrderService.get_order_by_id(session, self.test_order_id)

            # ۱. وضعیت APPROVED
            alert_appr = NotificationService.create_customer_status_alert(
                order, "APPROVED", note="مدارک بررسی و تایید شد."
            )
            self.assertEqual(alert_appr.chat_id, self.customer_id)
            self.assertIn("تاییدشده", alert_appr.text)
            self.assertIn(self.test_tracking_code, alert_appr.text)
            self.assertIn("مدارک بررسی و تایید شد", alert_appr.text)
            self.assertIn("در حال پیگیری است", alert_appr.text)

            # ۲. وضعیت NEED_INFO
            alert_ni = NotificationService.create_customer_status_alert(
                order, "NEED_INFO", note="عکس تار است."
            )
            self.assertIn("نقص مدارک", alert_ni.text)
            self.assertIn("اقدام فوری", alert_ni.text)
            self.assertIn("عکس تار است", alert_ni.text)

            # ۳. وضعیت COMPLETED
            alert_comp = NotificationService.create_customer_status_alert(
                order, "COMPLETED", note="کد صحت: 12345678"
            )
            self.assertIn("تکمیل‌شده", alert_comp.text)
            self.assertIn("تبریک", alert_comp.text)
            self.assertIn("کد صحت: 12345678", alert_comp.text)

            # ۴. وضعیت CANCELLED
            alert_canc = NotificationService.create_customer_status_alert(
                order, "CANCELLED", note="عدم تطابق اطلاعات هویتی"
            )
            self.assertIn("لغو شده", alert_canc.text)
            self.assertIn("عدم تطابق اطلاعات هویتی", alert_canc.text)

    def test_operator_approval_triggers_customer_notification(self):
        """آزمون ایجاد اعلان مشتری به محض تایید پرونده توسط اپراتور در کالبک."""
        cb = CallbackQuery(
            id="cb_appr",
            from_user=self.admin_user,
            data=f"op_setstatus_{self.test_order_id}_APPROVED"
        )
        resp = self.dispatcher.dispatch_callback(cb)

        # بررسی پاسخ به اپراتور
        self.assertIn("تاییدشده", resp.text)
        self.assertEqual(resp.callback_alert, "وضعیت پرونده به «تاییدشده» تغییر یافت.")

        # بررسی اعلان ضمیمه‌شده برای مشتری
        self.assertIsNotNone(resp.notification)
        self.assertEqual(resp.notification.chat_id, self.customer_id)
        self.assertIn(self.test_tracking_code, resp.notification.text)
        self.assertIn("تاییدشده", resp.notification.text)

    def test_operator_note_triggers_customer_notification(self):
        """آزمون ایجاد اعلان مشتری پس از ارسال توضیحات نقص مدرک توسط اپراتور."""
        # گام ۱: کلیک روی اعلام نقص
        cb_ni = CallbackQuery(
            id="cb_ni",
            from_user=self.admin_user,
            data=f"op_prompt_{self.test_order_id}_NEED_INFO"
        )
        self.dispatcher.dispatch_callback(cb_ni)

        # گام ۲: ارسال پیام نقص مدرک
        msg_note = IncomingMessage(
            message_id=99,
            from_user=self.admin_user,
            text="لطفاً اسکن اصل شناسنامه را ارسال فرمایید."
        )
        resp = self.dispatcher.dispatch(msg_note)

        self.assertIn("بروزرسانی شد", resp.text)
        self.assertIsNotNone(resp.notification)
        self.assertEqual(resp.notification.chat_id, self.customer_id)
        self.assertIn("لطفاً اسکن اصل شناسنامه را ارسال فرمایید", resp.notification.text)
        self.assertIn("نقص مدارک", resp.notification.text)


if __name__ == "__main__":
    unittest.main()
