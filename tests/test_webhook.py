"""
آزمون‌های خودکار ماژول وب‌هوک و پاسخ مستقیم تلگرام (bot/webhook.py)
"""

import unittest
from core.config import Settings
from core.security import AccessControl
from core.throttling import Throttler
from core.database import DatabaseManager
from services.catalog import CatalogService
from bot.dispatcher import BotDispatcher
from bot.webhook import handle_webhook_payload, parse_telegram_update, format_telegram_reply_markup
from bot.models import KeyboardButton


class TestWebhook(unittest.TestCase):
    """مجموعه آزمون‌های راستی‌آزمایی پروتکل Webhook و تولید پاسخ‌های Webhook-Reply."""

    def setUp(self):
        self.admin_id = 123456789
        self.user_id = 987654321
        self.settings = Settings(admin_id=self.admin_id)
        self.access_control = AccessControl(self.settings)
        self.throttler = Throttler(rate_limit_seconds=0.0, max_burst=1000)

        self.db_manager = DatabaseManager("sqlite:///:memory:")
        self.db_manager.init_db()

        with self.db_manager.get_session() as session:
            CatalogService.seed_initial_catalog(session)

        self.dispatcher = BotDispatcher(
            access_control=self.access_control,
            throttler=self.throttler,
            db_manager=self.db_manager
        )

    def tearDown(self):
        self.db_manager.drop_db()

    def test_format_telegram_reply_markup(self):
        """آزمون تبدیل ماتریس دکمه‌های شیشه‌ای به قالب رسمی inline_keyboard تلگرام."""
        markup = [
            [KeyboardButton(text="دکمه ۱", callback_data="cb_1"), KeyboardButton(text="دکمه ۲", callback_data="cb_2")],
            [KeyboardButton(text="بازگشت", callback_data="back")]
        ]
        res = format_telegram_reply_markup(markup)
        self.assertIsNotNone(res)
        self.assertIn("inline_keyboard", res)
        self.assertEqual(len(res["inline_keyboard"]), 2)
        self.assertEqual(res["inline_keyboard"][0][0]["text"], "دکمه ۱")
        self.assertEqual(res["inline_keyboard"][0][0]["callback_data"], "cb_1")

    def test_secret_token_security_enforcement(self):
        """آزمون مسدودسازی درخواست‌های وب‌هوک فاقد هدر محرمانه معتبر (Secret Token)."""
        payload = {
            "update_id": 1,
            "message": {
                "message_id": 10,
                "from": {"id": self.user_id, "first_name": "تستر"},
                "chat": {"id": self.user_id},
                "text": "/start"
            }
        }
        # حالت ۱: توکن اشتباه ارسال شده است
        status, resp = handle_webhook_payload(
            payload=payload,
            dispatcher=self.dispatcher,
            configured_secret="my_super_secret_token",
            received_secret="wrong_token"
        )
        self.assertEqual(status, 403)
        self.assertFalse(resp["ok"])

        # حالت ۲: توکن صحیح ارسال شده است
        status_ok, resp_ok = handle_webhook_payload(
            payload=payload,
            dispatcher=self.dispatcher,
            configured_secret="my_super_secret_token",
            received_secret="my_super_secret_token"
        )
        self.assertEqual(status_ok, 200)
        self.assertEqual(resp_ok["method"], "sendMessage")

    def test_webhook_message_flow_webhook_reply(self):
        """آزمون پردازش دستور /start از طریق وب‌هوک و تولید خروجی sendMessage متناظر."""
        payload = {
            "update_id": 55,
            "message": {
                "message_id": 101,
                "from": {"id": self.user_id, "first_name": "سارا", "username": "sara_t"},
                "chat": {"id": self.user_id},
                "text": "/start"
            }
        }
        status, reply = handle_webhook_payload(payload=payload, dispatcher=self.dispatcher)

        self.assertEqual(status, 200)
        self.assertEqual(reply["method"], "sendMessage")
        self.assertEqual(reply["chat_id"], self.user_id)
        self.assertIn("کافی نت لیمو", reply["text"])
        self.assertIn("inline_keyboard", reply["reply_markup"])

    def test_webhook_callback_query_flow(self):
        """آزمون پردازش کلیک روی دکمه فهرست خدمات از طریق وب‌هوک."""
        payload = {
            "update_id": 56,
            "callback_query": {
                "id": "cb_query_999",
                "from": {"id": self.user_id, "first_name": "سارا"},
                "message": {
                    "message_id": 101,
                    "from": {"id": self.user_id, "first_name": "سارا"},
                    "chat": {"id": self.user_id},
                    "text": "منوی اصلی"
                },
                "data": "services_list"
            }
        }
        status, reply = handle_webhook_payload(payload=payload, dispatcher=self.dispatcher)

        self.assertEqual(status, 200)
        self.assertEqual(reply["method"], "sendMessage")
        self.assertIn("فهرست خدمات فعال", reply["text"])
        self.assertIn("inline_keyboard", reply["reply_markup"])

    def test_unknown_update_ignored_safely(self):
        """آزمون نادیده گرفتن امن سایر انواع آپدیت‌ها (مانند ویرایش پیام، عضویت و ...) با کد 200."""
        payload = {"update_id": 57, "channel_post": {"message_id": 99}}
        status, reply = handle_webhook_payload(payload=payload, dispatcher=self.dispatcher)

        self.assertEqual(status, 200)
        self.assertTrue(reply.get("ok"))
        self.assertEqual(reply.get("status"), "ignored")


if __name__ == "__main__":
    unittest.main()
