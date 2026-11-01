"""
آزمون‌های خودکار سرویس کیف پول، تراکنش‌ها و دفترکل مالی (tests/test_wallet_service.py)
سامانه «کافی نت لیمو» - فاز ۶.
پوشش شارژ، کسر سفارش، استرداد وجه، ضد پرداخت دوباره (Anti-Double-Spend) و قالب‌بندی کارت مالی.
"""

import unittest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.database import Base
from core.models import User, Wallet, WalletTransaction
from services.wallet import WalletService, generate_transaction_ref


class TestWalletService(unittest.TestCase):
    """مجموعه آزمون‌های اعتبارسنجی قوانین تجاری و مالی کیف پول."""

    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        self.user = User(telegram_id=123456789, full_name="مشتری مالی", username="cust_fin")
        self.admin = User(telegram_id=999888777, full_name="مدیر مالی", role="ADMIN")
        self.session.add_all([self.user, self.admin])
        self.session.commit()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_get_or_create_wallet(self):
        """آزمون ایجاد خودکار کیف پول اولیه با موجودی صفر."""
        wallet = WalletService.get_or_create_wallet(self.session, self.user.id)
        self.assertIsNotNone(wallet.id)
        self.assertEqual(wallet.balance, 0)
        self.assertFalse(wallet.is_frozen)

        # فراخوانی مجدد باید همان شیء را بازگرداند
        wallet2 = WalletService.get_or_create_wallet(self.session, self.user.id)
        self.assertEqual(wallet.id, wallet2.id)

    def test_deposit_and_idempotency(self):
        """آزمون افزایش اعتبار و ممانعت از شارژ مضاعف با شناسه تکراری."""
        wallet = WalletService.get_or_create_wallet(self.session, self.user.id)

        # شارژ ۵۰۰،۰۰۰ ریال
        tx1 = WalletService.deposit(
            session=self.session,
            user_id=self.user.id,
            amount=500000,
            operator_id=self.admin.telegram_id,
            notes="شارژ دستی توسط مدیریت",
            idempotency_ref="DEP-TEST-001"
        )
        self.assertEqual(wallet.balance, 500000)
        self.assertEqual(tx1.amount, 500000)
        self.assertEqual(tx1.transaction_type, "TOPUP")
        self.assertEqual(tx1.tracking_ref, "DEP-TEST-001")

        # تلاش مجدد با همان کلید یکتا نباید موجودی را افزایش دهد
        tx2 = WalletService.deposit(
            session=self.session,
            user_id=self.user.id,
            amount=500000,
            idempotency_ref="DEP-TEST-001"
        )
        self.assertEqual(tx1.id, tx2.id)
        self.assertEqual(wallet.balance, 500000)  # موجودی تغییر نکرده

        # مبلغ منفی یا صفر خطا دارد
        with self.assertRaises(ValueError):
            WalletService.deposit(self.session, self.user.id, amount=-100)

    def test_charge_order_payment_and_anti_double_spend(self):
        """آزمون کسر وجه سفارش و قفل ضد پرداخت دوباره (Anti Double-Spending)."""
        wallet = WalletService.get_or_create_wallet(self.session, self.user.id)
        WalletService.deposit(self.session, self.user.id, amount=1000000)

        # ۱. کسر هزینه سفارش ۳۰۰،۰۰۰ ریال
        ok, msg, tx = WalletService.charge_order_payment(
            session=self.session,
            user_id=self.user.id,
            amount=300000,
            order_tracking_code="LIMO-1405-11111"
        )
        self.assertTrue(ok)
        self.assertEqual(wallet.balance, 700000)
        self.assertEqual(tx.amount, -300000)
        self.assertEqual(tx.transaction_type, "ORDER_PAYMENT")

        # ۲. تلاش مجدد برای پرداخت همان سفارش (دوبار کلیک کردن کاربر یا تکرار درخواست)
        ok2, msg2, tx2 = WalletService.charge_order_payment(
            session=self.session,
            user_id=self.user.id,
            amount=300000,
            order_tracking_code="LIMO-1405-11111"
        )
        self.assertTrue(ok2)
        self.assertIn("پرداخت گردیده است", msg2)
        self.assertEqual(wallet.balance, 700000)  # وجه دوباره کسر نشد!

        # ۳. عدم کفایت موجودی
        ok3, msg3, tx3 = WalletService.charge_order_payment(
            session=self.session,
            user_id=self.user.id,
            amount=900000  # بیش از ۷۰۰ هزار ریال
        )
        self.assertFalse(ok3)
        self.assertIn("موجودی کیف پول شما کافی نیست", msg3)
        self.assertEqual(wallet.balance, 700000)

    def test_refund_order_payment(self):
        """آزمون استرداد وجه سفارش لغوشده و ممانعت از بازگشت دوباره."""
        wallet = WalletService.get_or_create_wallet(self.session, self.user.id)
        WalletService.deposit(self.session, self.user.id, amount=1000000)

        # پرداخت سفارش
        WalletService.charge_order_payment(
            session=self.session,
            user_id=self.user.id,
            amount=400000,
            order_tracking_code="LIMO-1405-22222"
        )
        self.assertEqual(wallet.balance, 600000)

        # استرداد وجه
        ok_ref, msg_ref, tx_ref = WalletService.refund(
            session=self.session,
            user_id=self.user.id,
            amount=400000,
            order_tracking_code="LIMO-1405-22222",
            reason="نقص مدارک غیرقابل رفع",
            operator_id=self.admin.telegram_id
        )
        self.assertTrue(ok_ref)
        self.assertEqual(wallet.balance, 1000000)
        self.assertEqual(tx_ref.amount, 400000)
        self.assertEqual(tx_ref.transaction_type, "REFUND")

        # تلاش مجدد برای استرداد همان سفارش نباید مجدداً حساب را بستانکار کند
        ok_ref2, msg_ref2, tx_ref2 = WalletService.refund(
            session=self.session,
            user_id=self.user.id,
            amount=400000,
            order_tracking_code="LIMO-1405-22222"
        )
        self.assertTrue(ok_ref2)
        self.assertEqual(wallet.balance, 1000000)  # موجودی ثابت ماند

    def test_frozen_wallet_blocks_transactions(self):
        """آزمون مسدود بودن کیف پول در برابر تراکنش‌های مالی."""
        wallet = WalletService.get_or_create_wallet(self.session, self.user.id)
        wallet.is_frozen = True
        self.session.commit()

        # شارژ مسدود است
        with self.assertRaises(PermissionError):
            WalletService.deposit(self.session, self.user.id, amount=100000)

        # پرداخت مسدود است
        ok, msg, tx = WalletService.charge_order_payment(self.session, self.user.id, amount=50000)
        self.assertFalse(ok)
        self.assertIn("مسدود", msg)

    def test_format_wallet_card(self):
        """آزمون تولید متن نمایشی و رسمی کارت کیف پول."""
        wallet = WalletService.get_or_create_wallet(self.session, self.user.id)
        WalletService.deposit(self.session, self.user.id, amount=1500000, notes="شارژ نقدی")

        history = WalletService.get_transaction_history(self.session, self.user.id)
        card = WalletService.format_wallet_card(wallet, history)

        self.assertIn("1,500,000", card)
        self.assertIn("150,000", card)  # تومان
        self.assertIn("افزایش اعتبار", card)
        self.assertIn("🟢 فعال", card)


if __name__ == "__main__":
    unittest.main()
