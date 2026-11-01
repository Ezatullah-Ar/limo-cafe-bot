"""
ماژول دیسپچر و مسیریابی پیام‌ها و کالبک‌های ربات «کافی نت لیمو».
این بخش پیام‌ها و کلیک روی دکمه‌ها را دریافت، اعتبارسنجی امنیتی، کنترل نرخ ارسال (Throttling)،
مدیریت ماشین وضعیت FSM و هدایت به هندلرهای مربوطه را انجام می‌دهد.
"""

import logging
import re
from typing import Optional, List
from bot.models import IncomingMessage, CallbackQuery, OutgoingResponse, KeyboardButton
from bot.handlers import (
    handle_start,
    handle_admin,
    handle_orders,
    handle_stats,
    handle_health,
    handle_backup,
    handle_help,
    handle_unknown,
    ACCESS_DENIED_TEXT,
    WELCOME_TEXT
)
from bot.callbacks import handle_callback_query
from bot.fsm import FSMManager, FSMState
from core.security import AccessControl, AccessDeniedError
from core.throttling import Throttler
from core.database import DatabaseManager
from core.models import User
from core.validators import validate_national_id, validate_iranian_phone, validate_card_number, mask_sensitive_data
from services.catalog import CatalogService
from services.orders import OrderService
from services.reminders import ReminderService
from services.notifications import NotificationService
from services.sheets_sync import GoogleSheetsSyncService
from services.support import SupportService
from services.tracking import format_order_status_persian, render_order_card, render_user_orders_list
from services.wallet import WalletService
from core.calendar import parse_jalali_date, format_jalali_date, get_current_jalali

logger = logging.getLogger("dispatcher")

THROTTLED_WARNING_TEXT = (
    "⏳ <b>ارسال بیش از حد مجاز:</b>\n\n"
    "لطفاً کمی صبر کنید؛ ارسال رگباری پیام‌ها مجاز نیست. "
    "زمان انتظار: {wait_time} ثانیه."
)


def _back_to_main_markup() -> List[List[KeyboardButton]]:
    return [[KeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]]


