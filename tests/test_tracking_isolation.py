"""
آزمون‌های خودکار عایق‌بندی اطلاعات مشتریان، استپر ۴ مرحله‌ای و پیگیری پرونده‌ها (tests/test_tracking_isolation.py)
سامانه «کافی نت لیمو» - فاز ۵.
پوشش عایق‌بندی کامل (Tenant Isolation)، ممانعت از افشای اطلاعات دیگران، استپر واقعی، تاریخ‌های شمسی و جلوگیری از اعلان تکراری.
"""

import unittest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.database import Base
from core.models import User, ServiceCategory, ServiceItem, Order, OrderDocument
from services.tracking import (
    generate_tracking_code,
    format_order_status_persian,
    generate_order_stepper,
    render_order_card,
    render_user_orders_list
)
from services.orders import OrderService
from services.notifications import NotificationService


class TestTrackingAndIsolation(unittest.TestCase):
    """مجموعه آزمون‌های تخصصی امنیت، رهگیری و حریم خصوصی مشتریان."""

    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # تعریف دسته‌بندی، دو مشتری مجزا و یک مدیر
        self.category = ServiceCategory(code="UNI", title="خدمات دانشگاهی", description="خدمات آزمون و دانشگاه")
        self.customer1 = User(telegram_id=111111111, full_name="مشتری اول", username="cust_one")
        self.customer2 = User(telegram_id=222222222, full_name="مشتری دوم", username="cust_two")
        self.admin = User(telegram_id=999888777, full_name="مدیر سامانه", role="ADMIN")
        
        self.session.add_all([self.category, self.customer1, self.customer2, self.admin])
        self.session.commit()

        self.service = ServiceItem(
            category_id=self.category.id,
            code="TEST_SVC",
            title="ثبت‌نام دانشگاه پیام نور",
            description="ثبت‌نام اینترنتی در سیستم گلستان پیام نور",
            base_fee=250000
        )
        self.session.add(self.service)
        self.session.commit()

        # ثبت سفارش برای مشتری اول
        self.order1 = OrderService.create_order(
            session=self.session,
            user_id=self.customer1.id,
            service_id=self.service.id,
            form_data={"national_code": "0012345678"},
            actor_telegram_id=self.customer1.telegram_id
        )
        self.order1.created_at = datetime(2026, 10, 30, 10, 0, 0, tzinfo=timezone.utc)
        self.session.commit()

    def tearDown(self):
        NotificationService.clear_cache()
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_tenant_isolation_blocks_unauthorized_customer(self):
        """آزمون حیاتی امنیت و حریم خصوصی: ممانعت ۱۰۰٪ از استعلام پرونده دیگران."""
        # ۱. مشتری اول پرونده خودش را استعلام می‌کند -> مجاز
        allowed1, text1 = render_order_card(
            order=self.order1,
            requester_telegram_id=self.customer1.telegram_id,
            is_admin_or_op=False
        )
        self.assertTrue(allowed1)
        self.assertIn(self.order1.tracking_code, text1)
        self.assertIn("استپر پرونده", text1)

        # ۲. مشتری دوم تلاش می‌کند با دانستن یا حدس زدن کد رهگیری، سفارش مشتری اول را ببیند -> مسدود و خطا
        allowed2, text2 = render_order_card(
            order=self.order1,
            requester_telegram_id=self.customer2.telegram_id,
            is_admin_or_op=False
        )
        self.assertFalse(allowed2)
        self.assertIn("خطای دسترسی", text2)
        self.assertNotIn("استپر پرونده", text2)
        self.assertNotIn(self.service.title, text2)  # عدم افشای عنوان خدمت یا جزئیات

        # ۳. مدیر یا اپراتور پرونده را استعلام می‌کند -> مجاز
        allowed_admin, text_admin = render_order_card(
            order=self.order1,
            requester_telegram_id=self.admin.telegram_id,
            is_admin_or_op=True
        )
        self.assertTrue(allowed_admin)
        self.assertIn(self.order1.tracking_code, text_admin)

    def test_order_stepper_progression(self):
        """آزمون استپر بصری ۴ مرحله‌ای برای تمامی وضعیت‌های چرخه حیات پرونده."""
        # الف: وضعیت در انتظار بررسی اولیه (PENDING)
        s_pending = generate_order_stepper("PENDING")
        self.assertEqual(s_pending["current_step"], 1)
        self.assertIn("در نوبت بررسی", s_pending["steps"][1][1])

        # ب: نقص مدرک (NEED_INFO)
        s_info = generate_order_stepper("NEED_INFO")
        self.assertEqual(s_info["current_step"], 2)
        self.assertIn("نقص مدرک", s_info["steps"][1][1])
        self.assertIn("نقص مدرک است", s_info["action_required"])

        # ج: تایید شده (APPROVED)
        s_app = generate_order_stepper("APPROVED")
        self.assertEqual(s_app["current_step"], 2)
        self.assertIn("تایید مدارک", s_app["steps"][1][1])

        # د: در حال اقدام در سامانه (IN_PROGRESS)
        s_prog = generate_order_stepper("IN_PROGRESS")
        self.assertEqual(s_prog["current_step"], 3)
        self.assertIn("در حال اقدام", s_prog["steps"][2][1])

        # ه: تکمیل نهایی (COMPLETED)
        s_done = generate_order_stepper("COMPLETED")
        self.assertEqual(s_done["current_step"], 4)
        self.assertIn("تکمیل نهایی", s_done["steps"][3][1])

    def test_user_orders_list_portal(self):
        """آزمون پورتال «درخواست‌های من» با تفکیک قطعی بر اساس telegram_id."""
        # در ابتدا مشتری دوم هیچ سفارشی ندارد
        orders_c2 = OrderService.get_user_orders_by_telegram_id(self.session, self.customer2.telegram_id)
        self.assertEqual(len(orders_c2), 0)
        empty_text = render_user_orders_list(orders_c2)
        self.assertIn("هیچ سفارش یا پرونده فعالی در سامانه ندارید", empty_text)

        # مشتری اول ۱ سفارش دارد
        orders_c1 = OrderService.get_user_orders_by_telegram_id(self.session, self.customer1.telegram_id)
        self.assertEqual(len(orders_c1), 1)
        c1_text = render_user_orders_list(orders_c1)
        self.assertIn(self.order1.tracking_code, c1_text)
        self.assertIn("ثبت‌نام دانشگاه پیام نور", c1_text)

    def test_idempotent_notification_deduplication(self):
        """آزمون جلوگیری از ارسال پیام‌های تکراری به کاربر در هنگام تکرار رویداد."""
        order_id = self.order1.id
        status = "APPROVED"

        # بار اول نباید تکراری باشد
        self.assertFalse(NotificationService.is_alert_duplicate(order_id, status))
        
        # ثبت ارسال
        NotificationService.record_alert_sent(order_id, status)

        # بار دوم باید به عنوان تکراری شناسایی شده و جلوی ارسال گرفته شود
        self.assertTrue(NotificationService.is_alert_duplicate(order_id, status))

        # تغییر به وضعیت جدید مجاز است و تکراری نیست
        self.assertFalse(NotificationService.is_alert_duplicate(order_id, "COMPLETED"))


if __name__ == "__main__":
    unittest.main()
