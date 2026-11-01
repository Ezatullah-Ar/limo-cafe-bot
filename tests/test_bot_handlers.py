"""
آزمون‌های خودکار هندلرها و دیسپچر ربات (bot/handlers.py و bot/dispatcher.py)
"""

import unittest
from core.config import Settings
from core.security import AccessControl
from bot.models import TelegramUser, IncomingMessage
from bot.dispatcher import BotDispatcher
from bot.handlers import WELCOME_TEXT, ADMIN_PANEL_TEXT, ACCESS_DENIED_TEXT


class TestBotHandlers(unittest.TestCase):
    """مجموعه آزمون‌های رفتار پیام‌ها و مسیریابی دیسپچر ربات."""

    def setUp(self):
        self.admin_id = 123456789
        self.regular_user_id = 987654321

        self.admin_user = TelegramUser(
            id=self.admin_id,
            first_name="مدیر",
            username="admin_user"
        )
        self.regular_user = TelegramUser(
            id=self.regular_user_id,
            first_name="کاربر عادی",
            username="regular_user"
        )

        self.settings = Settings(admin_id=self.admin_id)
        self.access_control = AccessControl(self.settings)
        self.dispatcher = BotDispatcher(self.access_control)

    def test_start_command(self):
        """آزمون دستور /start: نمایش متن خوش‌آمدگویی و کیبورد منوی اصلی."""
        msg = IncomingMessage(
            message_id=1,
            from_user=self.regular_user,
            text="/start"
        )
        response = self.dispatcher.dispatch(msg)

        self.assertEqual(response.chat_id, self.regular_user_id)
        self.assertIn("کافی نت لیمو", response.text)
        self.assertEqual(response.text, WELCOME_TEXT)
        self.assertIsNotNone(response.reply_markup)

        # بررسی وجود دکمه‌های اصلی
        button_texts = [btn.text for row in response.reply_markup for btn in row]
        self.assertIn("📋 فهرست خدمات", button_texts)
        self.assertIn("🔍 پیگیری سفارش", button_texts)
        self.assertIn("⏰ یادآورها", button_texts)
        self.assertIn("📞 ارتباط با اپراتور", button_texts)

    def test_admin_command_unauthorized(self):
        """آزمون دستور /admin توسط کاربر غیرمجاز: رد دسترسی و عدم نشت اطلاعات پنل."""
        msg = IncomingMessage(
            message_id=2,
            from_user=self.regular_user,
            text="/admin"
        )
        response = self.dispatcher.dispatch(msg)

        self.assertEqual(response.chat_id, self.regular_user_id)
        self.assertEqual(response.text, ACCESS_DENIED_TEXT)
        self.assertIsNone(response.reply_markup)
        self.assertNotIn("پنل مدیریت", response.text)

    def test_admin_command_authorized(self):
        """آزمون دستور /admin توسط مدیر احرازشده: باز شدن موفق پنل مدیریت."""
        msg = IncomingMessage(
            message_id=3,
            from_user=self.admin_user,
            text="/admin"
        )
        response = self.dispatcher.dispatch(msg)

        self.assertEqual(response.chat_id, self.admin_id)
        self.assertEqual(response.text, ADMIN_PANEL_TEXT)
        self.assertIsNotNone(response.reply_markup)

        admin_button_texts = [btn.text for row in response.reply_markup for btn in row]
        self.assertIn("📊 آمار و وضعیت سیستم", admin_button_texts)
        self.assertIn("📂 کارتابل درخواست‌ها", admin_button_texts)

    def test_command_with_bot_username_suffix(self):
        """آزمون پردازش دستور همراه با شناسه بات (نظیر /start@LimoBot)."""
        msg = IncomingMessage(
            message_id=4,
            from_user=self.regular_user,
            text="/start@LimoBot"
        )
        response = self.dispatcher.dispatch(msg)
        self.assertEqual(response.text, WELCOME_TEXT)

    def test_unknown_command(self):
        """آزمون پیام یا دستور نامعتبر: ارسال پیام راهنمای بازگشت به /start."""
        msg = IncomingMessage(
            message_id=5,
            from_user=self.regular_user,
            text="سلام نامفهوم"
        )
        response = self.dispatcher.dispatch(msg)
        self.assertIn("/start", response.text)

    def test_empty_message_handling(self):
        """آزمون پردازش پیام با متن خالی یا None."""
        msg = IncomingMessage(
            message_id=6,
            from_user=self.regular_user,
            text=None
        )
        response = self.dispatcher.dispatch(msg)
        self.assertIn("/start", response.text)


if __name__ == "__main__":
    unittest.main()
