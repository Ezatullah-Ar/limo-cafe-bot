"""
آزمون‌های خودکار سرویس کاتالوگ خدمات و کاربران (services/catalog.py)
"""

import unittest
from core.database import DatabaseManager
from core.models import ServiceCategory, ServiceItem
from services.catalog import CatalogService


class TestCatalogService(unittest.TestCase):
    """مجموعه آزمون‌های منطق تجاری کاتالوگ خدمات کافی نت لیمو."""

    def setUp(self):
        self.db_manager = DatabaseManager("sqlite:///:memory:")
        self.db_manager.init_db()

    def tearDown(self):
        self.db_manager.drop_db()

    def test_seed_initial_catalog_and_idempotency(self):
        """آزمون ثبت داده‌های اولیه کاتالوگ و اجرای تکرارپذیر (Idempotent)."""
        with self.db_manager.get_session() as session:
            CatalogService.seed_initial_catalog(session)

        # اعتبارسنجی ثبت دسته‌بندی‌های ۶ گانه و خدمات اولیه
        with self.db_manager.get_session() as session:
            categories = CatalogService.get_categories(session)
            self.assertEqual(len(categories), 6)
            cat_codes = [c.code for c in categories]
            self.assertIn("ALIEN_AND_CODES", cat_codes)
            self.assertIn("UNIVERSITY_SERVICES", cat_codes)
            self.assertIn("TICKETS_TRAVEL", cat_codes)
            self.assertIn("GOVERNMENT_INTERNET", cat_codes)
            self.assertIn("PORTAL_AND_WALLET", cat_codes)
            self.assertIn("SUPPORT_AND_CONTACT", cat_codes)

            services = CatalogService.get_services_by_category(session, "UNIVERSITY_SERVICES")
            self.assertGreaterEqual(len(services), 4)
            service_codes = [s.code for s in services]
            self.assertIn("EMT_VERIFICATION", service_codes)
            self.assertIn("SANJESH_REGISTRATION", service_codes)
            self.assertIn("PNU_SERVICES", service_codes)
            self.assertIn("IAU_SERVICES", service_codes)

            # سازگاری با کد قدیمی STUDENT_SERVICES
            old_alias_services = CatalogService.get_services_by_category(session, "STUDENT_SERVICES")
            self.assertGreaterEqual(len(old_alias_services), 4)

        # اجرای مجدد Seed برای اثبات عدم ایجاد رکوردهای تکراری
        with self.db_manager.get_session() as session:
            CatalogService.seed_initial_catalog(session)

        with self.db_manager.get_session() as session:
            services_after = CatalogService.get_services_by_category(session, "UNIVERSITY_SERVICES")
            self.assertEqual(len(services_after), len(services))

    def test_get_service_by_code_details(self):
        """آزمون دریافت جزئیات دقیق یک خدمت (تاییدیه تحصیلی و سنجش)."""
        with self.db_manager.get_session() as session:
            CatalogService.seed_initial_catalog(session)

            # خدمت تاییدیه تحصیلی
            emt_svc = CatalogService.get_service_by_code(session, "EMT_VERIFICATION")
            self.assertIsNotNone(emt_svc)
            self.assertEqual(emt_svc.official_url, "https://emt.medu.ir/")
            self.assertIn("national_id", emt_svc.required_fields)
            self.assertGreater(len(emt_svc.required_docs), 0)

            # خدمت ثبت‌نام سنجش
            sanjesh_svc = CatalogService.get_service_by_code(session, "SANJESH_REGISTRATION")
            self.assertIsNotNone(sanjesh_svc)
            self.assertEqual(sanjesh_svc.official_url, "https://www.sanjesh.org/")
            self.assertIn("exam_type", sanjesh_svc.required_fields)

            # کد ناموجود
            missing_svc = CatalogService.get_service_by_code(session, "NON_EXISTING_SERVICE")
            self.assertIsNone(missing_svc)

    def test_get_or_create_user(self):
        """آزمون ایجاد کاربر و بازیابی/بروزرسانی مشخصات."""
        with self.db_manager.get_session() as session:
            user = CatalogService.get_or_create_user(
                session,
                telegram_id=777888999,
                full_name="رضا رضایی",
                username="reza_rezaei"
            )
            self.assertEqual(user.full_name, "رضا رضایی")

        # فراخوانی مجدد با نام جدید
        with self.db_manager.get_session() as session:
            updated_user = CatalogService.get_or_create_user(
                session,
                telegram_id=777888999,
                full_name="رضا رضایی نیا",
                username="reza_new"
            )
            self.assertEqual(updated_user.full_name, "رضا رضایی نیا")
            self.assertEqual(updated_user.username, "reza_new")


if __name__ == "__main__":
    unittest.main()
