"""
مدل‌های انتزاعی داده برای تعاملات ربات تلگرام «کافی نت لیمو».
این مدل‌ها مرزبندی میان دریافت ورودی تلگرام و منطق داخلی سامانه را تضمین می‌کنند.
"""

from typing import List, Optional, Any
from pydantic import BaseModel, Field


class TelegramUser(BaseModel):
    """مدل اطلاعات کاربر تلگرام."""
    id: int
    is_bot: bool = False
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None


class IncomingMessage(BaseModel):
    """مدل پیام ورودی از کاربر تلگرام."""
    message_id: int
    from_user: TelegramUser
    text: Optional[str] = None
    date: int = 0
    # فیلدهای مربوط به مدارک و فایل‌های پیوست
    file_id: Optional[str] = None
    file_name: Optional[str] = None
    file_type: Optional[str] = None  # PHOTO | DOCUMENT
    file_size: Optional[int] = None
    caption: Optional[str] = None
    reply_to_message: Optional[Any] = None


class KeyboardButton(BaseModel):
    """مدل دکمه در رابط کاربری ربات."""
    text: str
    callback_data: Optional[str] = None


class OutgoingResponse(BaseModel):
    """مدل پاسخ تولیدشده توسط هسته ربات جهت ارسال به کاربر."""
    chat_id: int
    text: str
    reply_markup: Optional[List[List[KeyboardButton]]] = None
    parse_mode: str = "HTML"
    photo: Optional[str] = None
    callback_alert: Optional[str] = None
    notification: Optional[Any] = None  # پیام آگاه‌سازی ارسالی برای مخاطب ثانویه (مثلاً مشتری)
    message_id: Optional[int] = None  # شناسه پیام قبلی جهت ویرایش درجا (editMessageText)
    edit_message: bool = False  # در صورت True پیام قبلی ویرایش می‌شود (مشابه ربات باختر)


class CallbackQuery(BaseModel):
    """مدل رویداد کلیک روی دکمه‌های شیشه‌ای (Callback Query)."""
    id: str
    from_user: TelegramUser
    data: Optional[str] = None
    message: Optional[IncomingMessage] = None

