"""
آزمون‌های خودکار ماژول سفارشات، کدهای رهگیری و لاگ حسابرسی (services/orders.py و services/tracking.py)
"""

import unittest
from core.database import DatabaseManager
from core.models import User, ServiceCategory, ServiceItem
from services.catalog import CatalogService
from services.orders import OrderService
from services.tracking import generate_tracking_code, format_order_status_persian


class TestOrders(unittest.TestCase):
    """مجموعه آزمون‌های ایجاد و مدیریت سفارشات و کد رهگیری."""

    def setUp(self):
        self.db_manager = DatabaseManager("sqlite:///:memory:")
        self.db_manager.init_db()
        with self.db_manager.get_session() as session:
            CatalogService.seed_initial_catalog(session)
            self.user = CatalogService.get_or_create_user(
                session,
                telegram_id=12345001,
                full_name="مشتری تستی",
                username="test_customer"
            )
            self.service = CatalogService.get_service_by_code(session, "EMT_VERIFICATION")
            self.user_id = self.user.id
            self.service_id = self.service.id

    def tearDown(self):
        self.db_manager.drop_db()

    def test_tracking_code_generator_format(self):
        """آزمون فرمت و ساختار کد رهگیری یکتا."""
        code = generate_tracking_code(prefix="LIMO", year=1405)
        self.assertTrue(code.startswith("LIMO-1405-"))
        parts = code.split("-")
        self.assertEqual(len(parts), 3)
        self.assertEqual(len(parts[2]), 5)
        self.assertTrue(parts[2].isdigit())

    def test_create_order_and_audit_trail(self):
        """آزمون ثبت سفارش جدید و تولید خودکار Audit Log اولیه."""
        form_data = {
            "national_id": "0010350829",
            "education_level": "کارشناسی",
            "school_or_university": "دانشگاه تهران",
            "graduation_year": "1402",
            "destination_org": "وزارت علوم"
        }

        with self.db_manager.get_session() as session:
            order = OrderService.create_order(
                session=session,
                user_id=self.user_id,
                service_id=self.service_id,
                form_data=form_data,
                actor_telegram_id=12345001
            )
            tracking_code = order.tracking_code
            self.assertIsNotNone(order.id)
            self.assertEqual(order.status, "PENDING")
            self.assertEqual(order.form_data["national_id"], "0010350829")

        # بررسی ذخیره در دیتابیس و اعتبارسنجی لاگ حسابرسی
        with self.db_manager.get_session() as session:
            saved_order = OrderService.get_order_by_tracking_code(session, tracking_code)
            self.assertIsNotNone(saved_order)
            self.assertEqual(saved_order.tracking_code, tracking_code)
            self.assertEqual(len(saved_order.audit_logs), 1)
            self.assertEqual(saved_order.audit_logs[0].from_status, "NONE")
            self.assertEqual(saved_order.audit_logs[0].to_status, "PENDING")

    def test_update_order_status_and_operator_notes(self):
        """آزمون تغییر وضعیت سفارش توسط اپراتور و ثبت سوابق تغییرات."""
        with self.db_manager.get_session() as session:
            order = OrderService.create_order(
                session=session,
                user_id=self.user_id,
                service_id=self.service_id,
                form_data={"test": "data"},
                actor_telegram_id=12345001
            )
            order_id = order.id

        # اپراتور وضعیت را به APPROVED تغییر می‌دهد
        operator_tg_id = 99990001
        with self.db_manager.get_session() as session:
            updated = OrderService.update_order_status(
                session=session,
                order_id=order_id,
                new_status="APPROVED",
                actor_telegram_id=operator_tg_id,
                note="مدارک اولیه بررسی و تایید گردید."
            )
            self.assertEqual(updated.status, "APPROVED")
            self.assertEqual(updated.operator_notes, "مدارک اولیه بررسی و تایید گردید.")

        # بررسی لاگ‌های حسابرسی
        with self.db_manager.get_session() as session:
            re_order = session.query(OrderService.get_order_by_tracking_code(session, updated.tracking_code).__class__).filter_by(id=order_id).first()
            self.assertEqual(len(re_order.audit_logs), 2)
            self.assertEqual(re_order.audit_logs[1].from_status, "PENDING")
            self.assertEqual(re_order.audit_logs[1].to_status, "APPROVED")
            self.assertEqual(re_order.audit_logs[1].actor_id, operator_tg_id)

    def test_attach_document_to_order(self):
        """آزمون پیوست کردن مدرک به سفارش."""
        with self.db_manager.get_session() as session:
            order = OrderService.create_order(
                session=session,
                user_id=self.user_id,
                service_id=self.service_id,
                form_data={"k": "v"},
                actor_telegram_id=12345001
            )
            doc = OrderService.attach_document(
                session=session,
                order_id=order.id,
                file_id="tg_file_id_xyz123",
                file_name="diploma_scan.pdf",
                file_type="DOCUMENT",
                file_size=102400
            )
            self.assertIsNotNone(doc.id)

        with self.db_manager.get_session() as session:
            order_re = session.query(order.__class__).filter_by(id=order.id).first()
            self.assertEqual(len(order_re.documents), 1)
            self.assertEqual(order_re.documents[0].file_name, "diploma_scan.pdf")

    def test_format_order_status_persian(self):
        """آزمون نمایش صحیح آیکون و عناوین فارسی وضعیت‌ها."""
        res_pending = format_order_status_persian("PENDING")
        self.assertEqual(res_pending["icon"], "⏳")
        self.assertIn("در انتظار", res_pending["title"])

        res_approved = format_order_status_persian("APPROVED")
        self.assertEqual(res_approved["icon"], "🟢")

        res_unknown = format_order_status_persian("UNKNOWN_CUSTOM")
        self.assertEqual(res_unknown["icon"], "🔄")


if __name__ == "__main__":
    unittest.main()
