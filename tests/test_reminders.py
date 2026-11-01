"""
آزمون‌های خودکار ماژول یادآورهای هوشمند تقویمی مهلت‌ها (Phase 7: Reminders & Calendar Workflow)
"""

import unittest
from datetime import datetime, timezone, timedelta
from core.config import Settings
from core.security import AccessControl
from core.throttling import Throttler
from core.database import DatabaseManager
from services.catalog import CatalogService
from services.reminders import ReminderService
from core.calendar import jalali_to_utc_datetime, parse_jalali_date
from bot.models import TelegramUser, IncomingMessage, CallbackQuery
from bot.dispatcher import BotDispatcher
from bot.fsm import FSMManager


class TestReminders(unittest.TestCase):
    """مجموعه آزمون‌های جامع ایجاد، استعلام، حذف، پردازش سررسید و تعامل FSM یادآورها."""

    def setUp(self):
        self.user1_id = 111222333
        self.user2_id = 444555666

        self.user1 = TelegramUser(id=self.user1_id, first_name="متقاضی اول", username="user_one")
        self.user2 = TelegramUser(id=self.user2_id, first_name="متقاضی دوم", username="user_two")

        self.settings = Settings(admin_id=999999999)
        self.access_control = AccessControl(self.settings)
        self.throttler = Throttler(rate_limit_seconds=0.0, max_burst=1000)
        self.fsm_manager = FSMManager()

        self.db_manager = DatabaseManager("sqlite:///:memory:")
        self.db_manager.init_db()

        # ثبت کاربران در دیتابیس آزمایشی
        with self.db_manager.get_session() as session:
            CatalogService.seed_initial_catalog(session)
            self.db_u1 = CatalogService.get_or_create_user(session, self.user1_id, "متقاضی اول")
            self.db_u2 = CatalogService.get_or_create_user(session, self.user2_id, "متقاضی دوم")
            self.u1_db_id = self.db_u1.id
            self.u2_db_id = self.db_u2.id

        self.dispatcher = BotDispatcher(
            access_control=self.access_control,
            throttler=self.throttler,
            db_manager=self.db_manager,
            fsm_manager=self.fsm_manager
        )

    def tearDown(self):
        self.db_manager.drop_db()

    def test_create_reminder_success(self):
        """آزمون ایجاد موفق یادآور با تاریخ آینده و بررسی فیلدهای ذخیره‌شده."""
        # زمان مرجع: ۴ آبان ۱۴۰۵
        now_mock = jalali_to_utc_datetime(1405, 8, 4, 12, 0)
        with self.db_manager.get_session() as session:
            reminder = ReminderService.create_reminder(
                session=session,
                user_id=self.u1_db_id,
                title="مهلت ثبت‌نام کنکور کارشناسی ارشد",
                shamsi_date="1405/08/15",
                target_hour=9,
                now_utc=now_mock
            )
            self.assertIsNotNone(reminder.id)
            self.assertEqual(reminder.shamsi_date, "1405/08/15")
            self.assertFalse(reminder.is_sent)
            self.assertEqual(reminder.title, "مهلت ثبت‌نام کنکور کارشناسی ارشد")

    def test_create_reminder_past_date_rejected(self):
        """آزمون مهار و رد ثبت یادآور برای تاریخی که در گذشته قرار دارد."""
        # زمان مرجع: ۱۰ آبان ۱۴۰۵
        now_mock = jalali_to_utc_datetime(1405, 8, 10, 12, 0)
        with self.db_manager.get_session() as session:
            with self.assertRaises(ValueError) as ctx:
                ReminderService.create_reminder(
                    session=session,
                    user_id=self.u1_db_id,
                    title="آزمون تاریخ گذشته",
                    shamsi_date="1405/08/05",  # ۵ روز قبل از زمان جاری
                    now_utc=now_mock
                )
            self.assertIn("گذشته", str(ctx.exception))

    def test_user_reminders_isolation_and_delete(self):
        """آزمون ایزولاسیون اطلاعات کاربران و اعتبارسنجی مالکیت هنگام حذف."""
        now_mock = jalali_to_utc_datetime(1405, 8, 1, 10, 0)
        with self.db_manager.get_session() as session:
            r1 = ReminderService.create_reminder(session, self.u1_db_id, "یادآور ۱ کاربر ۱", "1405/08/10", now_utc=now_mock)
            r2 = ReminderService.create_reminder(session, self.u1_db_id, "یادآور ۲ کاربر ۱", "1405/08/20", now_utc=now_mock)
            r3 = ReminderService.create_reminder(session, self.u2_db_id, "یادآور ۱ کاربر ۲", "1405/08/15", now_utc=now_mock)

            u1_list = ReminderService.get_user_reminders(session, self.u1_db_id)
            self.assertEqual(len(u1_list), 2)
            u2_list = ReminderService.get_user_reminders(session, self.u2_db_id)
            self.assertEqual(len(u2_list), 1)

            # تلاش کاربر ۲ برای حذف یادآور کاربر ۱ (باید شکست بخورد)
            deleted_by_intruder = ReminderService.delete_reminder(session, r1.id, user_id=self.u2_db_id)
            self.assertFalse(deleted_by_intruder)

            # حذف موفق توسط خود کاربر ۱
            deleted_by_owner = ReminderService.delete_reminder(session, r1.id, user_id=self.u1_db_id)
            self.assertTrue(deleted_by_owner)

            remaining = ReminderService.get_user_reminders(session, self.u1_db_id)
            self.assertEqual(len(remaining), 1)
            self.assertEqual(remaining[0].id, r2.id)

    def test_due_reminders_processing_and_idempotency(self):
        """آزمون پردازش سررسید یادآورها و تضمین قطعی عدم ارسال تکراری (Idempotency)."""
        # تنظیم یادآور برای ۱۰ آبان ساعت ۹ صبح
        target_utc = jalali_to_utc_datetime(1405, 8, 10, 9, 0)
        with self.db_manager.get_session() as session:
            ReminderService.create_reminder(
                session=session,
                user_id=self.u1_db_id,
                title="آخرین مهلت تاییدیه تحصیلی",
                shamsi_date="1405/08/10",
                target_hour=9,
                now_utc=jalali_to_utc_datetime(1405, 8, 1, 8, 0)
            )

        # ۱. استعلام پیش از موعد (مثلاً ۹ آبان) -> نباید هیچ اعلانی تولید شود
        time_before = jalali_to_utc_datetime(1405, 8, 9, 23, 59)
        with self.db_manager.get_session() as session:
            due_before = ReminderService.process_due_reminders(session, time_before)
            self.assertEqual(len(due_before), 0)

        # ۲. رسیدن زمان موعد (۱۰ آبان ساعت ۰۹:۰۱) -> باید اعلان ارسال شود
        time_due = jalali_to_utc_datetime(1405, 8, 10, 9, 1)
        with self.db_manager.get_session() as session:
            due_now = ReminderService.process_due_reminders(session, time_due)
            self.assertEqual(len(due_now), 1)
            telegram_id, alert_text = due_now[0]
            self.assertEqual(telegram_id, self.user1_id)
            self.assertIn("آخرین مهلت تاییدیه تحصیلی", alert_text)
            self.assertIn("10 آبان 1405", alert_text)

        # ۳. استعلام مجدد در دقایق یا ساعات بعدی -> تضمین عدم ارسال مجدد
        time_after = jalali_to_utc_datetime(1405, 8, 10, 10, 0)
        with self.db_manager.get_session() as session:
            due_after = ReminderService.process_due_reminders(session, time_after)
            self.assertEqual(len(due_after), 0)

    def test_bot_fsm_reminder_creation_and_cancel_flow(self):
        """آزمون تعاملی ثبت یادآور چندمرحله‌ای از طریق بات و دیسپچر."""
        # گام ۱: کلیک روی دکمه تنظیم یادآور جدید
        cb_new = CallbackQuery(id="cb_rem_new", from_user=self.user1, data="rem_new")
        resp1 = self.dispatcher.dispatch_callback(cb_new)
        self.assertIn("عنوان یا موضوع یادآور", resp1.text)

        state = self.fsm_manager.get_state(self.user1_id)
        self.assertIsNotNone(state)
        self.assertEqual(state.step, "REMINDER_TITLE")

        # گام ۲: ارسال عنوان یادآور
        msg_title = IncomingMessage(
            message_id=201,
            from_user=self.user1,
            text="مهلت انتخاب واحد دانشگاه پیام نور"
        )
        resp2 = self.dispatcher.dispatch(msg_title)
        self.assertIn("تاریخ سررسید شمسی", resp2.text)

        state2 = self.fsm_manager.get_state(self.user1_id)
        self.assertEqual(state2.step, "REMINDER_DATE")
        self.assertEqual(state2.reminder_title, "مهلت انتخاب واحد دانشگاه پیام نور")

        # گام ۳: ارسال تاریخ نامعتبر (باید خطا دهد و کاربر در FSM باقی بماند)
        msg_bad_date = IncomingMessage(
            message_id=202,
            from_user=self.user1,
            text="1405/13/45"
        )
        resp3 = self.dispatcher.dispatch(msg_bad_date)
        self.assertIn("خطا در تاریخ ورودی", resp3.text)
        self.assertEqual(self.fsm_manager.get_state(self.user1_id).step, "REMINDER_DATE")

        # گام ۴: ارسال تاریخ صحیح آینده (مثلاً سال 1406)
        msg_good_date = IncomingMessage(
            message_id=203,
            from_user=self.user1,
            text="1406/02/15"
        )
        resp4 = self.dispatcher.dispatch(msg_good_date)
        self.assertIn("با موفقیت ثبت گردید", resp4.text)
        self.assertIn("مهلت انتخاب واحد دانشگاه پیام نور", resp4.text)
        self.assertIsNone(self.fsm_manager.get_state(self.user1_id))

        # بررسی پایگاه داده
        with self.db_manager.get_session() as session:
            reminders = ReminderService.get_user_reminders(session, self.u1_db_id)
            self.assertEqual(len(reminders), 1)
            self.assertEqual(reminders[0].shamsi_date, "1406/02/15")

    def test_bot_reminders_list_and_delete_flow(self):
        """آزمون مشاهده لیست یادآورهای کاربر در بات و حذف از طریق دکمه شیشه‌ای."""
        # ایجاد یک یادآور اولیه برای کاربر
        with self.db_manager.get_session() as session:
            rem = ReminderService.create_reminder(
                session=session,
                user_id=self.u1_db_id,
                title="ارسال تاییدیه تحصیلی به دارالترجمه",
                shamsi_date="1406/05/10"
            )
            rem_id = rem.id

        # کلیک روی دکمه مشاهده یادآورها (rem_list)
        cb_list = CallbackQuery(id="cb_rem_list", from_user=self.user1, data="rem_list")
        resp_list = self.dispatcher.dispatch_callback(cb_list)
        self.assertIn("فهرست یادآورهای فعال شما", resp_list.text)
        self.assertIn("ارسال تاییدیه تحصیلی به دارالترجمه", resp_list.text)

        # کلیک روی دکمه حذف
        cb_del = CallbackQuery(id="cb_del", from_user=self.user1, data=f"rem_del_{rem_id}")
        resp_del = self.dispatcher.dispatch_callback(cb_del)
        self.assertIn("با موفقیت حذف گردید", resp_del.text)

        # بررسی حذف از دیتابیس
        with self.db_manager.get_session() as session:
            active = ReminderService.get_user_reminders(session, self.u1_db_id)
            self.assertEqual(len(active), 0)


if __name__ == "__main__":
    unittest.main()
