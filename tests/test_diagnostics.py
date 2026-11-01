"""
آزمون‌های خودکار ماژول عیب‌یابی و پشتیبان‌گیری دیتابیس (core/diagnostics.py)
"""

import unittest
from core.database import DatabaseManager
from services.catalog import CatalogService
from services.orders import OrderService
from services.reminders import ReminderService
from services.monitor import MonitorService
from core.diagnostics import SystemDiagnostics


class TestDiagnostics(unittest.TestCase):
    """مجموعه آزمون‌های راستی‌آزمایی یکپارچگی سیستم و تهیه نسخه پشتیبان."""

    def setUp(self):
        self.db_manager = DatabaseManager("sqlite:///:memory:")
        self.db_manager.init_db()

        with self.db_manager.get_session() as session:
            CatalogService.seed_initial_catalog(session)
            MonitorService.seed_initial_monitors(session)
            user = CatalogService.get_or_create_user(session, 111222, "کاربر آزمون")
            svc = CatalogService.get_service_by_code(session, "EMT_VERIFICATION")
            OrderService.create_order(
                session=session,
                user_id=user.id,
                service_id=svc.id,
                form_data={"national_id": "0010350829"},
                actor_telegram_id=111222
            )
            ReminderService.create_reminder(
                session=session,
                user_id=user.id,
                title="یادآور آزمایشی",
                shamsi_date="1406/01/01"
            )

    def tearDown(self):
        self.db_manager.drop_db()

    def test_run_health_check(self):
        """آزمون اجرای چک سلامت و دریافت معیارهای آماری سیستم."""
        with self.db_manager.get_session() as session:
            health = SystemDiagnostics.run_health_check(session)
            self.assertEqual(health["status"], "HEALTHY")
            self.assertEqual(health["database_integrity"], "OK")
            self.assertIn("1405", health["shamsi_time"])

            metrics = health["metrics"]
            self.assertEqual(metrics["total_users"], 1)
            self.assertEqual(metrics["total_orders"], 1)
            self.assertEqual(metrics["pending_orders"], 1)
            self.assertEqual(metrics["active_reminders"], 1)
            self.assertEqual(metrics["monitored_sites"], 6)

    def test_create_backup_snapshot(self):
        """آزمون تولید نسخه پشتیبان کامل و عدم نشت متغیرهای محرمانه."""
        with self.db_manager.get_session() as session:
            snapshot = SystemDiagnostics.create_backup_snapshot(session)

            self.assertEqual(snapshot["version"], "1.0.0")
            self.assertIn("created_at_shamsi", snapshot)
            self.assertEqual(len(snapshot["users"]), 1)
            self.assertEqual(len(snapshot["orders"]), 1)
            self.assertEqual(len(snapshot["reminders"]), 1)
            self.assertEqual(len(snapshot["monitors"]), 6)

            # اطمینان از ساختار سفارش
            order_data = snapshot["orders"][0]
            self.assertIn("LIMO-1405-", order_data["tracking_code"])
            self.assertEqual(order_data["service_code"], "EMT_VERIFICATION")

            # اطمینان از عدم وجود توکن یا پسورد در اسنپ‌شات
            snapshot_str = str(snapshot)
            self.assertNotIn("bot_token", snapshot_str)
            self.assertNotIn("password", snapshot_str)


if __name__ == "__main__":
    unittest.main()
