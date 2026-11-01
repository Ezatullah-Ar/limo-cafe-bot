"""
آزمون‌های خودکار سیستم CRM، پرونده مشتریان، تنظیمات تعرفه شاهد و کانال‌های ارتباطی (Phase 8).
"""

import unittest
from core.database import DatabaseManager
from core.models import User, Order, ServiceCategory, ServiceItem, CommunicationChannel, SystemSetting, OrderAuditLog
from services.catalog import CatalogService
from services.crm import CRMService
from services.wallet import WalletService


class TestCRMAndDashboard(unittest.TestCase):
    """مجموعه آزمون‌های CRM مشتریان، کانال‌های ارتباطی و تنظیمات سیستم."""

    def setUp(self):
        self.db_manager = DatabaseManager("sqlite:///:memory:")
        self.db_manager.init_db()

        with self.db_manager.get_session() as session:
            CatalogService.seed_initial_catalog(session)

    def tearDown(self):
        self.db_manager.drop_db()

    def test_seed_channels_and_system_settings(self):
        """آزمون درج خودکار و تکرارپذیر کانال‌های ارتباطی و تنظیمات تعرفه شاهد."""
        with self.db_manager.get_session() as session:
            channels = CatalogService.get_channels(session)
            self.assertGreaterEqual(len(channels), 6)
            keys = [c.key for c in channels]
            self.assertIn("PHONE", keys)
            self.assertIn("TELEGRAM", keys)
            self.assertIn("EITAA", keys)
            self.assertIn("RUBIKA", keys)
            self.assertIn("BALE", keys)
            self.assertIn("INSTAGRAM", keys)

            # بررسی تنظیم تعرفه پیش‌فرض ۳۵۰ هزار تومان (۳،۵۰۰،۰۰۰ ریال)
            witness_fee = CatalogService.get_witness_fee(session)
            self.assertEqual(witness_fee, 3500000)

    def test_update_channel_and_settings(self):
        """آزمون ویرایش داینامیک یک کانال ارتباطی و تنظیمات تعرفه شاهد."""
        with self.db_manager.get_session() as session:
            # بروزرسانی کانال ایتا
            ch = CatalogService.update_channel(session, "EITAA", "https://eitaa.com/limo_official")
            self.assertIsNotNone(ch)
            self.assertEqual(ch.value, "https://eitaa.com/limo_official")

            # تغییر تنظیمات هزینه شاهد با مجوز
            CatalogService.set_setting(session, "witness_provision_fee", "4000000")
            new_fee = CatalogService.get_witness_fee(session)
            self.assertEqual(new_fee, 4000000)

    def test_crm_customer_list_and_search(self):
        """آزمون استخراج لیست مشتریان و جست‌وجوی هوشمند CRM."""
        with self.db_manager.get_session() as session:
            # ساخت چند کاربر تستی
            u1 = CatalogService.get_or_create_user(session, telegram_id=111222, full_name="سارا حسینی", username="sara_h")
            u2 = CatalogService.get_or_create_user(session, telegram_id=333444, full_name="کامران نادری", username="kamran_n")

            # ایجاد سفارش و شارژ کیف پول برای کاربر ۱
            svc = session.query(ServiceItem).first()
            o = Order(user_id=u1.id, service_id=svc.id, tracking_code="LIMO-1405-TEST1", status="PENDING")
            session.add(o)
            session.flush()

            WalletService.deposit(session, u1.id, 500000, "DEP-001")

        with self.db_manager.get_session() as session:
            # لیست کلیه کاربران
            customers = CRMService.get_customers(session)
            self.assertGreaterEqual(len(customers), 2)

            # جست‌وجوی اختصاصی بر اساس نام
            search_sara = CRMService.get_customers(session, query_str="سارا")
            self.assertEqual(len(search_sara), 1)
            self.assertEqual(search_sara[0]["full_name"], "سارا حسینی")
            self.assertEqual(search_sara[0]["orders_count"], 1)
            self.assertEqual(search_sara[0]["wallet_balance"], 500000)

            # جست‌وجو بر اساس شناسه عددی تلگرام
            search_id = CRMService.get_customers(session, query_str="333444")
            self.assertEqual(len(search_id), 1)
            self.assertEqual(search_id[0]["full_name"], "کامران نادری")

    def test_crm_customer_dossier_and_operator_assignment(self):
        """آزمون استخراج پرونده کامل مشتری (Dossier) و تخصیص اپراتور مسئول پرونده."""
        with self.db_manager.get_session() as session:
            user = CatalogService.get_or_create_user(session, telegram_id=555666, full_name="مهدی راد", username="mehdi_rad")
            svc = session.query(ServiceItem).first()

            # ثبت سفارش
            order = Order(
                user_id=user.id,
                service_id=svc.id,
                tracking_code="LIMO-1405-DOSSIER",
                status="PENDING",
                form_data={"phone": "09121112233"}
            )
            session.add(order)
            session.flush()
            order_id = order.id

            # تخصیص اپراتور به پرونده
            CRMService.assign_operator_to_order(
                session=session,
                order_id=order_id,
                operator_name="علی احمدی (کارشناس ارشد)",
                actor_id=user.id,
                note="پرونده اولویت‌دار"
            )

        with self.db_manager.get_session() as session:
            # بازیابی پرونده کامل مشتری
            dossier = CRMService.get_customer_dossier(session, user_id=user.id)
            self.assertIsNotNone(dossier)
            self.assertEqual(dossier["user"]["full_name"], "مهدی راد")
            self.assertEqual(len(dossier["orders"]), 1)

            ord_info = dossier["orders"][0]
            self.assertEqual(ord_info["tracking_code"], "LIMO-1405-DOSSIER")
            self.assertIn("علی احمدی", ord_info["operator_notes"])

            # بررسی لاگ حسابرسی سفارش
            self.assertGreaterEqual(len(dossier["audit_logs"]), 1)
            self.assertEqual(dossier["audit_logs"][0]["action"], "ASSIGN_OPERATOR")
            self.assertIn("تخصیص به اپراتور", dossier["audit_logs"][0]["note"])

    def test_crm_dossier_non_existing_user(self):
        """آزمون عدم بازگرداندن پرونده برای کاربر ناموجود (عایق‌بندی و امنیت)."""
        with self.db_manager.get_session() as session:
            dossier = CRMService.get_customer_dossier(session, user_id=99999999)
            self.assertIsNone(dossier)


if __name__ == "__main__":
    unittest.main()
