"""
آزمون‌های خودکار سیستم جامع گفتگوی زنده مشتری و پشتیبانی (tests/test_support_service.py)
سامانه «کافی نت لیمو» - فاز ۳.
پوشش چرخه‌حیات تیکت‌ها، ارسال پیام متقاضی، پاسخ اپراتور، انتساب مسئول، بستن و بازگشایی تیکت.
"""

import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.database import Base
from core.models import User, Order, SupportThread, SupportMessage
from services.support import SupportService


class TestSupportService(unittest.TestCase):
    """مجموعه آزمون‌های سرویس تیکتینگ و گفتگوی پشتیبانی."""

    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # کاربر متقاضی و اپراتور
        self.customer = User(telegram_id=111222333, full_name="مشتری تستی چت", username="cust_chat")
        self.operator = User(telegram_id=999888777, full_name="اپراتور پشتیبانی", role="OPERATOR")
        self.session.add_all([self.customer, self.operator])
        self.session.commit()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_get_or_create_thread(self):
        """آزمون دریافت یا ایجاد رشته گفتگوی فعال."""
        thread1 = SupportService.get_or_create_active_thread(self.session, self.customer.id)
        self.assertIsNotNone(thread1.id)
        self.assertEqual(thread1.status, "NEW")

        # فراخوانی مجدد باید همان تیکت باز را بازگرداند
        thread2 = SupportService.get_or_create_active_thread(self.session, self.customer.id)
        self.assertEqual(thread1.id, thread2.id)

    def test_customer_and_operator_message_flow(self):
        """آزمون جریان پیام مشتری و پاسخ اپراتور با تغییر وضعیت تیکت."""
        thread = SupportService.get_or_create_active_thread(self.session, self.customer.id)

        # ۱. مشتری پیام ارسال می‌کند
        msg_c = SupportService.add_customer_message(
            session=self.session,
            thread_id=thread.id,
            sender_telegram_id=self.customer.telegram_id,
            message_text="سلام، وقت بخیر. مدارک را بارگذاری کردم."
        )
        self.assertEqual(msg_c.sender_role, "CUSTOMER")
        self.assertFalse(msg_c.is_read)
        self.assertEqual(thread.status, "PENDING_SUPPORT")

        # ۲. اپراتور پاسخ می‌دهد
        msg_o = SupportService.add_operator_message(
            session=self.session,
            thread_id=thread.id,
            operator_telegram_id=self.operator.telegram_id,
            message_text="سلام. مدارک شما دریافت شد و در دست بررسی است."
        )
        self.assertEqual(msg_o.sender_role, "OPERATOR")
        self.assertEqual(thread.status, "PENDING_CUSTOMER")
        self.assertEqual(thread.assigned_operator_id, self.operator.telegram_id)

        # پیام مشتری باید خوانده‌شده علامت بخورد
        self.session.refresh(msg_c)
        self.assertTrue(msg_c.is_read)

        # بررسی لیست پیام‌های گفتگو
        messages = SupportService.get_thread_messages(self.session, thread.id)
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].message_text, "سلام، وقت بخیر. مدارک را بارگذاری کردم.")
        self.assertEqual(messages[1].message_text, "سلام. مدارک شما دریافت شد و در دست بررسی است.")

    def test_close_and_reopen_thread(self):
        """آزمون بستن تیکت و بازگشایی مجدد آن با پیام جدید مشتری."""
        thread = SupportService.get_or_create_active_thread(self.session, self.customer.id)
        SupportService.close_thread(self.session, thread.id, actor_id=self.operator.telegram_id)
        self.assertEqual(thread.status, "CLOSED")

        # بازگشایی صریح
        SupportService.reopen_thread(self.session, thread.id)
        self.assertEqual(thread.status, "PENDING_SUPPORT")

        # یا بستن و ارسال پیام جدید که خودکار وضعیت را به PENDING_SUPPORT برمی‌گرداند
        SupportService.close_thread(self.session, thread.id)
        SupportService.add_customer_message(
            session=self.session,
            thread_id=thread.id,
            sender_telegram_id=self.customer.telegram_id,
            message_text="سوالی جدید پیش آمده است."
        )
        self.assertEqual(thread.status, "PENDING_SUPPORT")

    def test_assign_operator(self):
        """آزمون تخصیص اپراتور به تیکت."""
        thread = SupportService.get_or_create_active_thread(self.session, self.customer.id)
        SupportService.assign_operator(self.session, thread.id, self.operator.telegram_id)
        self.assertEqual(thread.assigned_operator_id, self.operator.telegram_id)

    def test_user_threads_isolation(self):
        """آزمون ایزولاسیون و عدم دسترسی به تیکت‌های سایر کاربران."""
        user2 = User(telegram_id=444555666, full_name="مشتری دوم")
        self.session.add(user2)
        self.session.commit()

        t1 = SupportService.get_or_create_active_thread(self.session, self.customer.id)
        t2 = SupportService.get_or_create_active_thread(self.session, user2.id)

        cust1_threads = SupportService.get_user_threads(self.session, self.customer.id)
        self.assertEqual(len(cust1_threads), 1)
        self.assertEqual(cust1_threads[0].id, t1.id)

        cust2_threads = SupportService.get_user_threads(self.session, user2.id)
        self.assertEqual(len(cust2_threads), 1)
        self.assertEqual(cust2_threads[0].id, t2.id)

    def test_get_all_threads_filter(self):
        """آزمون فیلتر تیکت‌ها بر مبنای وضعیت برای کارتابل مدیریت."""
        t1 = SupportService.get_or_create_active_thread(self.session, self.customer.id)
        SupportService.add_customer_message(self.session, t1.id, self.customer.telegram_id, "پیام ۱")

        all_pending = SupportService.get_all_threads(self.session, status="PENDING_SUPPORT")
        self.assertEqual(len(all_pending), 1)

        closed_threads = SupportService.get_all_threads(self.session, status="CLOSED")
        self.assertEqual(len(closed_threads), 0)


if __name__ == "__main__":
    unittest.main()
