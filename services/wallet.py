"""
سرویس جامع مدیریت کیف پول، تراکنش‌ها، دفترکل مالی و ضد کلاهبرداری/دوبار پرداخت (services/wallet.py)
سامانه «کافی نت لیمو» - فاز ۶.
شامل ثبت تراکنش‌ها، کسر و شارژ ایمن، استرداد وجه، کنترل Idempotency و گزارش گردش حساب.
"""

import logging
import secrets
import string
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Any
from sqlalchemy.orm import Session
from core.models import Wallet, WalletTransaction, User
from core.calendar import utc_to_jalali_datetime, format_jalali_date

logger = logging.getLogger("wallet")


def generate_transaction_ref(prefix: str = "TX") -> str:
    """تولید شناسه یکتای پیگیری مالی غیرقابل حدس (مثال: TX-1405-78219)."""
    rand = "".join(secrets.choice(string.digits) for _ in range(5))
    return f"{prefix}-1405-{rand}"


class WalletService:
    """سرویس مدیریت مالی، کیف پول و دفترکل تراکنش‌های مشتریان."""

    @staticmethod
    def get_or_create_wallet(session: Session, user_id: int) -> Wallet:
        """یافتن یا ایجاد کیف پول اولیه با موجودی صفر برای کاربر."""
        wallet = session.query(Wallet).filter_by(user_id=user_id).first()
        if not wallet:
            wallet = Wallet(user_id=user_id, balance=0, is_frozen=False)
            session.add(wallet)
            session.commit()
            session.refresh(wallet)
            logger.info("New wallet created for user_id=%d", user_id)
        return wallet

    @staticmethod
    def get_wallet_by_telegram_id(session: Session, telegram_id: int) -> Optional[Wallet]:
        """یافتن کیف پول بر مبنای شناسه کاربری تلگرام."""
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            return None
        return WalletService.get_or_create_wallet(session, user.id)

    @staticmethod
    def deposit(
        session: Session,
        user_id: int,
        amount: int,
        operator_id: Optional[int] = None,
        notes: str = "افزایش اعتبار حساب",
        receipt_file_id: Optional[str] = None,
        idempotency_ref: Optional[str] = None
    ) -> WalletTransaction:
        """
        شارژ و افزایش اعتبار کیف پول متقاضی همراه با صدور تراکنش و ثبت شناسه یکتا.
        """
        if amount <= 0:
            raise ValueError("مبلغ شارژ باید بزرگتر از صفر باشد.")

        wallet = WalletService.get_or_create_wallet(session, user_id)
        if wallet.is_frozen:
            raise PermissionError("کیف پول مورد نظر مسدود است و امکان شارژ آن وجود ندارد.")

        # بررسی کلید تکراری بودن جهت جلوگیری از شارژ مکرر
        tx_ref = idempotency_ref or generate_transaction_ref("DEP")
        existing = session.query(WalletTransaction).filter_by(tracking_ref=tx_ref).first()
        if existing:
            logger.warning("Duplicate deposit attempt blocked: ref=%s", tx_ref)
            return existing

        wallet.balance += amount
        wallet.updated_at = datetime.now(timezone.utc)

        tx = WalletTransaction(
            wallet_id=wallet.id,
            amount=amount,
            transaction_type="TOPUP",
            status="APPROVED",
            tracking_ref=tx_ref,
            receipt_file_id=receipt_file_id,
            operator_id=operator_id,
            notes=notes
        )
        session.add(tx)
        session.commit()
        session.refresh(tx)
        session.refresh(wallet)
        logger.info("Wallet user_id=%d credited by %d Rials (new balance: %d, ref: %s)", user_id, amount, wallet.balance, tx_ref)
        return tx

    @staticmethod
    def charge_order_payment(
        session: Session,
        user_id: int,
        amount: int,
        order_tracking_code: Optional[str] = None,
        idempotency_key: Optional[str] = None
    ) -> Tuple[bool, str, Optional[WalletTransaction]]:
        """
        کسر وجه و پرداخت هزینه سفارش از کیف پول با قفل ضد پرداخت دوباره (Anti-Double-Spend).
        """
        if amount <= 0:
            return False, "مبلغ پرداخت نامعتبر است.", None

        wallet = WalletService.get_or_create_wallet(session, user_id)
        if wallet.is_frozen:
            return False, "کیف پول شما مسدود می‌باشد؛ لطفاً با پشتیبانی تماس حاصل فرمایید.", None

        # بررسی قفل Idempotency جهت ممانعت از کسر دوباره در صورت کلیک مکرر
        tx_ref = idempotency_key or (f"PAY-{order_tracking_code}" if order_tracking_code else generate_transaction_ref("PAY"))
        existing_tx = session.query(WalletTransaction).filter_by(tracking_ref=tx_ref).first()
        if existing_tx and existing_tx.status == "APPROVED":
            logger.warning("Order payment already settled: ref=%s", tx_ref)
            return True, "این سفارش قبلاً از موجودی کیف پول شما پرداخت گردیده است.", existing_tx

        if wallet.balance < amount:
            shortage = amount - wallet.balance
            return False, f"موجودی کیف پول شما کافی نیست.\nموجودی فعلی: {wallet.balance:,} ریال\nکسری وجه: {shortage:,} ریال", None

        wallet.balance -= amount
        wallet.updated_at = datetime.now(timezone.utc)

        note_str = f"پرداخت هزینه سفارش {order_tracking_code}" if order_tracking_code else "پرداخت هزینه سفارش اینترنتی"
        tx = WalletTransaction(
            wallet_id=wallet.id,
            amount=-amount,
            transaction_type="ORDER_PAYMENT",
            status="APPROVED",
            tracking_ref=tx_ref,
            notes=note_str
        )
        session.add(tx)
        session.commit()
        session.refresh(tx)
        session.refresh(wallet)
        logger.info("Wallet user_id=%d debited by %d Rials (new balance: %d, ref: %s)", user_id, amount, wallet.balance, tx_ref)
        return True, "پرداخت هزینه سفارش با موفقیت از کیف پول کسر گردید.", tx

    @staticmethod
    def refund(
        session: Session,
        user_id: int,
        amount: int,
        order_tracking_code: Optional[str] = None,
        reason: str = "لغو سفارش توسط مشتری یا اپراتور",
        operator_id: Optional[int] = None
    ) -> Tuple[bool, str, Optional[WalletTransaction]]:
        """
        استرداد وجه سفارش لغوشده به کیف پول کاربر با ثبت تراکنش بستانکار.
        """
        if amount <= 0:
            return False, "مبلغ استرداد نامعتبر است.", None

        wallet = WalletService.get_or_create_wallet(session, user_id)
        tx_ref = f"REF-{order_tracking_code}" if order_tracking_code else generate_transaction_ref("REF")

        # بررسی ممانعت از بازگشت دوباره یک سفارش
        existing = session.query(WalletTransaction).filter_by(tracking_ref=tx_ref).first()
        if existing:
            logger.warning("Refund already processed for ref=%s", tx_ref)
            return True, "مبلغ این سفارش قبلاً به کیف پول مسترد شده است.", existing

        wallet.balance += amount
        wallet.updated_at = datetime.now(timezone.utc)

        note_str = f"استرداد وجه پرونده {order_tracking_code}: {reason}" if order_tracking_code else f"استرداد وجه: {reason}"
        tx = WalletTransaction(
            wallet_id=wallet.id,
            amount=amount,
            transaction_type="REFUND",
            status="APPROVED",
            tracking_ref=tx_ref,
            operator_id=operator_id,
            notes=note_str
        )
        session.add(tx)
        session.commit()
        session.refresh(tx)
        session.refresh(wallet)
        logger.info("Refund of %d Rials issued to wallet user_id=%d (new balance: %d, ref: %s)", amount, user_id, wallet.balance, tx_ref)
        return True, "مبلغ با موفقیت به کیف پول شما مسترد گردید.", tx

    @staticmethod
    def get_transaction_history(session: Session, user_id: int, limit: int = 10) -> List[WalletTransaction]:
        """دریافت آخرین تراکنش‌های مالی کیف پول کاربر."""
        wallet = WalletService.get_or_create_wallet(session, user_id)
        return (
            session.query(WalletTransaction)
            .filter_by(wallet_id=wallet.id)
            .order_by(WalletTransaction.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def format_wallet_card(wallet: Wallet, transactions: List[WalletTransaction]) -> str:
        """تولید کارت گزارش موجودی کیف پول و آخرین ریزتراکنش‌ها برای تلگرام."""
        balance_rial = wallet.balance
        balance_toman = balance_rial // 10

        status_text = "🔒 مسدود شده" if wallet.is_frozen else "🟢 فعال"

        lines = [
            "💳 <b>کیف پول و حساب مالی در کافی‌نت لیمو</b>\n",
            f"💰 <b>موجودی ریالی:</b> <code>{balance_rial:,}</code> ریال",
            f"💵 <b>معادل به تومان:</b> <code>{balance_toman:,}</code> تومان",
            f"📌 <b>وضعیت کیف پول:</b> {status_text}\n",
            "📜 <b>گردش تراکنش‌های اخیر:</b>"
        ]

        if not transactions:
            lines.append("<i>هنوز تراکنشی برای حساب شما ثبت نگردیده است.</i>")
        else:
            type_dict = {
                "TOPUP": ("➕ افزایش اعتبار", "🟢"),
                "ORDER_PAYMENT": ("➖ پرداخت سفارش", "🔴"),
                "REFUND": ("↩️ استرداد وجه", "🔵"),
                "ADJUSTMENT": ("⚖️ تعدیل حسابداری", "🟡")
            }
            for tx in transactions[:5]:
                label, icon = type_dict.get(tx.transaction_type, ("تراکنش", "⚪"))
                amt_str = f"{abs(tx.amount):,} ریال"
                dt = tx.created_at
                date_str = ""
                if dt:
                    jy, jm, jd, h, m = utc_to_jalali_datetime(dt)
                    date_str = f"{jy}/{jm:02d}/{jd:02d} {h:02d}:{m:02d}"

                lines.append(
                    f"{icon} <b>{label}:</b> <code>{amt_str}</code>\n"
                    f"   ▫️ شناسه: <code>{tx.tracking_ref}</code> | {date_str}\n"
                    f"   ▫️ شرح: <i>{tx.notes or '-'}</i>"
                )

        lines.append("\n<i>(کلیه تراکنش‌ها دارای شناسه یکتای پیگیری و غیرقابل تغییر می‌باشند)</i>")
        return "\n".join(lines)
