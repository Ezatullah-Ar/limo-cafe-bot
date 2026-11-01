"""
آزمون‌های خودکار ماژول دیتابیس و مدل‌های رابطه‌ای (core/database.py و core/models.py)
"""

import unittest
from sqlalchemy.exc import IntegrityError
from core.database import DatabaseManager, Base
from core.models import User, ServiceCategory, ServiceItem


class TestDatabase(unittest.TestCase):
    """مجموعه آزمون‌های پایگاه داده، تراکنش‌ها و مدل‌های داده."""

    def setUp(self):
        # استفاده از دیتابیس حافظه‌ای ایزوله برای آزمون‌ها
        self.db_manager = DatabaseManager("sqlite:///:memory:")
        self.db_manager.init_db()

    def tearDown(self):
        self.db_manager.drop_db()

    def test_user_creation_and_unique_constraint(self):
        """آزمون ساخت کاربر و قید یکتایی telegram_id."""
        with self.db_manager.get_session() as session:
            user1 = User(
                telegram_id=111222333,
                full_name="علی محمدی",
                username="alimohammadi",
                role="CUSTOMER"
            )
            session.add(user1)

        # بازیابی و اعتبارسنجی
        with self.db_manager.get_session() as session:
            saved_user = session.query(User).filter_by(telegram_id=111222333).first()
            self.assertIsNotNone(saved_user)
            self.assertEqual(saved_user.full_name, "علی محمدی")
            self.assertEqual(saved_user.role, "CUSTOMER")

        # تلاش برای ثبت کاربر تکراری با همان telegram_id (باید IntegrityError رخ دهد)
        with self.assertRaises(IntegrityError):
            with self.db_manager.get_session() as session:
                duplicate_user = User(
                    telegram_id=111222333,
                    full_name="شخص دیگر"
                )
                session.add(duplicate_user)

    def test_category_and_service_cascade(self):
        """آزمون ارتباط یک‌به‌چند دسته‌بندی و خدمات و حذف آبشاری (Cascade Delete)."""
        with self.db_manager.get_session() as session:
            cat = ServiceCategory(
                code="TEST_CAT",
                title="دسته‌بندی آزمایشی"
            )
            session.add(cat)
            session.flush()

            svc1 = ServiceItem(
                category_id=cat.id,
                code="SVC_TEST_1",
                title="خدمت تستی ۱",
                description="توضیحات ۱"
            )
            svc2 = ServiceItem(
                category_id=cat.id,
                code="SVC_TEST_2",
                title="خدمت تستی ۲",
                description="توضیحات ۲"
            )
            session.add_all([svc1, svc2])

        # بررسی وجود ۲ خدمت برای دسته‌بندی
        with self.db_manager.get_session() as session:
            cat = session.query(ServiceCategory).filter_by(code="TEST_CAT").first()
            self.assertEqual(len(cat.services), 2)

            # حذف دسته‌بندی
            session.delete(cat)

        # بررسی حذف شدن آبشاری خدمات زیرمجموعه
        with self.db_manager.get_session() as session:
            remaining_services = session.query(ServiceItem).filter(
                ServiceItem.code.in_(["SVC_TEST_1", "SVC_TEST_2"])
            ).all()
            self.assertEqual(len(remaining_services), 0)

    def test_transaction_rollback_on_error(self):
        """آزمون رول‌بک خودکار تراکنش در صورت بروز استثنا."""
        try:
            with self.db_manager.get_session() as session:
                user = User(telegram_id=999888, full_name="کاربر رول‌بک")
                session.add(user)
                # ایجاد خطای عمدی برای تحریک رول‌بک
                raise RuntimeError("خطای عمدی در تراکنش")
        except RuntimeError:
            pass

        # اطمینان از عدم ذخیره کاربر به دلیل رول‌بک
        with self.db_manager.get_session() as session:
            user = session.query(User).filter_by(telegram_id=999888).first()
            self.assertIsNone(user)


if __name__ == "__main__":
    unittest.main()
