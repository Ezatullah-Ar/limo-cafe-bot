"""
آزمون‌های یکپارچه دیسپچر و تیکتینگ پشتیبانی در پایگاه داده (tests/test_support_integration.py)
سامانه «کافی نت لیمو» - فاز ۳.
"""

import unittest
from core.config import Settings
from core.security import AccessControl
from core.throttling import Throttler
from core.database import DatabaseManager
from core.models import User, SupportThread, SupportMessage
from services.support import SupportService
from bot.models import TelegramUser, IncomingMessage, CallbackQuery
from bot.dispatcher import BotDispatcher


class TestSupportIntegration(unittest.TestCase):
    """آزمون‌های یکپارچه چت دوطرفه و تیکتینگ در دیسپچر."""

    def setUp(self):
        self.admin_id = 999888777
        self.customer_id = 111222333

        self.settings = Settings(admin_id=self.admin_id)
        self.access_control = AccessControl(self.settings)
        self.throttler = Throttler(rate_limit_seconds=0.0, max_burst=1000)

        self.db_manager = DatabaseManager("sqlite:///:memory:")
        self.db_manager.init_db()

        self.dispatcher = BotDispatcher(
            access_control=self.access_control,
            throttler=self.throttler,
            db_manager=self.db_manager
        )

        self.admin_user = TelegramUser(id=self.admin_id, first_name="مدیر پشتیبانی")
        self.customer_user = TelegramUser(id=self.customer_id, first_name="مشتری گرامی")

    def tearDown(self):
        self.db_manager.drop_db()

    def test_full_support_chat_database_flow(self):
        """آزمون کامل جریان ورود به چت، ثبت در دیتابیس، پاسخ اپراتور و خروج."""
        # ۱. مشتری دستور /chat را می‌فرستد
        msg_chat = IncomingMessage(
            message_id=1,
            from_user=self.customer_user,
            text="/chat"
        )
        resp1 = self.dispatcher.dispatch(msg_chat)
        self.assertIn("شما به سامانه گفتگوی مستقیم با پشتیبانی کافی‌نت لیمو متصل شدید", resp1.text)

        # ۲. مشتری پیام می‌فرستد
        msg_q = IncomingMessage(
            message_id=2,
            from_user=self.customer_user,
            text="سلام وقت بخیر، هزینه تاییدیه تحصیلی چقدر است؟"
        )
        resp2 = self.dispatcher.dispatch(msg_q)
        self.assertIn("پیام شما برای اپراتور ارسال شد", resp2.text)
        self.assertIsNotNone(resp2.notification)
        self.assertIn("تیکت #", resp2.notification.text)

        # بررسی پایگاه داده
        with self.db_manager.get_session() as session:
            user_rec = session.query(User).filter_by(telegram_id=self.customer_id).first()
            self.assertIsNotNone(user_rec)
            thread = session.query(SupportThread).filter_by(user_id=user_rec.id).first()
            self.assertIsNotNone(thread)
            self.assertEqual(thread.status, "PENDING_SUPPORT")
            self.assertEqual(len(thread.messages), 1)
            self.assertEqual(thread.messages[0].message_text, "سلام وقت بخیر، هزینه تاییدیه تحصیلی چقدر است؟")
            self.assertEqual(thread.messages[0].sender_role, "CUSTOMER")

        # ۳. مدیر پیام را ریپلای می‌کند
        reply_to_admin = IncomingMessage(
            message_id=10,
            from_user=self.admin_user,
            text=resp2.notification.text  # حاوی شناسه مشتری
        )
        msg_admin_reply = IncomingMessage(
            message_id=11,
            from_user=self.admin_user,
            text="سلام، استعلام تاییدیه تحصیلی در حال حاضر بدون کارمزد سامانه ثبت می‌شود.",
            reply_to_message=reply_to_admin
        )
        resp3 = self.dispatcher.dispatch(msg_admin_reply)
        self.assertIn("پیام شما با موفقیت برای متقاضی ارسال شد", resp3.text)

        # بررسی پایگاه داده پس از پاسخ اپراتور
        with self.db_manager.get_session() as session:
            thread = session.query(SupportThread).filter_by(user_id=user_rec.id).first()
            self.assertEqual(thread.status, "PENDING_CUSTOMER")
            self.assertEqual(len(thread.messages), 2)
            self.assertEqual(thread.messages[1].sender_role, "OPERATOR")
            self.assertTrue(thread.messages[0].is_read)

        # ۴. مشتری چت را می‌بندد (/endchat)
        msg_end = IncomingMessage(
            message_id=3,
            from_user=self.customer_user,
            text="/endchat"
        )
        resp4 = self.dispatcher.dispatch(msg_end)
        self.assertIn("گفتگوی شما با پشتیبانی به پایان رسید", resp4.text)

        # بررسی وضعیت CLOSED در پایگاه داده
        with self.db_manager.get_session() as session:
            thread = session.query(SupportThread).filter_by(user_id=user_rec.id).first()
            self.assertEqual(thread.status, "CLOSED")


if __name__ == "__main__":
    unittest.main()
