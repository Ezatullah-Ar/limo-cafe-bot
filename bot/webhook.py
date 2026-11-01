"""
ماژول هندلر وب‌هوک تلگرام (bot/webhook.py) سامانه «کافی نت لیمو».
مسئول دریافت آپدیت‌های تلگرام از طریق درخواست‌های HTTP POST، اعتبارسنجی توکن محرمانه (Secret Token)،
تبدیل به مدل‌های داده داخلی و تولید پاسخ به روش Webhook-Reply جهت سازگاری با کلودفلر و بسترهای Serverless.
"""

import json
from http.server import BaseHTTPRequestHandler
from typing import Optional, Dict, Any, Tuple, List
from bot.models import IncomingMessage, CallbackQuery, TelegramUser, KeyboardButton, OutgoingResponse
from bot.dispatcher import BotDispatcher


def format_telegram_reply_markup(markup: Optional[List[List[KeyboardButton]]]) -> Optional[Dict[str, Any]]:
    """تبدیل ساختار دکمه‌های داخلی به قالب رسمی inline_keyboard تلگرام."""
    if not markup:
        return None

    inline_keyboard = []
    for row in markup:
        button_row = []
        for btn in row:
            btn_dict: Dict[str, Any] = {"text": btn.text}
            if btn.callback_data is not None:
                btn_dict["callback_data"] = btn.callback_data
            button_row.append(btn_dict)
        inline_keyboard.append(button_row)

    return {"inline_keyboard": inline_keyboard}


def parse_telegram_update(data: Dict[str, Any]) -> Tuple[Optional[IncomingMessage], Optional[CallbackQuery]]:
    """تجزیه و اعتبارسنجی بدنه JSON آپدیت تلگرام و تبدیل به مدل‌های پایتون."""
    if "message" in data and isinstance(data["message"], dict):
        raw_msg = data["message"]
        from_data = raw_msg.get("from") or {}
        user = TelegramUser(
            id=from_data.get("id", 0),
            is_bot=from_data.get("is_bot", False),
            first_name=from_data.get("first_name", "کاربر"),
            last_name=from_data.get("last_name"),
            username=from_data.get("username")
        )
        file_id = None
        file_name = None
        file_type = None
        file_size = None
        caption = raw_msg.get("caption")

        if "document" in raw_msg and isinstance(raw_msg["document"], dict):
            doc = raw_msg["document"]
            file_id = doc.get("file_id")
            file_name = doc.get("file_name")
            file_type = "DOCUMENT"
            file_size = doc.get("file_size")
        elif "photo" in raw_msg and isinstance(raw_msg["photo"], list) and raw_msg["photo"]:
            photo = raw_msg["photo"][-1]
            file_id = photo.get("file_id")
            file_name = "photo.jpg"
            file_type = "PHOTO"
            file_size = photo.get("file_size")

        reply_to_raw = raw_msg.get("reply_to_message")
        reply_to_obj = None
        if reply_to_raw and isinstance(reply_to_raw, dict):
            reply_from = reply_to_raw.get("from") or {}
            reply_user = TelegramUser(
                id=reply_from.get("id", 0),
                is_bot=reply_from.get("is_bot", False),
                first_name=reply_from.get("first_name", "کاربر"),
                last_name=reply_from.get("last_name"),
                username=reply_from.get("username")
            )
            reply_to_obj = IncomingMessage(
                message_id=reply_to_raw.get("message_id", 0),
                from_user=reply_user,
                text=reply_to_raw.get("text") or reply_to_raw.get("caption"),
                date=reply_to_raw.get("date", 0)
            )

        msg = IncomingMessage(
            message_id=raw_msg.get("message_id", 0),
            from_user=user,
            text=raw_msg.get("text") or caption,
            date=raw_msg.get("date", 0),
            file_id=file_id,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            caption=caption,
            reply_to_message=reply_to_obj
        )
        return msg, None

    elif "callback_query" in data and isinstance(data["callback_query"], dict):
        raw_cb = data["callback_query"]
        from_data = raw_cb.get("from") or {}
        user = TelegramUser(
            id=from_data.get("id", 0),
            is_bot=from_data.get("is_bot", False),
            first_name=from_data.get("first_name", "کاربر"),
            last_name=from_data.get("last_name"),
            username=from_data.get("username")
        )

        msg_obj = None
        if "message" in raw_cb and isinstance(raw_cb["message"], dict):
            raw_msg = raw_cb["message"]
            msg_obj = IncomingMessage(
                message_id=raw_msg.get("message_id", 0),
                from_user=user,
                text=raw_msg.get("text"),
                date=raw_msg.get("date", 0)
            )

        query = CallbackQuery(
            id=str(raw_cb.get("id", "")),
            from_user=user,
            data=raw_cb.get("data"),
            message=msg_obj
        )
        return None, query

    return None, None


def handle_webhook_payload(
    payload: Dict[str, Any],
    dispatcher: BotDispatcher,
    configured_secret: Optional[str] = None,
    received_secret: Optional[str] = None
) -> Tuple[int, Dict[str, Any]]:
    """
    پردازش اصلی ورودی وب‌هوک با اعتبارسنجی هدر امنیتی Secret Token و تولید پاسخ Webhook-Reply.
    """
    # بررسی امنیتی توکن محرمانه وب‌هوک تلگرام
    if configured_secret:
        if not received_secret or received_secret != configured_secret:
            return 403, {"ok": False, "error": "Invalid or missing secret token"}

    msg, query = parse_telegram_update(payload)

    if msg is not None:
        response: OutgoingResponse = dispatcher.dispatch(msg)
        reply_dict: Dict[str, Any] = {
            "method": "sendMessage",
            "chat_id": response.chat_id,
            "text": response.text,
            "parse_mode": response.parse_mode
        }
        if response.reply_markup:
            reply_dict["reply_markup"] = format_telegram_reply_markup(response.reply_markup)
        return 200, reply_dict

    elif query is not None:
        response = dispatcher.dispatch_callback(query)
        reply_dict = {
            "method": "sendMessage",
            "chat_id": response.chat_id,
            "text": response.text,
            "parse_mode": response.parse_mode
        }
        if response.reply_markup:
            reply_dict["reply_markup"] = format_telegram_reply_markup(response.reply_markup)
        return 200, reply_dict

    return 200, {"ok": True, "status": "ignored"}
