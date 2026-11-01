"""
هندلرهای پردازش تعامل با دکمه‌های شیشه‌ای (Callback Query Handlers) سامانه «کافی نت لیمو».
این ماژول پیمایش منوها، دکمه‌های بازگشت، کاتالوگ پویا، ثبت سفارش و کارتابل اپراتور را مدیریت می‌کند.
"""

from typing import List, Optional
from bot.models import CallbackQuery, OutgoingResponse, KeyboardButton
from bot.handlers import WELCOME_TEXT, ADMIN_PANEL_TEXT, ACCESS_DENIED_TEXT
from bot.fsm import FSMManager
from core.security import AccessControl
from core.database import DatabaseManager
from services.catalog import CatalogService, HOUSING_TERMS_TEXT
from services.orders import OrderService
from services.reminders import ReminderService
from services.monitor import MonitorService
from services.notifications import NotificationService
from services.sheets_sync import GoogleSheetsSyncService
from services.tracking import format_order_status_persian, render_order_card, render_user_orders_list
from services.wallet import WalletService
from core.models import User
from core.validators import mask_sensitive_data


SERVICES_HEADER_TEXT = (
    "📋 <b>فهرست خدمات فعال کافی نت لیمو:</b>\n\n"
    "جهت مشاهده مدارک موردنیاز، مراحل و شرایط رسمی، یکی از خدمات زیر را انتخاب فرمایید:"
)

TRACKING_PROMPT_TEXT = (
    "🔍 <b>استعلام و پیگیری وضعیت پرونده:</b>\n\n"
    "لطفاً <b>کد رهگیری یکتا</b>ی خود را ارسال فرمایید (مثال: <code>LIMO-1405-88219</code>):\n\n"
    "<i>همچنین می‌توانید در هر زمان دستور /cancel را برای انصراف ارسال فرمایید.</i>"
)
TRACKING_INFO_TEXT = TRACKING_PROMPT_TEXT

REMINDERS_INFO_TEXT = (
    "⏰ <b>یادآورهای هوشمند مهلت‌ها:</b>\n\n"
    "با تنظیم یادآور تقویمی بر مبنای تاریخ شمسی، مهلت‌های ثبت‌نام، تمدید و تحویل مدارک "
    "را به موقع دریافت خواهید کرد."
)

OPERATOR_CONTACT_TEXT = (
    "📞 <b>هماهنگی با اپراتور:</b>\n\n"
    "درخواست‌های ثبت‌شده در کافی نت لیمو مستقیماً به اپراتور ارجاع شده و "
    "هماهنگی و تکمیل مراحل به صورت مستقیم انجام می‌پذیرد."
)

ADMIN_ORDERS_TEXT = (
    "📂 <b>کارتابل سفارشات اپراتور:</b>\n\n"
    "در حال حاضر هیچ سفارشی در کارتابل موجود نیست."
)

ADMIN_STATS_TEXT = (
    "📊 <b>آمار و وضعیت سامانه کافی نت لیمو:</b>\n\n"
    "• وضعیت هسته بات: آنلاین و فعال\n"
    "• منطقه زمانی فعال: Asia/Tehran\n"
    "• سطح امنیت: خط‌مشی Default-Deny فعال\n"
    "• درگاه پرداخت آنلاین: غیرفعال (نسخه اول)"
)

ADMIN_MONITORS_TEXT = (
    "🌐 <b>وضعیت پایش هوشمند سایت‌ها:</b>\n\n"
    "فهرست سایت‌های هدف ثبت شده است؛ فعال‌سازی پایش دوره‌ای در فاز اختصاصی انجام خواهد شد."
)


def _back_to_main_markup() -> List[List[KeyboardButton]]:
    """ایجاد دکمه بازگشت به منوی اصلی."""
    return [[KeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]]


def _back_to_admin_markup() -> List[List[KeyboardButton]]:
    """ایجاد دکمه بازگشت به پنل مدیریت."""
    return [[KeyboardButton(text="🔙 بازگشت به پنل مدیریت", callback_data="back_to_admin")]]


def _render_operator_order_view(order, chat_id: int) -> OutgoingResponse:
    """تولید کارت اطلاعات کامل سفارش برای بررسی و اقدام اپراتور."""
    status_meta = format_order_status_persian(order.status)
    created_str = order.created_at.strftime("%Y/%m/%d %H:%M UTC") if order.created_at else "—"

    fields_lines = []
    for k, v in (order.form_data or {}).items():
        fields_lines.append(f"• <b>{k}:</b> <code>{v}</code>")

    docs_count = len(order.documents) if order.documents else 0
    docs_details = ""
    if order.documents:
        docs_lines = [f"• [{d.file_type}] {d.file_name or 'مدرک ارسالی'} (شناسه: <code>{d.file_id[:12]}...</code>)" for d in order.documents]
        docs_details = "\n" + "\n".join(docs_lines)

    order_view_text = (
        f"📂 <b>جزئیات پرونده {order.tracking_code}</b>\n\n"
        f"👤 <b>متقاضی:</b> {order.user.full_name} (شناسه: <code>{order.user.telegram_id}</code>)\n"
        f"📋 <b>خدمت درخواستی:</b> {order.service.title}\n"
        f"📌 <b>وضعیت کنونی:</b> {status_meta['icon']} {status_meta['title']}\n"
        f"📅 <b>زمان ثبت:</b> <code>{created_str}</code>\n"
        f"📎 <b>مدارک پیوست:</b> {docs_count} مدرک{docs_details}\n\n"
        f"📝 <b>اطلاعات ثبت‌شده:</b>\n"
        + ("\n".join(fields_lines) if fields_lines else "—")
        + f"\n\n💬 <b>یادداشت اپراتور:</b>\n<i>{order.operator_notes or '—'}</i>\n\n"
        "جهت تغییر وضعیت یا ثبت یادداشت، یکی از گزینه‌های زیر را انتخاب فرمایید:"
    )

    keyboard = [
        [
            KeyboardButton(text="🟢 تأیید و شروع", callback_data=f"op_setstatus_{order.id}_APPROVED"),
            KeyboardButton(text="⚠️ اعلام نقص مدرک", callback_data=f"op_prompt_{order.id}_NEED_INFO")
        ],
        [
            KeyboardButton(text="✅ تکمیل پرونده", callback_data=f"op_prompt_{order.id}_COMPLETED"),
            KeyboardButton(text="❌ لغو پرونده", callback_data=f"op_prompt_{order.id}_CANCELLED")
        ],
        [KeyboardButton(text="🔙 بازگشت به کارتابل سفارشات", callback_data="admin_orders")]
    ]
    return OutgoingResponse(
        chat_id=chat_id,
        text=order_view_text,
        reply_markup=keyboard
    )


