"""
هندلرهای پایه و پردازش منطق پیام‌های ربات تلگرام «کافی نت لیمو».
این توابع بدون اتصال مستقیم به اینترنت و به صورت کاملاً تست‌پذیر پیاده‌سازی شده‌اند.
"""

from typing import List, Optional, Any
from bot.models import IncomingMessage, OutgoingResponse, KeyboardButton
from core.security import AccessControl


WELCOME_TEXT = (
    "سلام به سامانه <b>کافی نت لیمو</b> خوش آمدید.\n\n"
    "این سامانه جهت تسهیل ثبت درخواست‌های خدمات دانشجویی، "
    "پیگیری پرونده‌ها و یادآوری مهلت‌های ثبت‌نام طراحی شده است.\n\n"
    "جهت شروع یکی از گزینه‌های زیر را انتخاب فرمایید:"
)

ADMIN_PANEL_TEXT = (
    "<b>پنل مدیریت سامانه کافی نت لیمو</b>\n\n"
    "دسترسی شما به عنوان مدیر ارشد سیستم احراز شد.\n"
    "امکانات مدیریتی فعال:"
)

ACCESS_DENIED_TEXT = (
    "⛔ <b>خطای عدم دسترسی</b>\n\n"
    "این بخش منحصراً در اختیار مدیر سیستم است و شما مجاز به مشاهده آن نیستید."
)

HELP_TEXT = (
    "<b>راهنمای سامانه کافی نت لیمو:</b>\n\n"
    "• ارسال دستور /start برای مشاهده منوی اصلی\n"
    "• کلیه درخواست‌ها مستقیماً با اپراتور هماهنگ می‌شوند."
)

UNKNOWN_COMMAND_TEXT = (
    "دستور یا پیام ارسالی نامعتبر است.\n"
    "لطفاً از دستور /start برای بازگشت به منوی اصلی استفاده کنید."
)


def handle_start(message: IncomingMessage) -> OutgoingResponse:
    """پردازش دستور شروع (/start) برای تمام کاربران."""
    keyboard: List[List[KeyboardButton]] = [
        [KeyboardButton(text="📋 فهرست خدمات", callback_data="services_list")],
        [
            KeyboardButton(text="🔍 پیگیری سفارش", callback_data="order_tracking"),
            KeyboardButton(text="📂 درخواست‌های من", callback_data="my_orders")
        ],
        [
            KeyboardButton(text="💳 کیف پول", callback_data="wallet_menu"),
            KeyboardButton(text="⏰ یادآورها", callback_data="reminders_menu")
        ],
        [KeyboardButton(text="📞 ارتباط با اپراتور", callback_data="contact_operator")]
    ]
    return OutgoingResponse(
        chat_id=message.from_user.id,
        text=WELCOME_TEXT,
        reply_markup=keyboard
    )


def handle_admin(message: IncomingMessage, access_control: AccessControl) -> OutgoingResponse:
    """
    پردازش دستور مدیریت (/admin).
    دسترسی بر اساس خط‌مشی Default-Deny کنترل می‌شود.
    """
    user_id = message.from_user.id
    if not access_control.is_admin(user_id):
        # ثبت رویداد امنیتی در لاگ بدون افشای ساختار پنل
        access_control.verify_admin_access(user_id, action_name="view_admin_panel")

    keyboard: List[List[KeyboardButton]] = [
        [KeyboardButton(text="📊 آمار و وضعیت سیستم", callback_data="admin_stats")],
        [KeyboardButton(text="📂 کارتابل درخواست‌ها", callback_data="admin_orders")],
        [KeyboardButton(text="🌐 وضعیت پایش سایت‌ها", callback_data="admin_monitors")]
    ]
    return OutgoingResponse(
        chat_id=user_id,
        text=ADMIN_PANEL_TEXT,
        reply_markup=keyboard
    )


