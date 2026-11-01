"""
آزمون‌های خودکار ماژول لانگ‌پولینگ محلی (bot/polling.py و run_local.py)
سامانه «کافی نت لیمو».
راستی‌آزمایی کلاینت تلگرام، حلقه دریافت پیام‌ها (Polling Runner) و پردازش یکپارچه آپدیت‌ها.
"""

import unittest
import json
import urllib.error
from unittest.mock import MagicMock
from core.config import Settings
from core.security import AccessControl
from core.throttling import Throttler
from core.database import DatabaseManager
from services.catalog import CatalogService
from bot.models import KeyboardButton, OutgoingResponse
from bot.dispatcher import BotDispatcher
from bot.polling import TelegramClient, PollingRunner
from run_local import load_env_file


class TestPolling(unittest.TestCase):
    """مجموعه آزمون‌های کلاینت تلگرام و رانر لانگ‌پولینگ."""

    def setUp(self):
        self.admin_id = 111222333
        self.user_id = 444555666
        self.token = "123456789:ABCdefGhI_mock_token"

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

        self.mock_opener = MagicMock()
        self.client = TelegramClient(self.token, opener=self.mock_opener)

    def tearDown(self):
        self.db_manager.drop_db()

    def test_client_call_method_success(self):
        """آزمون اجرای موفق متد در کلاینت تلگرام با بازگشت داده‌های JSON."""
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"ok": True, "result": {"id": 123}}).encode("utf-8")
        self.mock_opener.open.return_value.__enter__.return_value = mock_resp

        res = self.client.call_method("getMe")
        self.assertTrue(res["ok"])
        self.assertEqual(res["result"]["id"], 123)

    def test_client_get_updates(self):
        """آزمون دریافت آپدیت‌ها و تنظیم offset در درخواست پولینگ."""
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "ok": True,
            "result": [
                {"update_id": 501, "message": {"message_id": 1, "from": {"id": self.user_id, "first_name": "تستر"}, "text": "/start"}}
            ]
        }).encode("utf-8")
        self.mock_opener.open.return_value.__enter__.return_value = mock_resp

        updates = self.client.get_updates(offset=500, timeout=10)
        self.assertEqual(len(updates), 1)
        self.assertEqual(updates[0]["update_id"], 501)

    def test_polling_runner_processes_message_and_advances_offset(self):
        """آزمون پردازش کامل پیام ورودی در حلقه پولینگ و پیشروی خودکار last_offset."""
        mock_resp_updates = MagicMock()
        mock_resp_updates.read.return_value = json.dumps({
            "ok": True,
            "result": [
                {
                    "update_id": 100,
                    "message": {
                        "message_id": 10,
                        "from": {"id": self.user_id, "first_name": "کاربر ۱"},
                        "text": "/start"
                    }
                }
            ]
        }).encode("utf-8")

        mock_resp_send = MagicMock()
        mock_resp_send.read.return_value = json.dumps({"ok": True, "result": {"message_id": 99}}).encode("utf-8")

        # بازگشت خروجی getUpdates و سپس sendMessage
        self.mock_opener.open.return_value.__enter__.side_effect = [mock_resp_updates, mock_resp_send]

        runner = PollingRunner(
            bot_token=self.token,
            dispatcher=self.dispatcher,
            db_manager=self.db_manager,
            client=self.client
        )

        processed = runner.run_once()
        self.assertEqual(processed, 1)
        self.assertEqual(runner.last_offset, 101)

    def test_polling_runner_processes_callback_query(self):
        """آزمون پردازش کلیک روی دکمه شیشه‌ای و ارسال تاییدیه answerCallbackQuery."""
        mock_resp_updates = MagicMock()
        mock_resp_updates.read.return_value = json.dumps({
            "ok": True,
            "result": [
                {
                    "update_id": 200,
                    "callback_query": {
                        "id": "cb_query_99",
                        "from": {"id": self.user_id, "first_name": "کاربر"},
                        "data": "services_list"
                    }
                }
            ]
        }).encode("utf-8")

        mock_resp_ans = MagicMock()
        mock_resp_ans.read.return_value = json.dumps({"ok": True, "result": True}).encode("utf-8")

        mock_resp_send = MagicMock()
        mock_resp_send.read.return_value = json.dumps({"ok": True, "result": {"message_id": 100}}).encode("utf-8")

        self.mock_opener.open.return_value.__enter__.side_effect = [
            mock_resp_updates,
            mock_resp_ans,
            mock_resp_send
        ]

        runner = PollingRunner(
            bot_token=self.token,
            dispatcher=self.dispatcher,
            db_manager=self.db_manager,
            client=self.client
        )

        processed = runner.run_once()
        self.assertEqual(processed, 1)
        self.assertEqual(runner.last_offset, 201)

    def test_polling_runner_sends_secondary_notification(self):
        """آزمون ارسال خودکار پیام آگاه‌سازی مشتری (Notification) در خلال اقدامات اپراتور."""
        mock_resp_updates = MagicMock()
        mock_resp_updates.read.return_value = json.dumps({
            "ok": True,
            "result": [
                {
                    "update_id": 300,
                    "message": {
                        "message_id": 5,
                        "from": {"id": self.admin_id, "first_name": "مدیر"},
                        "text": "/stats"
                    }
                }
            ]
        }).encode("utf-8")

        mock_resp_send = MagicMock()
        mock_resp_send.read.return_value = json.dumps({"ok": True, "result": {"message_id": 101}}).encode("utf-8")

        self.mock_opener.open.return_value.__enter__.side_effect = [mock_resp_updates, mock_resp_send]

        runner = PollingRunner(
            bot_token=self.token,
            dispatcher=self.dispatcher,
            db_manager=self.db_manager,
            client=self.client
        )

        processed = runner.run_once()
        self.assertEqual(processed, 1)
        self.assertEqual(runner.last_offset, 301)

    def test_polling_runner_handles_network_error_gracefully(self):
        """آزمون مقاومت رانر در برابر خطای شبکه و عدم بروز شکست غیرمنتظره."""
        self.mock_opener.open.side_effect = urllib.error.URLError("Network unreachable")

        runner = PollingRunner(
            bot_token=self.token,
            dispatcher=self.dispatcher,
            db_manager=self.db_manager,
            client=self.client
        )

        processed = runner.run_once()
        self.assertEqual(processed, 0)
        self.assertIsNone(runner.last_offset)


if __name__ == "__main__":
    unittest.main()
