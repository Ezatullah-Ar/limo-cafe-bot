"""
آزمون‌های خودکار اعتبارسنجی مدل‌های داده‌ای جدید و مایگریشن اسکیما (tests/test_schema_models.py)
سامانه «کافی نت لیمو» - فاز ۲.
راستی‌آزمایی ایجاد جداول کیف پول، تراکنش‌های مالی، تیکتینگ پشتیبانی، ثبت‌نام‌های مقطعی،
راه‌های ارتباطی و تنظیمات سراسری سیستم.
"""

import unittest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.database import Base
from core.models import (
    User,
    Order,
    ServiceCategory,
    ServiceItem,
    Wallet,
    WalletTransaction,
    SupportThread,
    SupportMessage,
    SeasonalCampaign,
    CommunicationChannel,
    SystemSetting
)


class TestSchemaModelsPhase2(unittest.TestCase):
    """آزمون‌های جامع مدل‌های افزوده شده در فاز دوم."""

    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # ایجاد کاربر تستی
        self.user = User(
            telegram_id=123456789,
            full_name="کاربر تستی فاز ۲",
            username="test_user_phase2"
        )
        self.session.add(self.user)
        self.session.commit()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_wallet_creation_and_user_relationship(self):
        """آزمون ساخت کیف پول و ارتباط یک‌به‌یک با کاربر."""
        wallet = Wallet(user_id=self.user.id, balance=500000)
        self.session.add(wallet)
        self.session.commit()

        # بازخوانی و بررسی
        fetched_user = self.session.query(User).filter_by(id=self.user.id).first()
        self.assertIsNotNone(fetched_user.wallet)
        self.assertEqual(fetched_user.wallet.balance, 500000)
        self.assertFalse(fetched_user.wallet.is_frozen)

    def test_wallet_transaction_and_unique_tracking_ref(self):
        """آزمون ثبت تراکنش کیف پول و الزام یکتا بودن tracking_ref."""
        wallet = Wallet(user_id=self.user.id, balance=1000000)
        self.session.add(wallet)
        self.session.commit()

        tx1 = WalletTransaction(
            wallet_id=wallet.id,
            amount=1000000,
            transaction_type="TOPUP",
            status="APPROVED",
            tracking_ref="TX-1405-TEST-001",
            notes="شارژ دستی آزمایشی"
        )
        self.session.add(tx1)
        self.session.commit()

        self.assertEqual(len(wallet.transactions), 1)
        self.assertEqual(wallet.transactions[0].tracking_ref, "TX-1405-TEST-001")

        # تلاش برای ثبت مجدد همین کد پیگیری باید خطا دهد
        tx_duplicate = WalletTransaction(
            wallet_id=wallet.id,
            amount=500000,
            transaction_type="ORDER_PAYMENT",
            status="PENDING",
            tracking_ref="TX-1405-TEST-001"
        )
        self.session.add(tx_duplicate)
        with self.assertRaises(Exception):
            self.session.commit()
        self.session.rollback()

    def test_support_thread_and_messages_lifecycle(self):
        """آزمون چرخه تیکتینگ و پیام‌های گفتگوی پشتیبانی."""
        thread = SupportThread(
            user_id=self.user.id,
            status="NEW"
        )
        self.session.add(thread)
        self.session.commit()

        # مشتری پیامی می‌فرستد
        msg1 = SupportMessage(
            thread_id=thread.id,
            sender_role="CUSTOMER",
            sender_id=self.user.telegram_id,
            message_text="سلام، مدارک من در چه وضعیتی قرار دارد؟"
        )
        self.session.add(msg1)
        thread.status = "PENDING_SUPPORT"
        self.session.commit()

        # اپراتور پاسخ می‌دهد
        msg2 = SupportMessage(
            thread_id=thread.id,
            sender_role="OPERATOR",
            sender_id=999888777,
            message_text="سلام، پرونده شما تایید شده و فردا صادر می‌شود."
        )
        self.session.add(msg2)
        thread.status = "PENDING_CUSTOMER"
        self.session.commit()

        # بررسی پیام‌ها
        fetched_thread = self.session.query(SupportThread).filter_by(id=thread.id).first()
        self.assertEqual(len(fetched_thread.messages), 2)
        self.assertEqual(fetched_thread.status, "PENDING_CUSTOMER")
        self.assertEqual(fetched_thread.messages[0].sender_role, "CUSTOMER")
        self.assertEqual(fetched_thread.messages[1].sender_role, "OPERATOR")

    def test_seasonal_campaign_model(self):
        """آزمون مدل ثبت‌نام‌های مقطعی با بازه زمانی."""
        now = datetime.now(timezone.utc)
        campaign = SeasonalCampaign(
            code="SANJESH_ARSHAD_1405",
            title="ثبت‌نام آزمون کارشناسی ارشد ۱۴۰۵",
            description="مهلت ثبت‌نام داوطلبان کنکور ارشد سراسری",
            start_at=now,
            end_at=now + timedelta(days=7),
            status="ACTIVE",
            base_fee=4500000,
            form_schema={"exam_group": "گروه آزمایشی", "university_choice": "دانشگاه مورد نظر"}
        )
        self.session.add(campaign)
        self.session.commit()

        fetched = self.session.query(SeasonalCampaign).filter_by(code="SANJESH_ARSHAD_1405").first()
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.status, "ACTIVE")
        self.assertEqual(fetched.base_fee, 4500000)
        self.assertIn("exam_group", fetched.form_schema)

    def test_communication_channel_model(self):
        """آزمون کانال‌های ارتباطی و شبکه‌های اجتماعی."""
        ch_eitaa = CommunicationChannel(
            key="EITAA",
            title="کانال ایتا کافی‌نت لیمو",
            value="https://eitaa.com/limocafe",
            is_active=True,
            order_priority=1
        )
        self.session.add(ch_eitaa)
        self.session.commit()

        fetched = self.session.query(CommunicationChannel).filter_by(key="EITAA").first()
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.value, "https://eitaa.com/limocafe")
        self.assertTrue(fetched.is_active)

    def test_system_settings_witness_fee(self):
        """آزمون تنظیمات سراسری سیستم و ثبت مبلغ پیش‌فرض ۳۵۰ تومان برای تامین شاهد."""
        setting = SystemSetting(
            key="witness_provision_fee",
            value="3500000",
            description="هزینه تامین شاهد رسمی توسط کافی نت (به ریال)"
        )
        self.session.add(setting)
        self.session.commit()

        fetched = self.session.query(SystemSetting).filter_by(key="witness_provision_fee").first()
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.value, "3500000")  # ۳۵۰ هزار تومان (۳,۵۰۰,۰۰۰ ریال)


if __name__ == "__main__":
    unittest.main()
