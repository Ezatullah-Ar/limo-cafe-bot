"""
ماژول اجرای محلی و سرور سنتی به روش لانگ‌پولینگ (bot/polling.py)
سامانه «کافی نت لیمو».
این ماژول امکان اجرای ربات تلگرام بر روی سرورهای مجازی لینوکس (VPS)، داکر یا سیستم‌های محلی
را بدون نیاز به دامنه، گواهی SSL یا وب‌هوک فراهم می‌سازد.
"""

import os
import sys
import time
import json
import logging
import threading
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List
from bot.models import OutgoingResponse
from bot.dispatcher import BotDispatcher
from bot.webhook import parse_telegram_update, format_telegram_reply_markup
from core.database import DatabaseManager

logger = logging.getLogger("polling")


class TelegramClient:
    """کلاینت ارتباطی رسمی با Telegram Bot API بر پایه کتابخانه استاندارد پایتون."""

    def __init__(self, bot_token: str, opener: Optional[Any] = None, timeout: int = 30):
        self.bot_token = bot_token
        self.api_base = f"https://api.telegram.org/bot{bot_token}/"
        self.opener = opener
        self.timeout = timeout

    def call_method(self, method: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """اجرای متد تلگرام به صورت درخواست امن HTTPS."""
        url = f"{self.api_base}{method}"
        data = None
        headers = {"User-Agent": "LimoCafeBot-Polling/1.0"}

        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json; charset=utf-8"

        req = urllib.request.Request(url, data=data, headers=headers)
        call = self.opener.open if self.opener else urllib.request.urlopen

        try:
            with call(req, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body)
        except urllib.error.HTTPError as exc:
            err_body = exc.read().decode("utf-8")
            logger.error("Telegram API HTTP %s on %s: %s", exc.code, method, err_body)
            raise
        except Exception as exc:
            logger.error("Network error on %s: %s", method, exc)
            raise

    def get_updates(self, offset: Optional[int] = None, timeout: int = 25) -> List[Dict[str, Any]]:
        """دریافت آپدیت‌های جدید تلگرام به روش Long Polling."""
        payload: Dict[str, Any] = {
            "timeout": timeout,
            "allowed_updates": ["message", "callback_query"]
        }
        if offset is not None:
            payload["offset"] = offset

        res = self.call_method("getUpdates", payload)
        if res.get("ok"):
            return res.get("result", [])
        return []

    def send_response(self, response: OutgoingResponse) -> Dict[str, Any]:
        """ارسال پاسخ OutgoingResponse تولیدشده توسط دیسپچر به تلگرام."""
        if getattr(response, "photo", None):
            payload: Dict[str, Any] = {
                "chat_id": response.chat_id,
                "photo": response.photo,
                "caption": response.text,
                "parse_mode": response.parse_mode
            }
            if response.reply_markup:
                markup_dict = format_telegram_reply_markup(response.reply_markup)
                if markup_dict:
                    payload["reply_markup"] = markup_dict
            return self.call_method("sendPhoto", payload)

        if getattr(response, "edit_message", False) and getattr(response, "message_id", None):
            payload: Dict[str, Any] = {
                "chat_id": response.chat_id,
                "message_id": response.message_id,
                "text": response.text,
                "parse_mode": response.parse_mode
            }
            if response.reply_markup:
                markup_dict = format_telegram_reply_markup(response.reply_markup)
                if markup_dict:
                    payload["reply_markup"] = markup_dict
            try:
                return self.call_method("editMessageText", payload)
            except Exception as exc:
                logger.warning("editMessageText failed (%s), falling back to sendMessage", exc)

        payload: Dict[str, Any] = {
            "chat_id": response.chat_id,
            "text": response.text,
            "parse_mode": response.parse_mode
        }
        if response.reply_markup:
            markup_dict = format_telegram_reply_markup(response.reply_markup)
            if markup_dict:
                payload["reply_markup"] = markup_dict

        return self.call_method("sendMessage", payload)

    def answer_callback_query(
        self,
        callback_query_id: str,
        text: Optional[str] = None,
        show_alert: bool = False
    ) -> Dict[str, Any]:
        """تایید دریافت کالبک کوئری دکمه‌های شیشه‌ای جهت بستن لودینگ تلگرام."""
        payload: Dict[str, Any] = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = text
            payload["show_alert"] = show_alert
        return self.call_method("answerCallbackQuery", payload)


class PollingRunner:
    """مدیر چرخه حیات و حلقه دریافت پیام‌های تلگرام (Long-Polling Runner)."""

    def __init__(
        self,
        bot_token: str,
        dispatcher: BotDispatcher,
        db_manager: Optional[DatabaseManager] = None,
        client: Optional[TelegramClient] = None
    ):
        self.bot_token = bot_token
        self.dispatcher = dispatcher
        self.db_manager = db_manager
        self.client = client if client is not None else TelegramClient(bot_token)
        self.is_running = False
        self.last_offset: Optional[int] = None

    def run_once(self) -> int:
        """
        یک دور دریافت و پردازش آپدیت‌ها.
        مناسب برای حلقه‌های عملیاتی و همچنین آزمون‌های تست‌پذیر خودکار.
        """
        try:
            updates = self.client.get_updates(offset=self.last_offset, timeout=5)
        except Exception as exc:
            logger.warning("Error fetching updates in polling: %s", exc)
            return 0

        processed_count = 0
        for update in updates:
            up_id = update.get("update_id")
            if up_id is not None:
                self.last_offset = up_id + 1

            msg, query = parse_telegram_update(update)

            # ۱. پردازش پیام متنی یا فایل
            if msg is not None:
                resp = self.dispatcher.dispatch(msg)
                try:
                    self.client.send_response(resp)
                    if resp.notification and isinstance(resp.notification, OutgoingResponse):
                        self.client.send_response(resp.notification)
                except Exception as exc:
                    logger.error("Failed to send message response: %s", exc)
                processed_count += 1

            # ۲. پردازش کلیک روی دکمه شیشه‌ای
            elif query is not None:
                resp = self.dispatcher.dispatch_callback(query)
                try:
                    # بستن وضعیت لودینگ تلگرام
                    self.client.answer_callback_query(
                        callback_query_id=query.id,
                        text=resp.callback_alert,
                        show_alert=bool(resp.callback_alert)
                    )
                    self.client.send_response(resp)
                    if resp.notification and isinstance(resp.notification, OutgoingResponse):
                        self.client.send_response(resp.notification)
                except Exception as exc:
                    logger.error("Failed to send callback response: %s", exc)
                processed_count += 1

        return processed_count

    def start(self, poll_interval: float = 0.5):
        """آغاز حلقه دائمی پولینگ تا دریافت سیگنال توقف."""
        self.is_running = True
        logger.info("Limo Cafe Polling Runner started. Press Ctrl+C to stop.")

        while self.is_running:
            try:
                self.run_once()
                if poll_interval > 0:
                    time.sleep(poll_interval)
            except KeyboardInterrupt:
                logger.info("KeyboardInterrupt received. Stopping polling runner.")
                self.stop()
                break
            except Exception as exc:
                logger.error("Unexpected error in polling loop: %s", exc)
                time.sleep(2)

    def stop(self):
        """توقف تمیز حلقه پولینگ."""
        self.is_running = False
        logger.info("Polling runner stopped cleanly.")