def handle_callback_query(
    query: CallbackQuery,
    access_control: AccessControl,
    db_manager: Optional[DatabaseManager] = None,
    fsm_manager: Optional[FSMManager] = None
) -> OutgoingResponse:
    """
    مسیریابی و پردازش کالبک‌های دکمه‌های شیشه‌ای با اتصال پویا به دیتابیس، FSM و کارتابل اپراتور.
    """
    user_id = query.from_user.id
    chat_id = query.message.from_user.id if query.message else user_id
    data = query.data or ""

    # بررسی و انسداد امنیتی تمامی کالبک‌های نیازمند صلاحیت مدیریت و اپراتوری
    if data.startswith("admin_") or data.startswith("op_") or data == "back_to_admin":
        if not access_control.is_admin(user_id):
            access_control.verify_admin_access(user_id, action_name=f"callback_{data}")
            return OutgoingResponse(
                chat_id=chat_id,
                text=ACCESS_DENIED_TEXT,
                callback_alert="خطای دسترسی: شما مجاز به مشاهده یا انجام این عملیات نیستید."
            )

    # کارتابل سفارشات اپراتور (فاز ۶)
    if data == "admin_orders":
        if db_manager:
            with db_manager.get_session() as session:
                orders = OrderService.get_orders_for_operator(session)
                if not orders:
                    return OutgoingResponse(
                        chat_id=chat_id,
                        text=ADMIN_ORDERS_TEXT,
                        reply_markup=_back_to_admin_markup()
                    )

                keyboard_orders: List[List[KeyboardButton]] = []
                orders_summary_lines = []
                for o in orders[:15]:  # نمایش حداکثر ۱۵ سفارش اخیر
                    status_meta = format_order_status_persian(o.status)
                    btn_text = f"{status_meta['icon']} {o.tracking_code} | {o.service.title[:15]}"
                    keyboard_orders.append([
                        KeyboardButton(text=btn_text, callback_data=f"op_view_{o.id}")
                    ])
                    orders_summary_lines.append(f"• <code>{o.tracking_code}</code> — {o.service.title} ({status_meta['title']})")

                keyboard_orders.append([KeyboardButton(text="🔙 بازگشت به پنل مدیریت", callback_data="back_to_admin")])
                orders_summary = "\n".join(orders_summary_lines)

                return OutgoingResponse(
                    chat_id=chat_id,
                    text=f"📂 <b>کارتابل سفارشات اپراتور ({len(orders)} پرونده):</b>\n\n{orders_summary}\n\nجهت بررسی مدارک و تغییر وضعیت، پرونده موردنظر را انتخاب فرمایید:",
                    reply_markup=keyboard_orders
                )

        return OutgoingResponse(
            chat_id=chat_id,
            text=ADMIN_ORDERS_TEXT,
            reply_markup=_back_to_admin_markup()
        )

    # مشاهده جزییات یک پرونده توسط اپراتور
    elif data.startswith("op_view_"):
        order_id = int(data[8:])
        if db_manager:
            with db_manager.get_session() as session:
                order = OrderService.get_order_by_id(session, order_id)
                if order:
                    return _render_operator_order_view(order, chat_id)

        return OutgoingResponse(
            chat_id=chat_id,
            text="پرونده مورد نظر یافت نشد.",
            reply_markup=[[KeyboardButton(text="🔙 بازگشت به کارتابل", callback_data="admin_orders")]]
        )

    # تغییر وضعیت مستقیم توسط اپراتور (مانند APPROVED)
    elif data.startswith("op_setstatus_"):
        parts = data.split("_", 3)
        order_id = int(parts[2])
        new_status = parts[3]
        if db_manager:
            with db_manager.get_session() as session:
                order = OrderService.update_order_status(
                    session=session,
                    order_id=order_id,
                    new_status=new_status,
                    actor_telegram_id=user_id,
                    note="تایید مدارک و شروع انجام توسط اپراتور"
                )
                resp = _render_operator_order_view(order, chat_id)
                resp.callback_alert = "وضعیت پرونده به «تاییدشده» تغییر یافت."
                resp.notification = NotificationService.create_customer_status_alert(
                    order=order,
                    new_status=new_status,
                    note="تایید مدارک و شروع انجام توسط اپراتور"
                )
                return resp

    # شروع دریافت توضیحات اپراتور برای تغییر وضعیت (NEED_INFO, COMPLETED, CANCELLED)
    elif data.startswith("op_prompt_"):
        parts = data.split("_", 3)
        order_id = int(parts[2])
        target_status = parts[3]
        if fsm_manager:
            fsm_manager.start_operator_note_flow(user_id, order_id, target_status)
            status_meta = format_order_status_persian(target_status)
            prompt_text = (
                f"✍️ <b>ثبت یادداشت اپراتور برای وضعیت «{status_meta['title']}»:</b>\n\n"
                "لطفاً متن توضیحات، نواقص یا پیام خود را برای این پرونده ارسال فرمایید:\n\n"
                "<i>یا برای انصراف، دستور /cancel را ارسال کنید.</i>"
            )
            return OutgoingResponse(
                chat_id=chat_id,
                text=prompt_text,
                reply_markup=[[KeyboardButton(text="❌ انصراف", callback_data=f"op_view_{order_id}")]]
            )

    # نمایش منوی دسته‌بندی‌های ۶ گانه مصوب خدمات و دسترسی سریع
    elif data == "services_list":
        keyboard_cats = [
            [KeyboardButton(text="🌐 امور اتباع و کدها", callback_data="cat_ALIEN_AND_CODES")],
            [KeyboardButton(text="🎓 خدمات دانشگاهی و آزمون‌ها", callback_data="cat_UNIVERSITY_SERVICES")],
            [KeyboardButton(text="✈️ بلیت هواپیما، قطار و اتوبوس", callback_data="cat_TICKETS_TRAVEL")],
            [KeyboardButton(text="🏛 سایر خدمات اینترنتی و اداری", callback_data="cat_GOVERNMENT_INTERNET")],
            [KeyboardButton(text="📂 درخواست‌های من، کیف پول و پیگیری", callback_data="cat_PORTAL_AND_WALLET")],
            [KeyboardButton(text="💬 گفت‌وگو با پشتیبانی و ارتباط با ما", callback_data="cat_SUPPORT_AND_CONTACT")],
            [KeyboardButton(text="📌 استعلام تاییدیه تحصیلی و کد صحت", callback_data="svc_EMT_VERIFICATION")],
            [KeyboardButton(text="📌 ثبت‌نام آزمون‌های سازمان سنجش", callback_data="svc_SANJESH_REGISTRATION")],
            [KeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
        ]
        return OutgoingResponse(
            chat_id=chat_id,
            text=SERVICES_HEADER_TEXT,
            reply_markup=keyboard_cats
        )

    # پیمایش دسته‌بندی‌های کاتالوگ
    elif data.startswith("cat_"):
        cat_code = data[4:]
        if cat_code == "PORTAL_AND_WALLET":
            keyboard_pw = [
                [KeyboardButton(text="📂 درخواست‌های من", callback_data="my_orders")],
                [KeyboardButton(text="💳 کیف پول من", callback_data="wallet_menu")],
                [KeyboardButton(text="🔍 پیگیری با کد رهگیری", callback_data="order_tracking")],
                [KeyboardButton(text="🔙 بازگشت به دسته‌بندی‌ها", callback_data="services_list")]
            ]
            return OutgoingResponse(
                chat_id=chat_id,
                text="📂 <b>درخواست‌های من، کیف پول و پیگیری سفارش:</b>\n\nلطفاً بخش مورد نظر را انتخاب فرمایید:",
                reply_markup=keyboard_pw
            )
        elif cat_code == "SUPPORT_AND_CONTACT":
            keyboard_sc = [
                [KeyboardButton(text="💬 گفت‌وگو با پشتیبانی", callback_data="contact_operator")],
                [KeyboardButton(text="📢 راه‌های ارتباطی با ما", callback_data="channels_info")],
                [KeyboardButton(text="🔙 بازگشت به دسته‌بندی‌ها", callback_data="services_list")]
            ]
            return OutgoingResponse(
                chat_id=chat_id,
                text="💬 <b>پشتیبانی و ارتباط با کافی‌نت لیمو:</b>\n\nجهت ارتباط مستقیم یا دریافت شبکه‌های ارتباطی انتخاب فرمایید:",
                reply_markup=keyboard_sc
            )
        else:
            if db_manager:
                with db_manager.get_session() as session:
                    services = CatalogService.get_services_by_category(session, cat_code)
                    keyboard_svcs = []
                    for svc in services:
                        keyboard_svcs.append([
                            KeyboardButton(text=f"📌 {svc.title}", callback_data=f"svc_{svc.code}")
                        ])
                    keyboard_svcs.append([KeyboardButton(text="🔙 بازگشت به دسته‌بندی‌ها", callback_data="services_list")])
                    keyboard_svcs.append([KeyboardButton(text="🏠 منوی اصلی", callback_data="back_to_main")])
                    return OutgoingResponse(
                        chat_id=chat_id,
                        text="📋 <b>فهرست خدمات دسته‌بندی انتخابی:</b>\n\nجهت مشاهده شرایط و ثبت درخواست، خدمت مورد نظر را انتخاب فرمایید:",
                        reply_markup=keyboard_svcs
                    )

            return OutgoingResponse(
                chat_id=chat_id,
                text="خطا در بازیابی خدمات دسته‌بندی.",
                reply_markup=[[KeyboardButton(text="🔙 بازگشت به دسته‌بندی‌ها", callback_data="services_list")]]
            )

    # نمایش جزئیات یک خدمت انتخابی (بدون لینک خارجی در مسیر ثبت سفارش)
    elif data.startswith("svc_"):
        service_code = data[4:]
        if service_code == "HOUSING_TRACKING_CODE":
            keyboard_housing = [
                [KeyboardButton(text="✅ شرایط را خواندم و می‌پذیرم", callback_data="housing_terms_accepted")],
                [KeyboardButton(text="🔙 بازگشت به دسته‌بندی", callback_data="cat_ALIEN_AND_CODES")],
                [KeyboardButton(text="🏠 منوی اصلی", callback_data="back_to_main")]
            ]
            return OutgoingResponse(
                chat_id=chat_id,
                text=HOUSING_TERMS_TEXT,
                reply_markup=keyboard_housing
            )

        if db_manager:
            with db_manager.get_session() as session:
                service = CatalogService.get_service_by_code(session, service_code)
                if service:
                    docs_text = "\n".join([f"• {doc}" for doc in (service.required_docs or [])])
                    fields_text = "\n".join([f"• {field_desc}" for field_desc in (service.required_fields or {}).values()])
                    details_text = (
                        f"<b>{service.title}</b>\n\n"
                        f"{service.description}\n\n"
                        f"🔗 <b>سامانه مرجع:</b> <code>{service.official_url or 'اعلامی سازمان'}</code> (ثبت مستقیم داخل ربات)\n\n"
                        f"📑 <b>مدارک موردنیاز:</b>\n{docs_text or '—'}\n\n"
                        f"📝 <b>اطلاعات موردنیاز:</b>\n{fields_text or '—'}"
                    )
                    cat_code = service.category.code if service.category else "services_list"
                    keyboard_svc: List[List[KeyboardButton]] = [
                        [KeyboardButton(text="📝 ثبت درخواست این خدمت", callback_data=f"order_start_{service.code}")],
                        [KeyboardButton(text="🔙 بازگشت به دسته‌بندی", callback_data=f"cat_{cat_code}")],
                        [KeyboardButton(text="🏠 منوی اصلی", callback_data="back_to_main")]
                    ]
                    return OutgoingResponse(
                        chat_id=chat_id,
                        text=details_text,
                        reply_markup=keyboard_svc
                    )

        return OutgoingResponse(
            chat_id=chat_id,
            text="اطلاعات خدمت درخواستی یافت نشد.",
            reply_markup=_back_to_main_markup()
        )

    # پذیرش شرایط کد رهگیری مسکن و ورود به فرم
    elif data == "housing_terms_accepted":
        if db_manager and fsm_manager:
            with db_manager.get_session() as session:
                service = CatalogService.get_service_by_code(session, "HOUSING_TRACKING_CODE")
                if service:
                    field_keys = list(service.required_fields.keys())
                    fsm_manager.start_order_flow(user_id, service.code, field_keys)
                    state = fsm_manager.get_state(user_id)
                    if state:
                        state.terms_accepted = True
                    first_field_key = field_keys[0]
                    first_label = service.required_fields.get(first_field_key, first_field_key)
                    prompt_text = (
                        f"📝 <b>ثبت درخواست: {service.title}</b>\n\n"
                        f"مرحله ۱ از {len(field_keys)}:\n"
                        f"لطفاً <b>{first_label}</b> را وارد فرمایید:"
                    )
                    keyboard_order = [
                        [KeyboardButton(text="❌ انصراف", callback_data="order_cancel")]
                    ]
                    return OutgoingResponse(
                        chat_id=chat_id,
                        text=prompt_text,
                        reply_markup=keyboard_order
                    )

        return OutgoingResponse(
            chat_id=chat_id,
            text="امکان شروع ثبت درخواست مسکن در حال حاضر مهیا نیست.",
            reply_markup=_back_to_main_markup()
        )

    # انتخاب گزینه تأمین دو شاهد توسط کافی‌نت (تعرفه ۳۵۰،۰۰۰ تومان)
    elif data == "witness_choice_limo":
        if fsm_manager and db_manager:
            state = fsm_manager.get_state(user_id)
            if state and state.service_code == "HOUSING_TRACKING_CODE":
                state.collected_data["witness_mode"] = "تأمین توسط کافی‌نت لیمو (تعرفه ۳۵۰،۰۰۰ تومان)"
                state.collected_data["witness_fee"] = "۳۵۰،۰۰۰ تومان (۳،۵۰۰،۰۰۰ ریال)"
                state.current_field_index += 1

                # انتقال به مرحله تایید نهایی
                state.step = "CONFIRMATION"
                with db_manager.get_session() as session:
                    service = CatalogService.get_service_by_code(session, state.service_code)
                    svc_title = service.title if service else state.service_code

                summary_lines = []
                for k, v in state.collected_data.items():
                    label = service.required_fields.get(k, k) if service else k
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
                    + "\n\n⚠️ <i>لطفاً صحت اطلاعات فوق را بررسی فرمایید. در صورت تأیید، پرونده ثبت و به کارتابل اپراتور ارسال می‌گردد.</i>"
                )
                keyboard_confirm = [
                    [KeyboardButton(text="✅ تأیید و ثبت نهایی درخواست", callback_data="order_confirm")],
                    [KeyboardButton(text="🔙 مرحله قبل (ویرایش)", callback_data="order_step_back")],
                    [KeyboardButton(text="❌ انصراف و لغو", callback_data="order_cancel")]
                ]
                return OutgoingResponse(
                    chat_id=chat_id,
                    text=preview_text,
                    reply_markup=keyboard_confirm
                )

        return OutgoingResponse(chat_id=chat_id, text="جلسه کاری منقضی شده است.", reply_markup=_back_to_main_markup())

    # انتخاب گزینه معرفی شاهد توسط خود متقاضی
    elif data == "witness_choice_self":
        if fsm_manager:
            state = fsm_manager.get_state(user_id)
            if state and state.service_code == "HOUSING_TRACKING_CODE":
                prompt_text = (
                    "👥 <b>مشخصات دو شاهد معتبر ایرانی:</b>\n\n"
                    "لطفاً مشخصات کامل دو شاهد (شامل نام و نام خانوادگی، کد ملی ۱۰ رقمی و شماره تلفن همراه هر دو شاهد) را در یک پیام ارسال فرمایید:"
                )
                keyboard_witness = [
                    [KeyboardButton(text="🔙 مرحله قبل", callback_data="order_step_back")],
                    [KeyboardButton(text="❌ انصراف", callback_data="order_cancel")]
                ]
                return OutgoingResponse(
                    chat_id=chat_id,
                    text=prompt_text,
                    reply_markup=keyboard_witness
                )

        return OutgoingResponse(chat_id=chat_id, text="جلسه کاری منقضی شده است.", reply_markup=_back_to_main_markup())

    # دکمه بازگشت به مرحله قبل در فرم FSM
    elif data == "order_step_back":
        if fsm_manager and db_manager:
            state = fsm_manager.get_state(user_id)
            if state and fsm_manager.step_back(user_id):
                with db_manager.get_session() as session:
                    service = CatalogService.get_service_by_code(session, state.service_code)
                    if service and state.step == "FIELD_INPUT":
                        curr_key = state.field_keys[state.current_field_index]
                        label = service.required_fields.get(curr_key, curr_key)
                        if curr_key == "witness_mode":
                            prompt_text = (
                                f"📝 <b>مرحله {state.current_field_index + 1} از {len(state.field_keys)}:</b>\n\n"
                                "👥 <b>نحوه معرفی دو شاهد ایرانی:</b>\n\n"
                                "برای صدور کد رهگیری، مشخصات دو شاهد ایرانی الزامی است.\n"
                                "لطفاً یکی از روش‌های زیر را انتخاب فرمایید:"
                            )
                            keyboard = [
                                [KeyboardButton(text="👥 خودم دو شاهد معرفی می‌کنم", callback_data="witness_choice_self")],
                                [KeyboardButton(text="🤝 تأمین دو شاهد توسط کافی‌نت (تعرفه ۳۵۰ هزار تومان)", callback_data="witness_choice_limo")],
                                [KeyboardButton(text="🔙 مرحله قبل", callback_data="order_step_back")],
                                [KeyboardButton(text="❌ انصراف", callback_data="order_cancel")]
                            ]
                            return OutgoingResponse(chat_id=chat_id, text=prompt_text, reply_markup=keyboard)
                        else:
                            prompt_text = (
                                f"📝 <b>ثبت درخواست: {service.title}</b>\n\n"
                                f"مرحله {state.current_field_index + 1} از {len(state.field_keys)}:\n"
                                f"لطفاً <b>{label}</b> را وارد فرمایید:"
                            )
                            buttons = []
                            if state.current_field_index > 0:
                                buttons.append([KeyboardButton(text="🔙 مرحله قبل", callback_data="order_step_back")])
                            buttons.append([KeyboardButton(text="❌ انصراف", callback_data="order_cancel")] )
                            return OutgoingResponse(chat_id=chat_id, text=prompt_text, reply_markup=buttons)

            return OutgoingResponse(
                chat_id=chat_id,
                text="شما در مرحله اول قرار دارید. جهت انصراف دکمه زیر را انتخاب فرمایید:",
                reply_markup=[[KeyboardButton(text="❌ انصراف", callback_data="order_cancel")]]
            )

        return OutgoingResponse(
            chat_id=chat_id,
            text="عملیاتی برای بازگشت وجود ندارد.",
            reply_markup=_back_to_main_markup()
        )

    # راه‌های ارتباطی و کانال‌های رسمی کافی‌نت لیمو
    elif data == "channels_info":
        channels_text = (
            "📢 <b>راه‌های ارتباطی و کانال‌های رسمی کافی نت لیمو:</b>\n\n"
            "• <b>کانال تلگرام:</b> @limocafe\n"
            "• <b>پیام‌رسان ایتا:</b> @limocafe\n"
            "• <b>پیام‌رسان روبیکا:</b> @limocafe\n"
            "• <b>پیام‌رسان بله:</b> @limocafe\n"
            "• <b>صفحه اینستاگرام:</b> @limocafe\n"
            "• <b>پشتیبانی مستقیم:</b> گفت‌وگوی داخل ربات (/chat)\n\n"
            "⏰ ساعت کاری: همه‌روزه از ۸:۰۰ صبح الی ۲۱:۰۰ شب"
        )
        keyboard_channels = [
            [KeyboardButton(text="💬 گفت‌وگو با پشتیبانی", callback_data="contact_operator")],
            [KeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
        ]
        return OutgoingResponse(
            chat_id=chat_id,
            text=channels_text,
            reply_markup=keyboard_channels
        )

    # آغاز فرآیند مرحله‌ای ثبت درخواست (FSM)
    elif data.startswith("order_start_"):
        service_code = data[12:]
        if db_manager and fsm_manager:
            with db_manager.get_session() as session:
                service = CatalogService.get_service_by_code(session, service_code)
                if service:
                    field_keys = list(service.required_fields.keys())
                    if field_keys:
                        fsm_manager.start_order_flow(user_id, service.code, field_keys)
                        first_field_key = field_keys[0]
                        first_label = service.required_fields.get(first_field_key, first_field_key)
                        prompt_text = (
                            f"📝 <b>ثبت درخواست: {service.title}</b>\n\n"
                            f"مرحله ۱ از {len(field_keys)}:\n"
                            f"لطفاً <b>{first_label}</b> را وارد فرمایید:"
                        )
                        keyboard_order: List[List[KeyboardButton]] = [
                            [KeyboardButton(text="❌ انصراف", callback_data="order_cancel")]
                        ]
                        return OutgoingResponse(
                            chat_id=chat_id,
                            text=prompt_text,
                            reply_markup=keyboard_order
                        )

        return OutgoingResponse(
            chat_id=chat_id,
            text="امکان شروع ثبت درخواست در حال حاضر مهیا نیست.",
            reply_markup=_back_to_main_markup()
        )

    # انصراف از فرآیند جاری
    elif data == "order_cancel":
        if fsm_manager:
            fsm_manager.clear_state(user_id)
        return OutgoingResponse(
            chat_id=chat_id,
            text="❌ فرآیند ثبت درخواست لغو گردید و اطلاعات وارد شده پاک شد.",
            reply_markup=_back_to_main_markup()
        )

    # تایید نهایی و ثبت رسمی در پایگاه داده
    elif data == "order_confirm":
        if fsm_manager and db_manager:
            state = fsm_manager.get_state(user_id)
            if state and state.step == "CONFIRMATION" and state.service_code:
                with db_manager.get_session() as session:
                    user_record = CatalogService.get_or_create_user(
                        session,
                        telegram_id=query.from_user.id,
                        full_name=f"{query.from_user.first_name} {query.from_user.last_name or ''}".strip(),
                        username=query.from_user.username
                    )
                    service = CatalogService.get_service_by_code(session, state.service_code)
                    if service:
                        order = OrderService.create_order(
                            session=session,
                            user_id=user_record.id,
                            service_id=service.id,
                            form_data=state.collected_data,
                            actor_telegram_id=query.from_user.id
                        )
                        # ذخیره مدارک پیوست در دیتابیس
                        for doc_item in (state.collected_docs or []):
                            OrderService.attach_document(
                                session=session,
                                order_id=order.id,
                                file_id=doc_item["file_id"],
                                file_name=doc_item.get("file_name"),
                                file_type=doc_item.get("file_type", "DOCUMENT"),
                                file_size=doc_item.get("file_size")
                            )

                        tracking_code = order.tracking_code
                        fsm_manager.clear_state(user_id)

                        success_text = (
                            "🎉 <b>درخواست شما با موفقیت ثبت گردید!</b>\n\n"
                            f"📋 <b>خدمت درخواستی:</b> {service.title}\n"
                            f"🔖 <b>کد رهگیری یکتا:</b> <code>{tracking_code}</code>\n"
                            f"⏳ <b>وضعیت اولیه:</b> در انتظار بررسی اپراتور\n\n"
                            "💬 <b>اقدام بعدی:</b> اپراتور کافی نت لیمو درخواست شما را بررسی "
                            "کرده و جهت هماهنگی با شما ارتباط خواهد گرفت. لطفاً کد رهگیری خود را یادداشت فرمایید."
                        )
                        return OutgoingResponse(
                            chat_id=chat_id,
                            text=success_text,
                            reply_markup=_back_to_main_markup()
                        )

        return OutgoingResponse(
            chat_id=chat_id,
            text="جلسه کاری شما منقضی شده است. لطفاً فرآیند ثبت درخواست را مجدداً آغاز فرمایید.",
            reply_markup=_back_to_main_markup()
        )

    # استعلام کد رهگیری
    elif data == "order_tracking":
        if fsm_manager:
            fsm_manager.start_tracking_flow(user_id)
        keyboard_tracking = [
            [KeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")],
            [KeyboardButton(text="📂 مشاهده لیست پرونده‌های من", callback_data="my_orders")]
        ]
        return OutgoingResponse(
            chat_id=chat_id,
            text=TRACKING_PROMPT_TEXT,
            reply_markup=keyboard_tracking
        )

    # پرتال پرونده‌های من
    elif data == "my_orders":
        if db_manager:
            with db_manager.get_session() as session:
                orders = OrderService.get_user_orders_by_telegram_id(session, user_id)
                text = render_user_orders_list(orders)
                buttons: List[List[KeyboardButton]] = []
                for o in orders[:5]:
                    st = format_order_status_persian(o.status)
                    svc_title = o.service.title[:15] if o.service else ""
                    buttons.append([KeyboardButton(
                        text=f"{st['icon']} {o.tracking_code} ({svc_title})",
                        callback_data=f"track_code_{o.tracking_code}"
                    )])
                buttons.append([KeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")])
                return OutgoingResponse(chat_id=chat_id, text=text, reply_markup=buttons)

    # استعلام مستقیم پرونده از طریق دکمه‌های پرتال من
    elif data.startswith("track_code_"):
        code = data.replace("track_code_", "").strip()
        if db_manager:
            with db_manager.get_session() as session:
                order = OrderService.get_order_by_tracking_code(session, code)
                if not order:
                    return OutgoingResponse(
                        chat_id=chat_id,
                        text=f"❌ پرونده‌ای با کد رهگیری <code>{code}</code> یافت نشد.",
                        reply_markup=_back_to_main_markup()
                    )
                is_admin_or_op = access_control.is_admin(user_id) if access_control else False
                is_auth, card_text = render_order_card(order, user_id, is_admin_or_op)
                return OutgoingResponse(
                    chat_id=chat_id,
                    text=card_text,
                    reply_markup=_back_to_main_markup()
                )

    # کیف پول و حساب مالی
    elif data == "wallet_menu":
        if db_manager:
            with db_manager.get_session() as session:
                user = session.query(User).filter_by(telegram_id=user_id).first()
                if not user:
                    user = User(telegram_id=user_id, full_name="مشتری")
                    session.add(user)
                    session.commit()
                wallet = WalletService.get_or_create_wallet(session, user.id)
                history = WalletService.get_transaction_history(session, user.id, limit=5)
                card_text = WalletService.format_wallet_card(wallet, history)
                buttons = [
                    [KeyboardButton(text="💬 هماهنگی شارژ با پشتیبانی", callback_data="contact_operator")],
                    [KeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
                ]
                return OutgoingResponse(chat_id=chat_id, text=card_text, reply_markup=buttons)

    elif data == "reminders_menu":
        keyboard_rem = [
            [KeyboardButton(text="➕ تنظیم یادآور جدید", callback_data="rem_new")],
            [KeyboardButton(text="📋 یادآورهای فعال من", callback_data="rem_list")],
            [KeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
        ]
        return OutgoingResponse(
            chat_id=chat_id,
            text=REMINDERS_INFO_TEXT,
            reply_markup=keyboard_rem
        )

    elif data == "rem_new":
        if fsm_manager:
            fsm_manager.start_reminder_flow(user_id)
        prompt_text = (
            "⏰ <b>تنظیم یادآور هوشمند مهلت:</b>\n\n"
            "لطفاً <b>عنوان یا موضوع یادآور</b> را ارسال فرمایید (مثال: <code>مهلت ثبت‌نام کنکور سراسری</code>):\n\n"
            "<i>یا برای انصراف، دستور /cancel را ارسال فرمایید.</i>"
        )
        return OutgoingResponse(
            chat_id=chat_id,
            text=prompt_text,
            reply_markup=[[KeyboardButton(text="❌ انصراف", callback_data="reminders_menu")]]
        )

    elif data == "rem_list":
        if db_manager:
            with db_manager.get_session() as session:
                user_rec = CatalogService.get_or_create_user(
                    session=session,
                    telegram_id=user_id,
                    full_name=f"{query.from_user.first_name} {query.from_user.last_name or ''}".strip(),
                    username=query.from_user.username
                )
                reminders = ReminderService.get_user_reminders(session, user_id=user_rec.id, active_only=True)
                if not reminders:
                    return OutgoingResponse(
                        chat_id=chat_id,
                        text="📋 <b>یادآورهای فعال شما:</b>\n\nدر حال حاضر هیچ یادآور فعالی برای شما ثبت نشده است.",
                        reply_markup=[
                            [KeyboardButton(text="➕ تنظیم یادآور جدید", callback_data="rem_new")],
                            [KeyboardButton(text="🔙 بازگشت به بخش یادآورها", callback_data="reminders_menu")]
                        ]
                    )

                lines = [f"📋 <b>فهرست یادآورهای فعال شما ({len(reminders)} مورد):</b>\n"]
                kb: List[List[KeyboardButton]] = []
                for idx, r in enumerate(reminders, 1):
                    lines.append(f"{idx}. 📌 <b>{r.title}</b>\n   📅 موعد سررسید: <code>{r.shamsi_date}</code>")
                    kb.append([KeyboardButton(text=f"🗑 حذف: {r.title[:20]}", callback_data=f"rem_del_{r.id}")])

                kb.append([
                    KeyboardButton(text="➕ تنظیم یادآور جدید", callback_data="rem_new"),
                    KeyboardButton(text="🔙 بازگشت به بخش یادآورها", callback_data="reminders_menu")
                ])
                return OutgoingResponse(
                    chat_id=chat_id,
                    text="\n".join(lines),
                    reply_markup=kb
                )

        return OutgoingResponse(
            chat_id=chat_id,
            text="پایگاه داده در دسترس نیست.",
            reply_markup=_back_to_main_markup()
        )

    elif data.startswith("rem_del_"):
        reminder_id = int(data[8:])
        if db_manager:
            with db_manager.get_session() as session:
                user_rec = CatalogService.get_or_create_user(
                    session=session,
                    telegram_id=user_id,
                    full_name=f"{query.from_user.first_name} {query.from_user.last_name or ''}".strip(),
                    username=query.from_user.username
                )
                deleted = ReminderService.delete_reminder(session, reminder_id=reminder_id, user_id=user_rec.id)
                if deleted:
                    return OutgoingResponse(
                        chat_id=chat_id,
                        text="🗑 یادآور موردنظر با موفقیت حذف گردید.",
                        callback_alert="یادآور با موفقیت حذف شد.",
                        reply_markup=[
                            [KeyboardButton(text="📋 مشاهده یادآورهای فعال", callback_data="rem_list")],
                            [KeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
                        ]
                    )

        return OutgoingResponse(
            chat_id=chat_id,
            text="یادآور موردنظر یافت نشد یا قبلاً حذف گردیده است.",
            callback_alert="یادآور یافت نشد.",
            reply_markup=[[KeyboardButton(text="📋 مشاهده یادآورهای فعال", callback_data="rem_list")]]
        )
    elif data == "contact_operator":
        keyboard = [
            [KeyboardButton(text="💬 آغاز گفتگوی مستقیم (چت زنده)", callback_data="start_support_chat")],
            [KeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
        ]
        return OutgoingResponse(
            chat_id=chat_id,
            text=OPERATOR_CONTACT_TEXT,
            reply_markup=keyboard
        )
    elif data == "start_support_chat":
        if fsm_manager:
            fsm_manager.start_chat_flow(user_id)
        return OutgoingResponse(
            chat_id=chat_id,
            text=(
                "💬 <b>شما به سامانه گفتگوی مستقیم با پشتیبانی کافی‌نت لیمو متصل شدید.</b>\n\n"
                "لطفاً پیام، سوال یا فایل‌های خود را در همین صفحه ارسال فرمایید. "
                "اپراتور به زودی پاسخ شما را ارسال خواهد کرد.\n\n"
                "<i>(جهت خروج از چت و بازگشت به منو، دکمه زیر را لمس کرده یا دستور /endchat را بفرستید)</i>"
            ),
            reply_markup=[[KeyboardButton(text="❌ پایان گفتگو و بازگشت", callback_data="exit_chat")]]
        )
    elif data == "exit_chat":
        if fsm_manager:
            fsm_manager.clear_state(user_id)
        keyboard_main = [
            [KeyboardButton(text="📋 فهرست خدمات", callback_data="services_list")],
            [
                KeyboardButton(text="🔍 پیگیری با کد", callback_data="order_tracking"),
                KeyboardButton(text="📂 درخواست‌های من", callback_data="my_orders")
            ],
            [KeyboardButton(text="⏰ یادآورها", callback_data="reminders_menu")],
            [KeyboardButton(text="📞 ارتباط با اپراتور", callback_data="contact_operator")]
        ]
        return OutgoingResponse(
            chat_id=chat_id,
            text="✅ <b>گفتگوی شما با پشتیبانی به پایان رسید.</b>\nبه منوی اصلی بازگشتید.",
            reply_markup=keyboard_main
        )
    elif data == "back_to_main":
        if fsm_manager:
            fsm_manager.clear_state(user_id)
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
            chat_id=chat_id,
            text=WELCOME_TEXT,
            reply_markup=keyboard_main
        )

    # پیمایش بخش‌های مدیریت
    elif data == "admin_stats":
        return OutgoingResponse(
            chat_id=chat_id,
            text=ADMIN_STATS_TEXT,
            reply_markup=_back_to_admin_markup()
        )
    elif data == "admin_monitors":
        if db_manager:
            with db_manager.get_session() as session:
                monitors = MonitorService.get_monitors(session, active_only=True)
                if not monitors:
                    return OutgoingResponse(
                        chat_id=chat_id,
                        text=ADMIN_MONITORS_TEXT,
                        reply_markup=_back_to_admin_markup()
                    )

                report_text = MonitorService.format_monitors_report(monitors)
                kb = [
                    [KeyboardButton(text="🔄 بررسی و به‌روزرسانی آنی", callback_data="admin_check_monitors_now")],
                    [KeyboardButton(text="🔙 بازگشت به پنل مدیریت", callback_data="back_to_admin")]
                ]
                return OutgoingResponse(
                    chat_id=chat_id,
                    text=report_text,
                    reply_markup=kb
                )

        return OutgoingResponse(
            chat_id=chat_id,
            text=ADMIN_MONITORS_TEXT,
            reply_markup=_back_to_admin_markup()
        )

    elif data == "admin_check_monitors_now":
        if db_manager:
            with db_manager.get_session() as session:
                MonitorService.check_all(session)
                monitors = MonitorService.get_monitors(session, active_only=True)
                report_text = MonitorService.format_monitors_report(monitors)
                kb = [
                    [KeyboardButton(text="🔄 بررسی مجدد", callback_data="admin_check_monitors_now")],
                    [KeyboardButton(text="🔙 بازگشت به پنل مدیریت", callback_data="back_to_admin")]
                ]
                return OutgoingResponse(
                    chat_id=chat_id,
                    text=report_text,
                    callback_alert="پایش آنی کلیه سایت‌ها با موفقیت انجام شد.",
                    reply_markup=kb
                )

        return OutgoingResponse(
            chat_id=chat_id,
            text="پایگاه داده در دسترس نیست.",
            reply_markup=_back_to_admin_markup()
        )
    elif data == "back_to_admin":
        keyboard_admin: List[List[KeyboardButton]] = [
            [KeyboardButton(text="📊 آمار و وضعیت سیستم", callback_data="admin_stats")],
            [KeyboardButton(text="📂 کارتابل درخواست‌ها", callback_data="admin_orders")],
            [KeyboardButton(text="🌐 وضعیت پایش سایت‌ها", callback_data="admin_monitors")]
        ]
        return OutgoingResponse(
            chat_id=chat_id,
            text=ADMIN_PANEL_TEXT,
            reply_markup=keyboard_admin
        )

    return OutgoingResponse(
        chat_id=chat_id,
        text="گزینه انتخاب شده معتبر نیست.",
        callback_alert="گزینه نامعتبر"
    )