def handle_orders(message: IncomingMessage, access_control: AccessControl, db_manager: Optional[Any] = None) -> OutgoingResponse:
    """
    پردازش مستقیم دستور کارتابل اپراتور (/orders).
    """
    user_id = message.from_user.id
    access_control.verify_admin_access(user_id, action_name="cmd_orders")

    if not db_manager:
        return OutgoingResponse(chat_id=user_id, text="پایگاه داده در دسترس نیست.")

    with db_manager.get_session() as session:
        from services.orders import OrderService
        from services.tracking import format_order_status_persian
        orders = OrderService.get_orders_for_operator(session)
        if not orders:
            return OutgoingResponse(
                chat_id=user_id,
                text="📂 <b>کارتابل سفارشات اپراتور</b>\n\nدر حال حاضر هیچ سفارشی در سامانه ثبت نشده است.",
                reply_markup=[[KeyboardButton(text="🔙 بازگشت به پنل مدیریت", callback_data="back_to_admin")]]
            )
        keyboard_orders: List[List[KeyboardButton]] = []
        orders_summary_lines = []
        for o in orders[:15]:
            status_meta = format_order_status_persian(o.status)
            btn_text = f"{status_meta['icon']} {o.tracking_code} | {o.service.title[:15]}"
            keyboard_orders.append([KeyboardButton(text=btn_text, callback_data=f"op_view_{o.id}")])
            orders_summary_lines.append(f"• <code>{o.tracking_code}</code> — {o.service.title} ({status_meta['title']})")

        keyboard_orders.append([KeyboardButton(text="🔙 بازگشت به پنل مدیریت", callback_data="back_to_admin")])
        orders_summary = "\n".join(orders_summary_lines)
        return OutgoingResponse(
            chat_id=user_id,
            text=f"📂 <b>کارتابل سفارشات اپراتور ({len(orders)} پرونده):</b>\n\n{orders_summary}\n\nجهت بررسی مدارک و تغییر وضعیت، پرونده موردنظر را انتخاب فرمایید:",
            reply_markup=keyboard_orders
        )


def handle_stats(message: IncomingMessage, access_control: AccessControl, db_manager: Optional[Any] = None) -> OutgoingResponse:
    """
    پردازش مستقیم دستور آمار سامانه (/stats).
    """
    user_id = message.from_user.id
    access_control.verify_admin_access(user_id, action_name="cmd_stats")

    if not db_manager:
        return OutgoingResponse(chat_id=user_id, text="پایگاه داده در دسترس نیست.")

    with db_manager.get_session() as session:
        from core.diagnostics import SystemDiagnostics
        diag = SystemDiagnostics.run_health_check(session)
        m = diag["metrics"]
        text = (
            f"📊 <b>آمار و وضعیت عمومی سامانه کافی نت لیمو</b>\n\n"
            f"🕒 <b>زمان جاری:</b> <code>{diag['shamsi_time']}</code>\n"
            f"🛡 <b>یکپارچگی دیتابیس:</b> <code>{diag['database_integrity']}</code>\n\n"
            f"👥 <b>تعداد کل کاربران:</b> {m['total_users']}\n"
            f"📋 <b>خدمات فعال:</b> {m['active_services']}\n"
            f"📦 <b>کل سفارشات:</b> {m['total_orders']}\n"
            f"⏳ <b>سفارشات در انتظار بررسی:</b> {m['pending_orders']}\n"
            f"⏰ <b>یادآورهای در نوبت:</b> {m['active_reminders']}\n"
            f"🌐 <b>سایت‌های تحت پایش:</b> {m['monitored_sites']}"
        )
        keyboard = [
            [KeyboardButton(text="📂 کارتابل سفارشات", callback_data="admin_orders")],
            [KeyboardButton(text="🌐 وضعیت پایش سایت‌ها", callback_data="admin_monitors")],
            [KeyboardButton(text="🔙 بازگشت به پنل مدیریت", callback_data="back_to_admin")]
        ]
        return OutgoingResponse(chat_id=user_id, text=text, reply_markup=keyboard)


