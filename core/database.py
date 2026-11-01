"""
ماژول اتصال و مدیریت پایگاه داده سامانه «کافی نت لیمو».
این ماژول از SQLAlchemy 2.0 استفاده می‌کند و با SQLite (در حالت بهینه WAL) و PostgreSQL
کاملاً سازگار و قابل حمل است.
"""

import os
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# کلاس پایه مدل‌های رابطه‌ای
Base = declarative_base()


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    """
    اعمال تنظیمات کارایی و یکپارچگی ارجاعی برای SQLite:
    - فعال‌سازی کلیدهای خارجی (Foreign Keys)
    - فعال‌سازی حالت WAL جهت نوشتن و خواندن همزمان بدون قفل
    - تنظیم مهلت قفل (busy_timeout) به ۵ ثانیه
    """
    # فقط در صورت استفاده از اتصال SQLite اجرا شود
    if dbapi_connection.__class__.__module__.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()


class DatabaseManager:
    """مدیریت موتور پایگاه داده و ایجاد سشن‌های تراکنشی."""

    def __init__(self, database_url: str):
        self.database_url = database_url
        
        # اطمینان از وجود پوشه والد در صورت استفاده از مسیر محلی SQLite
        if database_url.startswith("sqlite:///") and not database_url.startswith("sqlite:///:memory:"):
            db_path = database_url.replace("sqlite:///", "")
            parent_dir = os.path.dirname(db_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)

        # ساخت موتور SQLAlchemy
        connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
        self.engine = create_engine(
            database_url,
            connect_args=connect_args,
            echo=False
        )
        self.session_factory = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )

    def init_db(self) -> None:
        """ساخت تمامی جداول تعریف‌شده در مدل‌ها به صورت خودکار و عاری از خطا."""
        Base.metadata.create_all(bind=self.engine)

    def drop_db(self) -> None:
        """حذف تمامی جداول (صرفاً برای بازسازی در محیط‌های تست ایزوله)."""
        Base.metadata.drop_all(bind=self.engine)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """مدیریت تراکنش پایگاه داده با بستن و رول‌بک خودکار در صورت وقوع خطا."""
        session: Session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
