"""
آزمون‌های خودکار کارتابل و پنل اپراتور (Phase 6: Operator Panel & Order Status Transitions)
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
from bot.handlers import ACCESS_DENIED_TEXT


class TestOperatorPanel(unittest.TestCase):
    """مجموعه آزمون‌های کارتابل اپراتور، بررسی مدارک و تغییر وضعیت پرونده‌ها."""

    def setUp(self):
        self.admin_id = 123456789
        self.regular_user_id = 987654321

        self.admin_user = TelegramUser(
            id=self.admin_id,
            first_name="مدیر و اپراتور",
            username="admin_operator"
        )
        self.regular_user = TelegramUser(
            id=self.regular_user_id,
            first_name="مشتری",
            username="customer_user"
        )

        self.settings = Settings(admin_id=self.admin_id)
        self.access_control = AccessControl(self.settings)
        self.throttler = Throttler(rate_limit_seconds=0.0, max_burst=1000)
        self.fsm_manager = FSMManager()

        self.db_manager = DatabaseManager("sqlite:///:memory:")
        self.db_manager.init_db()

        with self.db_manager.get_session() as session:
            CatalogService.seed_initial_catalog(session)
            # ایجاد یک مشتری نمونه
            customer = CatalogService.get_or_create_user(
                session=session,
                telegram_id=self.regular_user_id,
                full_name="علی رضایی",
                username="ali_rezaei"
            )
            svc = CatalogService.get_service_by_code(session, "EMT_VERIFICATION")
            # ایجاد یک سفارش آزمایشی با وضعیت اولیه PENDING
            self.test_order = OrderService.create_order(
                session=session,
                user_id=customer.id,
                service_id=svc.id,
                form_data={"national_id": "0010350829", "study_level": "کارشناسی"},
                actor_telegram_id=self.regular_user_id
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

    def test_admin_orders_list(self):
        """آزمون مشاهده کارتابل سفارش‌ها توسط اپراتور: نمایش لیست سفارشات در صف."""
        cb = CallbackQuery(
            id="cb_adm_ord",
            from_user=self.admin_user,
            data="admin_orders"
        )
        resp = self.dispatcher.dispatch_callback(cb)

        self.assertIn("کارتابل سفارشات اپراتور", resp.text)
        self.assertIn(self.test_tracking_code, resp.text)
        self.assertIsNotNone(resp.reply_markup)
        button_callbacks = [btn.callback_data for row in resp.reply_markup for btn in row]
        self.assertIn(f"op_view_{self.test_order_id}", button_callbacks)

    def test_operator_view_order_details(self):
        """آزمون مشاهده کارت تفصیلی یک پرونده توسط اپراتور و وجود دکمه‌های اقدام."""
        cb = CallbackQuery(
            id="cb_view",
            from_user=self.admin_user,
            data=f"op_view_{self.test_order_id}"
        )
        resp = self.dispatcher.dispatch_callback(cb)

        self.assertIn(self.test_tracking_code, resp.text)
        self.assertIn("علی رضایی", resp.text)
        self.assertIn("0010350829", resp.text)
        self.assertIn("در انتظار بررسی اپراتور", resp.text)

        button_callbacks = [btn.callback_data for row in resp.reply_markup for btn in row]
        self.assertIn(f"op_setstatus_{self.test_order_id}_APPROVED", button_callbacks)
        self.assertIn(f"op_prompt_{self.test_order_id}_NEED_INFO", button_callbacks)
        self.assertIn(f"op_prompt_{self.test_order_id}_COMPLETED", button_callbacks)
        self.assertIn(f"op_prompt_{self.test_order_id}_CANCELLED", button_callbacks)

    def test_operator_approve_order(self):
        """آزمون تایید مستقیم سفارش توسط اپراتور (تغییر وضعیت به APPROVED)."""
        cb = CallbackQuery(
            id="cb_appr",
            from_user=self.admin_user,
            data=f"op_setstatus_{self.test_order_id}_APPROVED"
        )
        resp = self.dispatcher.dispatch_callback(cb)

        self.assertIn("تاییدشده", resp.text)
        self.assertEqual(resp.callback_alert, "وضعیت پرونده به «تاییدشده» تغییر یافت.")

        # بررسی پایگاه داده
        with self.db_manager.get_session() as session:
            saved = OrderService.get_order_by_id(session, self.test_order_id)
            self.assertEqual(saved.status, "APPROVED")
            # بررسی لاگ حسابرسی
            self.assertEqual(saved.audit_logs[-1].to_status, "APPROVED")
            self.assertEqual(saved.audit_logs[-1].actor_id, self.admin_id)

    def test_operator_need_info_flow(self):
        """آزمون چرخه اعلام نقص مدرک توسط اپراتور با ثبت توضیحات در FSM."""
        # گام ۱: کلیک روی اعلام نقص مدرک
        cb = CallbackQuery(
            id="cb_ni",
            from_user=self.admin_user,
            data=f"op_prompt_{self.test_order_id}_NEED_INFO"
        )
        resp1 = self.dispatcher.dispatch_callback(cb)
        self.assertIn("ثبت یادداشت اپراتور", resp1.text)
        self.assertIn("نقص مدارک", resp1.text)

        state = self.fsm_manager.get_state(self.admin_id)
        self.assertIsNotNone(state)
        self.assertEqual(state.step, "OPERATOR_NOTE")
        self.assertEqual(state.order_id, self.test_order_id)
        self.assertEqual(state.target_status, "NEED_INFO")

        # گام ۲: اپراتور متن نقص را ارسال می‌کند
        msg_note = IncomingMessage(
            message_id=88,
            from_user=self.admin_user,
            text="تصویر ارسالی از گواهی موقت تار است؛ لطفاً اسکن خوانا ارسال نمایید."
        )
        resp2 = self.dispatcher.dispatch(msg_note)
        self.assertIn("بروزرسانی شد", resp2.text)
        self.assertIn("نقص مدارک", resp2.text)
        self.assertIn("تصویر ارسالی از گواهی موقت تار است", resp2.text)
        self.assertIsNone(self.fsm_manager.get_state(self.admin_id))

        # بررسی ثبت در دیتابیس
        with self.db_manager.get_session() as session:
            saved = OrderService.get_order_by_id(session, self.test_order_id)
            self.assertEqual(saved.status, "NEED_INFO")
            self.assertIn("تار است", saved.operator_notes)
            self.assertEqual(saved.audit_logs[-1].to_status, "NEED_INFO")

    def test_operator_complete_flow(self):
        """آزمون تکمیل پرونده توسط اپراتور."""
        # کلیک روی دکمه تکمیل
        cb = CallbackQuery(
            id="cb_comp",
            from_user=self.admin_user,
            data=f"op_prompt_{self.test_order_id}_COMPLETED"
        )
        self.dispatcher.dispatch_callback(cb)

        # ارسال یادداشت تکمیل
        msg_note = IncomingMessage(
            message_id=89,
            from_user=self.admin_user,
            text="تاییدیه تحصیلی صادر گردید و کد صحت رسمی ۲۰ رقمی دریافت شد."
        )
        resp = self.dispatcher.dispatch(msg_note)
        self.assertIn("تکمیل‌شده", resp.text)

        with self.db_manager.get_session() as session:
            saved = OrderService.get_order_by_id(session, self.test_order_id)
            self.assertEqual(saved.status, "COMPLETED")
            self.assertEqual(saved.audit_logs[-1].to_status, "COMPLETED")

    def test_operator_cancel_flow(self):
        """آزمون لغو پرونده با ذکر دلیل توسط اپراتور."""
        cb = CallbackQuery(
            id="cb_canc",
            from_user=self.admin_user,
            data=f"op_prompt_{self.test_order_id}_CANCELLED"
        )
        self.dispatcher.dispatch_callback(cb)

        # ارسال علت لغو
        msg_note = IncomingMessage(
            message_id=90,
            from_user=self.admin_user,
            text="مدرک ارسالی فاقد مهر آموزشگاه بود و متقاضی پاسخگو نبود."
        )
        resp = self.dispatcher.dispatch(msg_note)
        self.assertIn("لغو شده", resp.text)

        with self.db_manager.get_session() as session:
            saved = OrderService.get_order_by_id(session, self.test_order_id)
            self.assertEqual(saved.status, "CANCELLED")

    def test_unauthorized_user_blocked_from_all_operator_callbacks(self):
        """آزمون مسدودسازی قطعی کاربر عادی از کلیه اکشن‌های کارتابل اپراتور."""
        forbidden_callbacks = [
            "admin_orders",
            f"op_view_{self.test_order_id}",
            f"op_setstatus_{self.test_order_id}_APPROVED",
            f"op_prompt_{self.test_order_id}_NEED_INFO"
        ]

        for cb_data in forbidden_callbacks:
            intruder_query = CallbackQuery(
                id="cb_intruder",
                from_user=self.regular_user,
                data=cb_data
            )
            resp = self.dispatcher.dispatch_callback(intruder_query)
            self.assertEqual(resp.text, ACCESS_DENIED_TEXT)
            self.assertIn("خطای دسترسی", resp.callback_alert)


if __name__ == "__main__":
    unittest.main()