def handle_health(message: IncomingMessage, access_control: AccessControl, db_manager: Optional[Any] = None) -> OutgoingResponse:
    """
    پردازش مستقیم دستور عیب‌یابی و پایش سلامت (/health).
    """
    user_id = message.from_user.id
    access_control.verify_admin_access(user_id, action_name="cmd_health")

    if not db_manager:
        return OutgoingResponse(chat_id=user_id, text="پایگاه داده در دسترس نیست.")

    with db_manager.get_session() as session:
        from core.diagnostics import SystemDiagnostics
        diag = SystemDiagnostics.run_health_check(session)
        health_icon = "🟢" if diag["status"] == "HEALTHY" else "🔴"
        text = (
            f"{health_icon} <b>گزارش سلامت و عیب‌یابی سامانه</b>\n\n"
            f"📌 <b>وضعیت کلی:</b> {diag['status']}\n"
            f"📅 <b>زمان سامانه (ایران):</b> <code>{diag['shamsi_time']}</code>\n"
            f"💾 <b>یکپارچگی پایگاه داده:</b> <code>{diag['database_integrity']}</code>\n\n"
            f"🔢 <b>شمارنده‌های موجودیت:</b>\n"
            f"• کاربران: {diag['metrics']['total_users']}\n"
            f"• سفارشات: {diag['metrics']['total_orders']} (در انتظار: {diag['metrics']['pending_orders']})\n"
            f"• یادآورها: {diag['metrics']['active_reminders']}\n"
            f"• سایت‌های پایش: {diag['metrics']['monitored_sites']}"
        )
        keyboard = [[KeyboardButton(text="🔙 بازگشت به پنل مدیریت", callback_data="back_to_admin")]]
        return OutgoingResponse(chat_id=user_id, text=text, reply_markup=keyboard)


def handle_backup(message: IncomingMessage, access_control: AccessControl, db_manager: Optional[Any] = None) -> OutgoingResponse:
    """
    پردازش مستقیم دستور نسخه پشتیبان امن (/backup).
    """
    user_id = message.from_user.id
    access_control.verify_admin_access(user_id, action_name="cmd_backup")

    if not db_manager:
        return OutgoingResponse(chat_id=user_id, text="پایگاه داده در دسترس نیست.")

    with db_manager.get_session() as session:
        from core.diagnostics import SystemDiagnostics
        snapshot = SystemDiagnostics.create_backup_snapshot(session)
        text = (
            f"💾 <b>گزارش تهیه نسخه پشتیبان (Backup Snapshot)</b>\n\n"
            f"📅 <b>زمان تهیه:</b> <code>{snapshot['created_at_shamsi']}</code>\n"
            f"🏷 <b>نسخه ساختار:</b> <code>{snapshot['version']}</code>\n\n"
            f"📊 <b>محتویات اسنپ‌شات امن:</b>\n"
            f"• رکورد کاربران: {len(snapshot['users'])}\n"
            f"• رکورد سفارشات: {len(snapshot['orders'])}\n"
            f"• رکورد یادآورها: {len(snapshot['reminders'])}\n"
            f"• سایت‌های پایش: {len(snapshot['monitors'])}\n\n"
            f"<i>کلیه داده‌های حساس و توکن‌ها طبق اصل محرمانگی فیلتر گردیده‌اند.</i>"
        )
        keyboard = [[KeyboardButton(text="🔙 بازگشت به پنل مدیریت", callback_data="back_to_admin")]]
        return OutgoingResponse(chat_id=user_id, text=text, reply_markup=keyboard)


def handle_help(message: IncomingMessage) -> OutgoingResponse:
    """پردازش دستور راهنما (/help)."""
    return OutgoingResponse(
        chat_id=message.from_user.id,
        text=HELP_TEXT
    )


def handle_unknown(message: IncomingMessage) -> OutgoingResponse:
    """پردازش پیام‌ها و دستورات ناشناخته."""
    return OutgoingResponse(
        chat_id=message.from_user.id,
        text=UNKNOWN_COMMAND_TEXT
    )