class BotDispatcher:
    """دیسپچر پیام‌های ورودی و رویدادهای کالبک با کنترل دسترسی، مهار اسپم و مدیریت FSM."""

    def __init__(
        self,
        access_control: AccessControl,
        throttler: Optional[Throttler] = None,
        db_manager: Optional[DatabaseManager] = None,
        fsm_manager: Optional[FSMManager] = None
    ):
        self.access_control = access_control
        self.throttler = throttler if throttler is not None else Throttler()
        self.db_manager = db_manager
        self.fsm_manager = fsm_manager if fsm_manager is not None else FSMManager()

    def dispatch(self, message: IncomingMessage, current_time: Optional[float] = None) -> OutgoingResponse:
        """
        مسیریابی پیام متنی دریافتی با اولویت مهار اسپم و ماشین وضعیت FSM.
        """
        user_id = message.from_user.id

        # ۱. بررسی محدودیت نرخ ارسال (Throttling)
        allowed, wait_time = self.throttler.is_allowed(user_id, current_time=current_time)
        if not allowed:
            logger.warning("Throttled user_id=%s wait_time=%.2fs", user_id, wait_time)
            return OutgoingResponse(
                chat_id=user_id,
                text=THROTTLED_WARNING_TEXT.format(wait_time=wait_time)
            )

        text = (message.text or "").strip()

        # ۱.۵. بررسی پیام‌های ویژه اپراتور/مدیر (پاسخ مستقیم با ریپلای و ارسال مدرک نهایی)
        if self.access_control.is_admin(user_id):
            if message.reply_to_message:
                admin_reply_resp = self._handle_admin_direct_reply(message)
                if admin_reply_resp:
                    return admin_reply_resp

            if text.startswith("/send"):
                return self._handle_admin_send_command(message)

        # ۲. بررسی دستور انصراف (/cancel)
        if text == "/cancel":
            self.fsm_manager.clear_state(user_id)
            keyboard_main: List[List[KeyboardButton]] = [
                [KeyboardButton(text="📋 فهرست خدمات", callback_data="services_list")],
                [
                    KeyboardButton(text="🔍 پیگیری با کد", callback_data="order_tracking"),
                    KeyboardButton(text="📂 درخواست‌های من", callback_data="my_orders")
                ],
                [KeyboardButton(text="⏰ یادآورها", callback_data="reminders_menu")],
                [KeyboardButton(text="📞 ارتباط با اپراتور", callback_data="contact_operator")]
            ]
            return OutgoingResponse(
                chat_id=user_id,
                text="❌ عملیات جاری لغو گردید و به منوی اصلی بازگشتید.",
                reply_markup=keyboard_main
            )

        # ۲.۵. بررسی دستور پرتال درخواست‌های من (/myorders)
        if text.startswith("/myorders") or text in ("درخواست‌های من", "پرونده‌های من", "سفارش‌های من"):
            return self._render_user_orders(user_id)

        # ۲.۶. بررسی دستور کیف پول (/wallet)
        if text.startswith("/wallet") or text in ("کیف پول", "موجودی", "حساب من"):
            return self._render_wallet(user_id)

        # ۳. بررسی دستور مستقیم رهگیری (/track <code?>)
        if text.startswith("/track"):
            parts = text.split(maxsplit=1)
            if len(parts) > 1:
                return self._render_tracking_result(user_id, parts[1])
            else:
                self.fsm_manager.start_tracking_flow(user_id)
                return OutgoingResponse(
                    chat_id=user_id,
                    text="🔍 لطفاً <b>کد رهگیری</b> پرونده خود را ارسال فرمایید (مثال: <code>LIMO-1405-88219</code>):",
                    reply_markup=_back_to_main_markup()
                )

        # ۴. پردازش پیام‌های جاری در ماشین وضعیت FSM
        state = self.fsm_manager.get_state(user_id)
        if state:
            # دریافت مدارک پیوست در خلال تکمیل سفارش
            if message.file_id and state.step in ("FIELD_INPUT", "CONFIRMATION"):
                return self._handle_order_document_upload(user_id, message, state)

            if state.step == "AWAITING_TRACKING_CODE":
                return self._render_tracking_result(user_id, text)

            elif state.step == "FIELD_INPUT":
                return self._handle_fsm_field_input(user_id, text, state)

            elif state.step == "OPERATOR_NOTE" and state.order_id and state.target_status:
                return self._handle_operator_note_input(user_id, text, state)

            elif state.step == "REMINDER_TITLE":
                return self._handle_reminder_title_input(user_id, text, state)

            elif state.step == "REMINDER_DATE":
                return self._handle_reminder_date_input(user_id, text, state, message)

            elif state.step == "IN_SUPPORT_CHAT":
                return self._handle_support_chat_message(user_id, message, state)

        # ۵. مسیریابی دستورات پایه تلگرام در غیاب وضعیت فعال FSM
        command = text.split()[0].lower() if text else ""
        if "@" in command:
            command = command.split("@")[0]

        try:
            if command == "/start":
                self.fsm_manager.clear_state(user_id)
                return handle_start(message)
            elif command == "/chat":
                self.fsm_manager.start_chat_flow(user_id)
                return OutgoingResponse(
                    chat_id=user_id,
                    text=(
                        "💬 <b>شما به سامانه گفتگوی مستقیم با پشتیبانی کافی‌نت لیمو متصل شدید.</b>\n\n"
                        "لطفاً پیام، سوال یا فایل‌های خود را در همین صفحه ارسال فرمایید. "
                        "اپراتور سامانه در اسرع وقت پاسخ شما را ارسال خواهد کرد.\n\n"
                        "<i>(جهت خروج از گفتگو، دکمه زیر را لمس کرده یا دستور /endchat را بفرستید)</i>"
                    ),
                    reply_markup=[[KeyboardButton(text="❌ پایان گفتگو و بازگشت", callback_data="exit_chat")]]
                )
            elif command == "/endchat":
                self.fsm_manager.clear_state(user_id)
                return OutgoingResponse(
                    chat_id=user_id,
                    text="✅ <b>گفتگوی شما با پشتیبانی به پایان رسید.</b>\nبه منوی اصلی بازگشتید.",
                    reply_markup=_back_to_main_markup()
                )
            elif command == "/admin":
                return handle_admin(message, self.access_control)
            elif command == "/orders":
                return handle_orders(message, self.access_control, self.db_manager)
            elif command == "/stats":
                return handle_stats(message, self.access_control, self.db_manager)
            elif command == "/health":
                return handle_health(message, self.access_control, self.db_manager)
            elif command == "/backup":
                return handle_backup(message, self.access_control, self.db_manager)
            elif command in ("/help", "راهنما"):
                return handle_help(message)
            else:
                return handle_unknown(message)

        except AccessDeniedError:
            return OutgoingResponse(
                chat_id=user_id,
                text=ACCESS_DENIED_TEXT
            )
        except Exception as exc:
            logger.exception("Unexpected error handling message_id=%s: %s", message.message_id, exc)
            return OutgoingResponse(
                chat_id=user_id,
                text="متأسفانه در پردازش درخواست شما خطایی رخ داد. لطفاً لحظاتی دیگر تلاش فرمایید."
            )

    def _render_tracking_result(self, chat_id: int, tracking_code: str) -> OutgoingResponse:
        """استعلام وضعیت پرونده از دیتابیس با رعایت کامل عایق‌بندی اطلاعات و تولید استپر ۴ مرحله‌ای."""
        if not self.db_manager:
            return OutgoingResponse(
                chat_id=chat_id,
                text="پایگاه داده در دسترس نیست.",
                reply_markup=_back_to_main_markup()
            )

        with self.db_manager.get_session() as session:
            order = OrderService.get_order_by_tracking_code(session, tracking_code)
            if not order:
                return OutgoingResponse(
                    chat_id=chat_id,
                    text=(
                        f"❌ پرونده‌ای با کد رهگیری <code>{tracking_code.strip()}</code> یافت نشد.\n\n"
                        "لطفاً کد رهگیری را مجدداً با دقت بررسی فرمایید، یا دستور /cancel را برای بازگشت به منوی اصلی ارسال کنید."
                    ),
                    reply_markup=_back_to_main_markup()
                )

            # پاکسازی وضعیت FSM پس از استعلام موفق
            self.fsm_manager.clear_state(chat_id)

            is_admin_or_op = self.access_control.is_admin(chat_id)
            is_authorized, report_text = render_order_card(
                order=order,
                requester_telegram_id=chat_id,
                is_admin_or_op=is_admin_or_op
            )

            if not is_authorized:
                logger.warning("Tenant isolation violation attempt: chat_id=%s tried to view order %s", chat_id, tracking_code)

            return OutgoingResponse(
                chat_id=chat_id,
                text=report_text,
                reply_markup=_back_to_main_markup()
            )

    def _render_user_orders(self, chat_id: int) -> OutgoingResponse:
        """ارائه پرتال درخواست‌های من و سوابق پرونده‌ها با تفکیک قطعی شناسه کاربر."""
        if not self.db_manager:
            return OutgoingResponse(
                chat_id=chat_id,
                text="پایگاه داده در دسترس نیست.",
                reply_markup=_back_to_main_markup()
            )

        with self.db_manager.get_session() as session:
            orders = OrderService.get_user_orders_by_telegram_id(session, chat_id)
            report_text = render_user_orders_list(orders)

            buttons: List[List[KeyboardButton]] = []
            if orders:
                for o in orders[:5]:
                    status_meta = format_order_status_persian(o.status)
                    svc_title = (o.service.title[:15] + "...") if o.service and len(o.service.title) > 15 else (o.service.title if o.service else "")
                    buttons.append([
                        KeyboardButton(
                            text=f"{status_meta['icon']} {o.tracking_code} ({svc_title})",
                            callback_data=f"track_code_{o.tracking_code}"
                        )
                    ])

            buttons.append([KeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")])

            return OutgoingResponse(
                chat_id=chat_id,
                text=report_text,
                reply_markup=buttons
            )

    def _render_wallet(self, chat_id: int) -> OutgoingResponse:
        """ارائه کارت اطلاعات موجودی کیف پول و گردش تراکنش‌های متقاضی."""
        if not self.db_manager:
            return OutgoingResponse(
                chat_id=chat_id,
                text="پایگاه داده در دسترس نیست.",
                reply_markup=_back_to_main_markup()
            )

        with self.db_manager.get_session() as session:
            user = session.query(User).filter_by(telegram_id=chat_id).first()
            if not user:
                user = User(telegram_id=chat_id, full_name="مشتری")
                session.add(user)
                session.commit()
            wallet = WalletService.get_or_create_wallet(session, user.id)
            history = WalletService.get_transaction_history(session, user.id, limit=5)
            card_text = WalletService.format_wallet_card(wallet, history)
            buttons = [
                [KeyboardButton(text="💬 هماهنگی شارژ با پشتیبانی", callback_data="contact_operator")],
                [KeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
            ]
            return OutgoingResponse(
                chat_id=chat_id,
                text=card_text,
                reply_markup=buttons
            )

    def _handle_fsm_field_input(self, user_id: int, text: str, state) -> OutgoingResponse:
        """اعتبارسنجی ورودی هر مرحله از فرم و هدایت به مرحله بعد یا صفحه تایید."""
        field_key = state.field_keys[state.current_field_index]

        # اعتبارسنجی اختصاصی کدملی
        if field_key in ("national_id", "landlord_national_id"):
            is_valid, err_msg = validate_national_id(text)
            if not is_valid:
                buttons = []
                if state.current_field_index > 0:
                    buttons.append([KeyboardButton(text="🔙 مرحله قبل", callback_data="order_step_back")])
                buttons.append([KeyboardButton(text="❌ انصراف", callback_data="order_cancel")])
                return OutgoingResponse(
                    chat_id=user_id,
                    text=(
                        f"⚠️ <b>خطای اعتبارسنجی:</b> {err_msg}\n\n"
                        "لطفاً <b>کد ملی ۱۰ رقمی</b> را مجدداً با دقت وارد فرمایید:"
                    ),
                    reply_markup=buttons
                )

        # اعتبارسنجی اختصاصی شماره همراه
        elif field_key in ("mobile_phone", "phone", "phone_number", "tenant_phone", "landlord_phone"):
            is_valid, err_msg = validate_iranian_phone(text)
            if not is_valid:
                buttons = []
                if state.current_field_index > 0:
                    buttons.append([KeyboardButton(text="🔙 مرحله قبل", callback_data="order_step_back")])
                buttons.append([KeyboardButton(text="❌ انصراف", callback_data="order_cancel")])
                return OutgoingResponse(
                    chat_id=user_id,
                    text=(
                        f"⚠️ <b>خطای اعتبارسنجی:</b> {err_msg}\n\n"
                        "لطفاً <b>شماره تلفن همراه</b> (مثال: 09123456789) را وارد فرمایید:"
                    ),
                    reply_markup=buttons
                )

        # اعتبارسنجی اختصاصی شماره کارت بانکی
        elif field_key in ("card_number", "landlord_card_number"):
            is_valid, err_msg = validate_card_number(text)
            if not is_valid:
                buttons = []
                if state.current_field_index > 0:
                    buttons.append([KeyboardButton(text="🔙 مرحله قبل", callback_data="order_step_back")])
                buttons.append([KeyboardButton(text="❌ انصراف", callback_data="order_cancel")])
                return OutgoingResponse(
                    chat_id=user_id,
                    text=(
                        f"⚠️ <b>خطای اعتبارسنجی:</b> {err_msg}\n\n"
                        "لطفاً <b>شماره کارت بانکی ۱۶ رقمی</b> (مثال: 6037991812345678) را وارد فرمایید:"
                    ),
                    reply_markup=buttons
                )

        # ذخیره ورودی معتبر
        state.collected_data[field_key] = text.strip()
        state.current_field_index += 1

        # اگر هنوز فیلد دیگری باقی مانده است
        if state.current_field_index < len(state.field_keys):
            next_field_key = state.field_keys[state.current_field_index]
            with self.db_manager.get_session() as session:
                service = CatalogService.get_service_by_code(session, state.service_code)
                next_label = service.required_fields.get(next_field_key, next_field_key) if service else next_field_key

            # اگر فیلد بعدی witness_mode مربوط به مسکن باشد
            if next_field_key == "witness_mode":
                prompt_witness = (
                    f"📝 <b>مرحله {state.current_field_index + 1} از {len(state.field_keys)}:</b>\n\n"
                    "👥 <b>نحوه معرفی دو شاهد ایرانی:</b>\n\n"
                    "برای صدور کد رهگیری، معرفی مشخصات دو شاهد ایرانی الزامی است.\n"
                    "شما می‌توانید مشخصات دو شاهد را شخصاً معرفی فرمایید، یا درخواست تأمین شاهد توسط کافی‌نت لیمو (تعرفه مصوب ۳۵۰،۰۰۰ تومان) را ثبت نمایید.\n\n"
                    "لطفاً یکی از گزینه‌های زیر را انتخاب فرمایید:"
                )
                keyboard_witness = [
                    [KeyboardButton(text="👥 خودم دو شاهد معرفی می‌کنم", callback_data="witness_choice_self")],
                    [KeyboardButton(text="🤝 تأمین دو شاهد توسط کافی‌نت (تعرفه ۳۵۰ هزار تومان)", callback_data="witness_choice_limo")],
                    [KeyboardButton(text="🔙 مرحله قبل", callback_data="order_step_back")],
                    [KeyboardButton(text="❌ انصراف", callback_data="order_cancel")]
                ]
                return OutgoingResponse(
                    chat_id=user_id,
                    text=prompt_witness,
                    reply_markup=keyboard_witness
                )

            buttons = []
            if state.current_field_index > 0:
                buttons.append([KeyboardButton(text="🔙 مرحله قبل", callback_data="order_step_back")])
            buttons.append([KeyboardButton(text="❌ انصراف", callback_data="order_cancel")])

            return OutgoingResponse(
                chat_id=user_id,
                text=(
                    f"📝 <b>مرحله {state.current_field_index + 1} از {len(state.field_keys)}:</b>\n\n"
                    f"لطفاً <b>{next_label}</b> را وارد فرمایید:"
                ),
                reply_markup=buttons
            )

        # تمام فیلدها دریافت شد؛ تغییر وضعیت به پیش‌نمایش و تایید نهایی
        state.step = "CONFIRMATION"

        with self.db_manager.get_session() as session:
            service = CatalogService.get_service_by_code(session, state.service_code)
            svc_title = service.title if service else state.service_code

        summary_lines = []
        for k, v in state.collected_data.items():
            label = service.required_fields.get(k, k) if service else k
            # ماسک کردن داده‌های حساس
            if k in ("landlord_card_number", "card_number"):
                display_val = mask_sensitive_data(str(v), "card")
            elif k in ("national_id", "landlord_national_id"):
                display_val = mask_sensitive_data(str(v), "national_id")
            elif k in ("tenant_phone", "landlord_phone", "mobile_phone", "phone", "phone_number"):
                display_val = mask_sensitive_data(str(v), "phone")
            else:
                display_val = str(v)
            summary_lines.append(f"• <b>{label}:</b> <code>{display_val}</code>")

        preview_text = (
            f"📋 <b>پیش‌نمایش درخواست: {svc_title}</b>\n\n"
            "اطلاعات واردشده توسط شما به شرح زیر است (جهت حفظ امنیت، اطلاعات حساس ماسک شده‌اند):\n\n"
            + "\n".join(summary_lines)
            + (f"\n\n📎 <b>مدارک پیوست‌شده:</b> {len(state.collected_docs)} مدرک" if state.collected_docs else "")
            + "\n\n⚠️ <i>لطفاً صحت اطلاعات فوق را بررسی فرمایید. در صورت تأیید، پرونده ثبت و به کارتابل اپراتور ارسال می‌گردد.</i>"
        )
        keyboard_confirm: List[List[KeyboardButton]] = [
            [KeyboardButton(text="✅ تأیید و ثبت نهایی درخواست", callback_data="order_confirm")],
            [KeyboardButton(text="🔙 مرحله قبل (ویرایش)", callback_data="order_step_back")],
            [KeyboardButton(text="❌ انصراف و لغو", callback_data="order_cancel")]
        ]
        return OutgoingResponse(
            chat_id=user_id,
            text=preview_text,
            reply_markup=keyboard_confirm
        )

    def _handle_order_document_upload(
        self,
        user_id: int,
        message: IncomingMessage,
        state: FSMState
    ) -> OutgoingResponse:
        """ذخیره موقت مدرک پیوست ارسالی کاربر در حافظه FSM تا زمان ثبت نهایی سفارش."""
        doc_entry = {
            "file_id": message.file_id,
            "file_name": message.file_name or f"document_{len(state.collected_docs) + 1}",
            "file_type": message.file_type or "DOCUMENT",
            "file_size": message.file_size
        }
        state.collected_docs.append(doc_entry)

        return OutgoingResponse(
            chat_id=user_id,
            text=(
                f"📎 <b>مدرک با موفقیت ضمیمه گردید ({len(state.collected_docs)} مدرک پیوست شد).</b>\n\n"
                "در صورت تمایل می‌توانید مدرک بعدی را ارسال فرمایید، یا سفارش را تایید و نهایی کنید."
            ),
            reply_markup=[
                [KeyboardButton(text="✅ تأیید و ثبت نهایی درخواست", callback_data="order_confirm")],
                [KeyboardButton(text="❌ انصراف و لغو", callback_data="order_cancel")]
            ]
        )

    def _handle_operator_note_input(self, user_id: int, text: str, state) -> OutgoingResponse:
        """پردازش ثبت یادداشت، اعلام نقص مدرک یا علت لغو توسط اپراتور."""
        if not self.access_control.is_admin(user_id):
            self.fsm_manager.clear_state(user_id)
            return OutgoingResponse(
                chat_id=user_id,
                text=ACCESS_DENIED_TEXT
            )

        note_text = text.strip()
        order_id = state.order_id
        target_status = state.target_status

        if not self.db_manager:
            return OutgoingResponse(chat_id=user_id, text="دیتابیس در دسترس نیست.")

        with self.db_manager.get_session() as session:
            order = OrderService.update_order_status(
                session=session,
                order_id=order_id,
                new_status=target_status,
                actor_telegram_id=user_id,
                note=note_text
            )
            tracking_code = order.tracking_code
            status_meta = format_order_status_persian(target_status)
            customer_alert = NotificationService.create_customer_status_alert(
                order=order,
                new_status=target_status,
                note=note_text
            )

        self.fsm_manager.clear_state(user_id)

        confirm_text = (
            f"✅ <b>وضعیت پرونده {tracking_code} بروزرسانی شد:</b>\n\n"
            f"📌 <b>وضعیت جدید:</b> {status_meta['icon']} {status_meta['title']}\n"
            f"💬 <b>یادداشت ثبت‌شده:</b>\n<i>{note_text}</i>"
        )
        keyboard = [
            [KeyboardButton(text="📂 مشاهده مجدد پرونده", callback_data=f"op_view_{order_id}")],
            [KeyboardButton(text="🔙 بازگشت به کارتابل سفارشات", callback_data="admin_orders")]
        ]
        return OutgoingResponse(
            chat_id=user_id,
            text=confirm_text,
            reply_markup=keyboard,
            notification=customer_alert
        )

    def _handle_reminder_title_input(self, user_id: int, text: str, state: FSMState) -> OutgoingResponse:
        """پردازش متن عنوان یادآور در جریان FSM و هدایت به دریافت تاریخ شمسی."""
        title = text.strip()
        if len(title) < 2:
            return OutgoingResponse(
                chat_id=user_id,
                text="❌ عنوان یادآور بسیار کوتاه است. لطفاً عنوانی مشخص وارد فرمایید (مثال: <code>مهلت ثبت‌نام کنکور سراسری</code>):"
            )

        self.fsm_manager.set_reminder_title(user_id, title)
        cur_jy, cur_jm, cur_jd = get_current_jalali()
        example_date = f"{cur_jy}/{cur_jm:02d}/{min(cur_jd + 7, 28):02d}"

        prompt = (
            f"📌 <b>موضوع یادآور:</b> <code>{title}</code>\n\n"
            "📅 اکنون لطفاً <b>تاریخ سررسید شمسی</b> را ارسال فرمایید:\n"
            f"• قالب مجاز: <code>سال/ماه/روز</code> (مثال: <code>{example_date}</code>)\n\n"
            "<i>یا دستور /cancel را برای انصراف ارسال فرمایید.</i>"
        )
        return OutgoingResponse(
            chat_id=user_id,
            text=prompt
        )

    def _handle_reminder_date_input(
        self,
        user_id: int,
        text: str,
        state: FSMState,
        message: IncomingMessage
    ) -> OutgoingResponse:
        """اعتبارسنجی تاریخ شمسی، ذخیره یادآور در دیتابیس و ارسال تاییدیه."""
        title = state.reminder_title or "یادآور مهلت"
        date_str = text.strip()

        if not self.db_manager:
            return OutgoingResponse(
                chat_id=user_id,
                text="پایگاه داده در دسترس نیست.",
                reply_markup=_back_to_main_markup()
            )

        try:
            with self.db_manager.get_session() as session:
                user_rec = CatalogService.get_or_create_user(
                    session=session,
                    telegram_id=user_id,
                    full_name=f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip(),
                    username=message.from_user.username
                )
                reminder = ReminderService.create_reminder(
                    session=session,
                    user_id=user_rec.id,
                    title=title,
                    shamsi_date=date_str
                )

                # پاکسازی وضعیت FSM پس از ثبت موفق
                self.fsm_manager.clear_state(user_id)

                jy, jm, jd = parse_jalali_date(reminder.shamsi_date)
                formatted_persian = format_jalali_date(jy, jm, jd)

                confirm_text = (
                    "⏰ <b>یادآور شما با موفقیت ثبت گردید!</b>\n\n"
                    f"📌 <b>موضوع:</b> {reminder.title}\n"
                    f"📅 <b>موعد سررسید:</b> {formatted_persian}\n"
                    "🕘 <b>ساعت یادآوری:</b> ۰۹:۰۰ صبح (به وقت رسمی کشور)\n\n"
                    "در موعد مقرر، پیام یادآوری به صورت خودکار در همین ربات برای شما ارسال خواهد شد."
                )
                keyboard = [
                    [KeyboardButton(text="📋 مشاهده یادآورهای فعال", callback_data="rem_list")],
                    [KeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
                ]
                return OutgoingResponse(
                    chat_id=user_id,
                    text=confirm_text,
                    reply_markup=keyboard
                )

        except ValueError as val_err:
            return OutgoingResponse(
                chat_id=user_id,
                text=(
                    f"❌ <b>خطا در تاریخ ورودی:</b> {str(val_err)}\n\n"
                    "لطفاً تاریخ را مجدداً به صورت سال/ماه/روز وارد فرمایید (مثال: <code>1405/08/20</code>)، "
                    "یا دستور /cancel را برای انصراف ارسال کنید."
                )
            )

    def _handle_support_chat_message(self, user_id: int, message: IncomingMessage, state: FSMState) -> OutgoingResponse:
        """پردازش پیام متقاضی در حالت گفتگوی زنده با پشتیبانی (چت دوطرفه)."""
        text = (message.text or "").strip()
        if text in ("/endchat", "خروج از گفتگو", "پایان گفتگو", "/cancel"):
            self.fsm_manager.clear_state(user_id)
            if self.db_manager:
                try:
                    with self.db_manager.get_session() as session:
                        user_rec = session.query(User).filter_by(telegram_id=user_id).first()
                        if user_rec:
                            thread = SupportService.get_or_create_active_thread(session, user_rec.id)
                            SupportService.close_thread(session, thread.id, actor_id=user_id)
                except Exception as e:
                    logger.warning("Error closing support thread for user %d: %s", user_id, e)

            return OutgoingResponse(
                chat_id=user_id,
                text="✅ <b>گفتگوی شما با پشتیبانی به پایان رسید.</b>\nبه منوی اصلی بازگشتید.",
                reply_markup=_back_to_main_markup()
            )

        admin_id = self.access_control.admin_id
        user_name = message.from_user.first_name
        content = text or (f"[فایل پیوست: {message.file_name or message.file_type}]" if message.file_id else "")

        thread_id_str = ""
        if self.db_manager:
            try:
                with self.db_manager.get_session() as session:
                    user_rec = CatalogService.get_or_create_user(
                        session=session,
                        telegram_id=user_id,
                        full_name=f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip(),
                        username=message.from_user.username
                    )
                    thread = SupportService.get_or_create_active_thread(session, user_rec.id)
                    SupportService.add_customer_message(
                        session=session,
                        thread_id=thread.id,
                        sender_telegram_id=user_id,
                        message_text=text or None,
                        file_id=message.file_id,
                        file_type=message.file_type
                    )
                    thread_id_str = f" (تیکت #{thread.id})"
            except Exception as e:
                logger.error("Failed to record support message: %s", e)

        admin_notification = OutgoingResponse(
            chat_id=admin_id,
            text=(
                f"💬 <b>پیام چت زنده از:</b> {user_name} (شناسه: <code>{user_id}</code>){thread_id_str}\n\n"
                f"{content}\n\n"
                f"<i>(برای پاسخ مستقیم به متقاضی، کافیست این پیام را ریپلای کنید)</i>"
            )
        )

        return OutgoingResponse(
            chat_id=user_id,
            text="✅ پیام شما برای اپراتور ارسال شد. پاسخ اپراتور در همینجا نمایش داده خواهد شد.",
            reply_markup=[[KeyboardButton(text="❌ پایان گفتگو و بازگشت", callback_data="exit_chat")]],
            notification=admin_notification
        )

    def _handle_admin_direct_reply(self, message: IncomingMessage) -> Optional[OutgoingResponse]:
        """ارسال پاسخ ریپلای‌شده مدیر به چت مشتری و ثبت در تیکت پشتیبانی."""
        reply_msg = message.reply_to_message
        target_text = (getattr(reply_msg, "text", "") or "") + " " + (getattr(reply_msg, "caption", "") or "")

        # استخراج آیدی کاربر از متن پیام
        id_match = re.search(r'شناسه:\s*<code>?(\d+)</code>?', target_text) or re.search(r'ID:\s*<code>?(\d+)</code>?', target_text)
        if id_match:
            target_chat_id = int(id_match.group(1))
            reply_text = message.text or message.caption or ""

            if self.db_manager:
                try:
                    with self.db_manager.get_session() as session:
                        user_rec = session.query(User).filter_by(telegram_id=target_chat_id).first()
                        if user_rec:
                            thread = SupportService.get_or_create_active_thread(session, user_rec.id)
                            SupportService.add_operator_message(
                                session=session,
                                thread_id=thread.id,
                                operator_telegram_id=message.from_user.id,
                                message_text=reply_text or None,
                                file_id=message.file_id,
                                file_type=message.file_type
                            )
                except Exception as e:
                    logger.error("Failed to record operator reply: %s", e)

            return OutgoingResponse(
                chat_id=message.from_user.id,
                text="✅ <b>پیام شما با موفقیت برای متقاضی ارسال شد.</b>",
                notification=OutgoingResponse(
                    chat_id=target_chat_id,
                    text=f"💬 <b>پیام پشتیبانی کافی نت لیمو:</b>\n\n{reply_text}"
                )
            )
        return None

    def _handle_admin_send_command(self, message: IncomingMessage) -> OutgoingResponse:
        """ارسال فایل یا نتیجه نهایی پرونده توسط مدیر به مشتری و تکمیل پرونده."""
        parts = (message.text or "").split(maxsplit=2)
        if len(parts) < 2:
            return OutgoingResponse(
                chat_id=message.from_user.id,
                text="⚠️ لطفاً کد رهگیری را پس از دستور وارد فرمایید:\nمثال: <code>/send LIMO-1405-12345 فایل نهایی تاییدیه تحصیلی</code>"
            )
        tracking_code = parts[1].strip()
        custom_note = parts[2].strip() if len(parts) > 2 else "مدارک نهایی پرونده برای شما ارسال شد."

        if not self.db_manager:
            return OutgoingResponse(chat_id=message.from_user.id, text="پایگاه داده در دسترس نیست.")

        with self.db_manager.get_session() as session:
            order = OrderService.get_order_by_tracking_code(session, tracking_code)
            if not order:
                return OutgoingResponse(
                    chat_id=message.from_user.id,
                    text=f"❌ پرونده‌ای با کد رهگیری <code>{tracking_code}</code> یافت نشد."
                )

            # تغییر وضعیت به COMPLETED
            OrderService.update_order_status(
                session=session,
                order_id=order.id,
                new_status="COMPLETED",
                actor_telegram_id=message.from_user.id,
                note=custom_note
            )

            customer_chat_id = order.user.telegram_id
            customer_text = (
                f"🎉 <b>مشتری گرامی، پرونده شما تکمیل و نهایی شد!</b>\n\n"
                f"🔖 <b>کد پرونده:</b> <code>{tracking_code}</code>\n"
                f"📋 <b>خدمت:</b> {order.service.title}\n"
                f"💬 <b>توضیح اپراتور:</b> {custom_note}"
            )

            return OutgoingResponse(
                chat_id=message.from_user.id,
                text=f"✅ مدرک و نتیجه پرونده <code>{tracking_code}</code> با موفقیت برای متقاضی ارسال و وضعیت به «تکمیل‌شده» تغییر یافت.",
                notification=OutgoingResponse(
                    chat_id=customer_chat_id,
                    text=customer_text
                )
            )

    def dispatch_callback(self, query: CallbackQuery, current_time: Optional[float] = None) -> OutgoingResponse:
        """
        مسیریابی رویدادهای کلیک دکمه‌های شیشه‌ای.
        """
        user_id = query.from_user.id
        chat_id = query.message.from_user.id if query.message else user_id

        # بررسی محدودیت نرخ کلیک برای جلوگیری از کلیک‌های رگباری اسپمرها
        allowed, wait_time = self.throttler.is_allowed(user_id, current_time=current_time)
        if not allowed:
            logger.warning("Throttled callback from user_id=%s wait_time=%.2fs", user_id, wait_time)
            return OutgoingResponse(
                chat_id=chat_id,
                text=THROTTLED_WARNING_TEXT.format(wait_time=wait_time),
                callback_alert=f"لطفاً {wait_time} ثانیه صبر کنید."
            )

        try:
            resp = handle_callback_query(
                query=query,
                access_control=self.access_control,
                db_manager=self.db_manager,
                fsm_manager=self.fsm_manager
            )
            # رفتار مشابه ربات باختر: ویرایش درجا پیام قبلی بدون ارسال پیام جدید
            if query.message and query.message.message_id and not getattr(resp, "photo", None):
                resp.message_id = query.message.message_id
                resp.edit_message = True
            return resp
        except AccessDeniedError:
            return OutgoingResponse(
                chat_id=chat_id,
                text=ACCESS_DENIED_TEXT,
                callback_alert="خطای دسترسی!"
            )
        except Exception as exc:
            logger.exception("Unexpected error handling callback_id=%s: %s", query.id, exc)
            return OutgoingResponse(
                chat_id=chat_id,
                text="متأسفانه در پردازش این گزینه خطایی رخ داد.",
                callback_alert="خطای سرور"
            )
