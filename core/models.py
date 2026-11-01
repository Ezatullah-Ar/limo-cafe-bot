"""
مدل‌های پایگاه داده رابطه‌ای سامانه «کافی نت لیمو».
تعریف‌شده با استفاده از نگاشت استاندارد SQLAlchemy 2.0 و سازگار با SQLite و PostgreSQL.
"""

from datetime import datetime, timezone
from typing import Optional, List, Any
from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    JSON
)
from sqlalchemy.orm import relationship
from core.database import Base


def _utc_now():
    """تولید زمان جاری استاندارد با آگاهی از منطقه زمانی UTC."""
    return datetime.now(timezone.utc)


class User(Base):
    """مدل کاربر سامانه (مشتری، اپراتور یا مدیر)."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    username = Column(String(255), nullable=True)
    phone_number = Column(String(50), nullable=True)
    role = Column(String(50), nullable=False, default="CUSTOMER")  # CUSTOMER | OPERATOR | ADMIN
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now, onupdate=_utc_now)

    # ارتباط با سفارشات و یادآورهای کاربر
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan", order_by="Reminder.target_date.asc()")
    wallet = relationship("Wallet", back_populates="user", uselist=False, cascade="all, delete-orphan")
    support_threads = relationship("SupportThread", back_populates="user", cascade="all, delete-orphan", order_by="SupportThread.created_at.desc()")

    def __repr__(self) -> str:
        return f"<User id={self.id} telegram_id={self.telegram_id} role={self.role}>"


class ServiceCategory(Base):
    """مدل دسته‌بندی خدمات کافینت لیمو."""
    __tablename__ = "service_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    order_priority = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now)

    # ارتباط یک به چند با آیتم‌های خدمت
    services = relationship(
        "ServiceItem",
        back_populates="category",
        cascade="all, delete-orphan",
        order_by="ServiceItem.order_priority"
    )

    def __repr__(self) -> str:
        return f"<ServiceCategory code={self.code} title={self.title}>"


class ServiceItem(Base):
    """مدل هر خدمت در کاتالوگ خدمات کافی نت لیمو."""
    __tablename__ = "service_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("service_categories.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    official_url = Column(String(500), nullable=True)
    required_fields = Column(JSON, nullable=False, default=dict)
    required_docs = Column(JSON, nullable=False, default=list)
    base_fee = Column(BigInteger, nullable=False, default=0)
    order_priority = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now, onupdate=_utc_now)

    # ارتباط معکوس با دسته‌بندی
    category = relationship("ServiceCategory", back_populates="services")
    orders = relationship("Order", back_populates="service")

    def __repr__(self) -> str:
        return f"<ServiceItem code={self.code} title={self.title}>"


class Order(Base):
    """مدل سفارش و پرونده متقاضی در سامانه کافی نت لیمو."""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tracking_code = Column(String(30), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    service_id = Column(Integer, ForeignKey("service_items.id"), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="PENDING", index=True)
    # وضعیت‌ها: PENDING, IN_REVIEW, NEED_INFO, APPROVED, COMPLETED, CANCELLED
    form_data = Column(JSON, nullable=False, default=dict)
    operator_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now, onupdate=_utc_now)

    # روابط
    user = relationship("User", back_populates="orders")
    service = relationship("ServiceItem", back_populates="orders")
    documents = relationship("OrderDocument", back_populates="order", cascade="all, delete-orphan")
    audit_logs = relationship("OrderAuditLog", back_populates="order", cascade="all, delete-orphan", order_by="OrderAuditLog.created_at.asc()")

    def __repr__(self) -> str:
        return f"<Order id={self.id} tracking_code={self.tracking_code} status={self.status}>"


class OrderDocument(Base):
    """مدل فایل‌ها و مدارک پیوست‌شده به پرونده."""
    __tablename__ = "order_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    file_id = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=True)
    file_type = Column(String(50), nullable=False, default="DOCUMENT")  # PHOTO | DOCUMENT
    file_size = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now)

    order = relationship("Order", back_populates="documents")

    def __repr__(self) -> str:
        return f"<OrderDocument id={self.id} file_name={self.file_name}>"


class OrderAuditLog(Base):
    """ثبت تاریخچه تغییر وضعیت و رویدادهای پرونده (Audit Trail)."""
    __tablename__ = "order_audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    actor_id = Column(BigInteger, nullable=False)  # شناسه تلگرام شخص تغییردهنده (مشتری یا اپراتور)
    from_status = Column(String(50), nullable=False)
    to_status = Column(String(50), nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now)

    order = relationship("Order", back_populates="audit_logs")

    def __repr__(self) -> str:
        return f"<OrderAuditLog order_id={self.order_id} {self.from_status}->{self.to_status}>"


class Reminder(Base):
    """مدل یادآورهای هوشمند مهلت‌ها بر مبنای تقویم شمسی و منطقه زمانی تهران."""
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    shamsi_date = Column(String(30), nullable=False)
    target_date = Column(DateTime(timezone=True), nullable=False, index=True)
    is_sent = Column(Boolean, nullable=False, default=False, index=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now)

    user = relationship("User", back_populates="reminders")

    def __repr__(self) -> str:
        return f"<Reminder id={self.id} user_id={self.user_id} title={self.title} date={self.shamsi_date} sent={self.is_sent}>"


class WebsiteMonitor(Base):
    """مدل اطلاعات و تنظیمات پایش هوشمند سایت‌های هدف."""
    __tablename__ = "website_monitors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    check_interval_minutes = Column(Integer, nullable=False, default=15)
    last_checked_at = Column(DateTime(timezone=True), nullable=True)

    # دو بعد تفکیک‌شده بر اساس اصل حاکم بر پایش سایت‌ها (AGENTS.md)
    uptime_status = Column(String(50), nullable=False, default="UNKNOWN")  # UP | DOWN | DEGRADED | UNKNOWN
    service_status = Column(String(50), nullable=False, default="UNKNOWN")  # OPEN | CLOSED | UNKNOWN

    last_response_time_ms = Column(Integer, nullable=True)
    last_http_code = Column(Integer, nullable=True)
    status_message = Column(Text, nullable=True)
    detection_rule = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now, onupdate=_utc_now)

    logs = relationship("MonitorLog", back_populates="monitor", cascade="all, delete-orphan", order_by="MonitorLog.checked_at.desc()")

    def __repr__(self) -> str:
        return f"<WebsiteMonitor code={self.code} uptime={self.uptime_status} service={self.service_status}>"


class MonitorLog(Base):
    """مدل تاریخچه نتایج بررسی‌های ادواری پایش (Audit Log)."""
    __tablename__ = "monitor_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    monitor_id = Column(Integer, ForeignKey("website_monitors.id", ondelete="CASCADE"), nullable=False, index=True)
    checked_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now)
    uptime_status = Column(String(50), nullable=False)
    service_status = Column(String(50), nullable=False)
    http_code = Column(Integer, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)

    monitor = relationship("WebsiteMonitor", back_populates="logs")

    def __repr__(self) -> str:
        return f"<MonitorLog monitor_id={self.monitor_id} uptime={self.uptime_status} service={self.service_status}>"


class Wallet(Base):
    """مدل کیف پول اختصاصی مشتری در سامانه کافی نت لیمو."""
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    balance = Column(BigInteger, nullable=False, default=0)  # موجودی به ریال
    is_frozen = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now, onupdate=_utc_now)

    user = relationship("User", back_populates="wallet")
    transactions = relationship("WalletTransaction", back_populates="wallet", cascade="all, delete-orphan", order_by="WalletTransaction.created_at.desc()")

    def __repr__(self) -> str:
        return f"<Wallet user_id={self.user_id} balance={self.balance} is_frozen={self.is_frozen}>"


class WalletTransaction(Base):
    """مدل تراکنش‌های مالی و گردش حساب کیف پول."""
    __tablename__ = "wallet_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(BigInteger, nullable=False)  # مبلغ به ریال (مثبت برای واریز، منفی برای برداشت)
    transaction_type = Column(String(50), nullable=False, index=True)  # TOPUP | ORDER_PAYMENT | REFUND | ADJUSTMENT
    status = Column(String(50), nullable=False, default="PENDING", index=True)  # PENDING | APPROVED | REJECTED
    tracking_ref = Column(String(64), unique=True, nullable=False, index=True)  # شناسه پیگیری یکتای مالی
    receipt_file_id = Column(String(255), nullable=True)  # شناسه فایل فیش واریزی در تلگرام
    operator_id = Column(BigInteger, nullable=True)  # شناسه تلگرام اپراتور تاییدکننده
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now, onupdate=_utc_now)

    wallet = relationship("Wallet", back_populates="transactions")

    def __repr__(self) -> str:
        return f"<WalletTransaction ref={self.tracking_ref} amount={self.amount} type={self.transaction_type} status={self.status}>"


class SupportThread(Base):
    """مدل تیکت یا رشته گفتگوی زنده مشتری با اپراتور."""
    __tablename__ = "support_threads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="NEW", index=True)  # NEW | PENDING_SUPPORT | PENDING_CUSTOMER | CLOSED
    assigned_operator_id = Column(BigInteger, nullable=True, index=True)
    related_order_id = Column(Integer, ForeignKey("orders.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now, onupdate=_utc_now)

    user = relationship("User", back_populates="support_threads")
    order = relationship("Order")
    messages = relationship("SupportMessage", back_populates="thread", cascade="all, delete-orphan", order_by="SupportMessage.created_at.asc()")

    def __repr__(self) -> str:
        return f"<SupportThread id={self.id} user_id={self.user_id} status={self.status}>"


class SupportMessage(Base):
    """مدل پیام‌های تبادل‌شده در گفتگوی پشتیبانی."""
    __tablename__ = "support_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    thread_id = Column(Integer, ForeignKey("support_threads.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_role = Column(String(50), nullable=False, default="CUSTOMER")  # CUSTOMER | OPERATOR
    sender_id = Column(BigInteger, nullable=False)  # شناسه تلگرام ارسال‌کننده
    message_text = Column(Text, nullable=True)
    file_id = Column(String(255), nullable=True)
    file_type = Column(String(50), nullable=True)  # PHOTO | DOCUMENT | VOICE
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now)

    thread = relationship("SupportThread", back_populates="messages")

    def __repr__(self) -> str:
        return f"<SupportMessage id={self.id} thread_id={self.thread_id} sender_role={self.sender_role}>"


class SeasonalCampaign(Base):
    """مدل ثبت‌نام‌های مقطعی، دوره‌ای و زمان‌دار سامانه."""
    __tablename__ = "seasonal_campaigns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    start_at = Column(DateTime(timezone=True), nullable=False)
    end_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50), nullable=False, default="DRAFT", index=True)  # DRAFT | SCHEDULED | ACTIVE | EXPIRING_SOON | ENDED | SUSPENDED
    base_fee = Column(BigInteger, nullable=False, default=0)
    form_schema = Column(JSON, nullable=False, default=dict)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now, onupdate=_utc_now)

    def __repr__(self) -> str:
        return f"<SeasonalCampaign code={self.code} title={self.title} status={self.status}>"


class CommunicationChannel(Base):
    """مدل کانال‌ها و راه‌های ارتباطی و شبکه‌های اجتماعی کافی نت لیمو."""
    __tablename__ = "communication_channels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(50), unique=True, nullable=False, index=True)  # PHONE | TELEGRAM | EITAA | RUBIKA | BALE | INSTAGRAM
    title = Column(String(100), nullable=False)
    value = Column(String(255), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    order_priority = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now, onupdate=_utc_now)

    def __repr__(self) -> str:
        return f"<CommunicationChannel key={self.key} active={self.is_active}>"


class SystemSetting(Base):
    """مدل تنظیمات سراسری سیستم (هزینه شاهد مسکن، وضعیت انیمیشن و ...)."""
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now, onupdate=_utc_now)

    def __repr__(self) -> str:
        return f"<SystemSetting key={self.key} value={self.value}>"
