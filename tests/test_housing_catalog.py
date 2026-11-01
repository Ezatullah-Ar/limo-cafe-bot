"""
آزمون‌های خودکار فرآیند کد رهگیری مسکن، شرایط، فرم مرحله‌ای، گزینه‌های شاهد و دکمه بازگشت (Phase 7).
"""

import unittest
from core.config import Settings
from core.security import AccessControl
from core.throttling import Throttler
from core.database import DatabaseManager
from services.catalog import CatalogService, HOUSING_TERMS_TEXT
from services.orders import OrderService
from bot.models import TelegramUser, CallbackQuery, IncomingMessage
from bot.dispatcher import BotDispatcher
from bot.fsm import FSMManager
from core.validators import validate_card_number, mask_sensitive_data


class TestHousingCatalogFlow(unittest.TestCase):
    """مجموعه آزمون‌های جامع فرآیند ثبت کد رهگیری مسکن و کاتالوگ جدید."""

    def setUp(self):
        self.user_id = 99112233
        self.user = TelegramUser(id=self.user_id, first_name="علی", last_name="کاظمی")

        self.settings = Settings(admin_id=123456789)
        self.access_control = AccessControl(self.settings)
        self.throttler = Throttler(rate_limit_seconds=0.0, max_burst=1000)
        self.fsm_manager = FSMManager()

        self.db_manager = DatabaseManager("sqlite:///:memory:")
        self.db_manager.init_db()

        with self.db_manager.get_session() as session:
            CatalogService.seed_initial_catalog(session)

        self.dispatcher = BotDispatcher(
            access_control=self.access_control,
            throttler=self.throttler,
            db_manager=self.db_manager,
            fsm_manager=self.fsm_manager
        )

    def tearDown(self):
        self.db_manager.drop_db()

    def test_housing_terms_displayed_before_form(self):
        """آزمون نمایش متن شرایط و دکمه «شرایط را خواندم» قبل از ورود به فرم."""
        cb = CallbackQuery(id="cb_h1", from_user=self.user, data="svc_HOUSING_TRACKING_CODE")
        res = self.dispatcher.dispatch_callback(cb)

        self.assertIn("شرایط و الزامات دریافت کد رهگیری مسکن", res.text)
        self.assertIn("مسئولیت قانونی هرگونه مغایرت اطلاعات تماماً بر عهده متقاضی است", res.text)
        self.assertIn("۳۵۰،۰۰۰ تومان", res.text)
        
        button_callbacks = [btn.callback_data for row in res.reply_markup for btn in row if btn.callback_data]
        self.assertIn("housing_terms_accepted", button_callbacks)
        self.assertIn("cat_ALIEN_AND_CODES", button_callbacks)

    def test_housing_terms_acceptance_starts_fsm(self):
        """آزمون پذیرش شرایط با دکمه خواندم و آغاز مرحله اول فرم (شماره مستأجر)."""
        cb = CallbackQuery(id="cb_h2", from_user=self.user, data="housing_terms_accepted")
        res = self.dispatcher.dispatch_callback(cb)

        self.assertIn("ثبت درخواست: کد رهگیری قرارداد مسکن", res.text)
        self.assertIn("شماره تلفن همراه مستأجر", res.text)

        state = self.fsm_manager.get_state(self.user_id)
        self.assertIsNotNone(state)
        self.assertEqual(state.service_code, "HOUSING_TRACKING_CODE")
        self.assertTrue(state.terms_accepted)
        self.assertEqual(state.current_field_index, 0)

    def test_step_by_step_housing_form_with_validations_and_witness_limo(self):
        """آزمون تکمیل مرحله‌به‌مرحله فرم مسکن، اعتبارسنجی‌ها، انتخاب شاهد کافی‌نت و تایید نهایی."""
        # ۱. آغاز فرم
        cb_accept = CallbackQuery(id="cb_acc", from_user=self.user, data="housing_terms_accepted")
        self.dispatcher.dispatch_callback(cb_accept)

        # ۲. ارسال شماره مستأجر با فرمت اشتباه -> خطای اعتبارسنجی
        msg_err_phone = IncomingMessage(message_id=1, from_user=self.user, text="0912123")
        res_err = self.dispatcher.dispatch(msg_err_phone)
        self.assertIn("خطای اعتبارسنجی", res_err.text)

        # ۳. ارسال شماره مستأجر معتبر
        msg_tenant_phone = IncomingMessage(message_id=2, from_user=self.user, text="09123456789")
        res_step2 = self.dispatcher.dispatch(msg_tenant_phone)
        self.assertIn("شماره تلفن همراه صاحب‌خانه", res_step2.text)

        # ۴. ارسال شماره مالک معتبر
        msg_landlord_phone = IncomingMessage(message_id=3, from_user=self.user, text="09351112233")
        res_step3 = self.dispatcher.dispatch(msg_landlord_phone)
        self.assertIn("کد ملی ۱۰ رقمی مالک", res_step3.text)

        # ۵. ارسال کد ملی مالک نامعتبر -> خطا
        msg_err_nid = IncomingMessage(message_id=4, from_user=self.user, text="1111111111")
        res_err_nid = self.dispatcher.dispatch(msg_err_nid)
        self.assertIn("خطای اعتبارسنجی", res_err_nid.text)

        # ۶. ارسال کد ملی مالک معتبر (0010123456 با الگوریتم درست یا تست استاندارد)
        # برای کد ملی استاندارد: 0010000000 -> 0*10 + 0*9 + 1*8 + 0... = 8. 11 - 8 = 3 -> 0010000003
        msg_landlord_nid = IncomingMessage(message_id=5, from_user=self.user, text="0010000003")
        res_step4 = self.dispatcher.dispatch(msg_landlord_nid)
        self.assertIn("مبلغ ودیعه (رهن)، اجاره ماهانه و مدت قرارداد", res_step4.text)

        # ۷. ارسال شرایط مالی و مدت قرارداد
        msg_rent = IncomingMessage(message_id=6, from_user=self.user, text="رهن ۱۰۰ میلیون، اجاره ۵ میلیون، یک ساله")
        res_step5 = self.dispatcher.dispatch(msg_rent)
        self.assertIn("شناسه قبض برق و کد پستی", res_step5.text)

        # ۸. ارسال قبض برق و کد پستی
        msg_postal = IncomingMessage(message_id=7, from_user=self.user, text="قبض: ۱۲۳۴۵۶۷۸۹۰ - کد پستی: ۱۴۱۷۶۱۴۴۱۱")
        res_step6 = self.dispatcher.dispatch(msg_postal)
        self.assertIn("شماره کارت بانکی ۱۶ رقمی مالک", res_step6.text)

        # ۹. ارسال شماره کارت بانکی معتبر مالک (۱۶ رقم)
        msg_card = IncomingMessage(message_id=8, from_user=self.user, text="6037991812345678")
        res_step7 = self.dispatcher.dispatch(msg_card)
        self.assertIn("نحوه معرفی دو شاهد ایرانی", res_step7.text)

        # بررسی وجود گزینه‌های شاهد کافی‌نت و شاهد شخصی
        witness_btn_cbs = [btn.callback_data for row in res_step7.reply_markup for btn in row if btn.callback_data]
        self.assertIn("witness_choice_limo", witness_btn_cbs)
        self.assertIn("witness_choice_self", witness_btn_cbs)
        self.assertIn("order_step_back", witness_btn_cbs)

        # ۱۰. انتخاب تأمین شاهد توسط کافی‌نت (تعرفه ۳۵۰،۰۰۰ تومان)
        cb_witness_limo = CallbackQuery(id="cb_wit", from_user=self.user, data="witness_choice_limo")
        res_preview = self.dispatcher.dispatch_callback(cb_witness_limo)

        self.assertIn("پیش‌نمایش درخواست: کد رهگیری قرارداد مسکن", res_preview.text)
        self.assertIn("تأمین توسط کافی‌نت لیمو (تعرفه ۳۵۰،۰۰۰ تومان)", res_preview.text)

        # راستی‌آزمایی ماسک‌گذاری داده‌های حساس در پیش‌نمایش
        self.assertIn("6037-****-****-5678", res_preview.text)
        self.assertIn("0912***6789", res_preview.text)
        self.assertIn("001****003", res_preview.text)

        # ۱۱. تایید نهایی و ثبت سفارش
        cb_confirm = CallbackQuery(id="cb_conf", from_user=self.user, data="order_confirm")
        res_success = self.dispatcher.dispatch_callback(cb_confirm)
        self.assertIn("درخواست شما با موفقیت ثبت گردید", res_success.text)
        self.assertIn("LIMO-1405-", res_success.text)

        # اعتبارسنجی ثبت شدن در پایگاه داده
        with self.db_manager.get_session() as session:
            orders = OrderService.get_user_orders_by_telegram_id(session, self.user_id)
            self.assertEqual(len(orders), 1)
            o = orders[0]
            self.assertEqual(o.service.code, "HOUSING_TRACKING_CODE")
            self.assertEqual(o.form_data.get("tenant_phone"), "09123456789")
            self.assertEqual(o.form_data.get("landlord_card_number"), "6037991812345678")
            self.assertIn("تأمین توسط کافی‌نت لیمو", o.form_data.get("witness_mode"))

    def test_order_step_back_and_cancel(self):
        """آزمون دکمه بازگشت به مرحله قبل (step_back) و انصراف (cancel)."""
        # شروع فرم
        self.dispatcher.dispatch_callback(CallbackQuery(id="c1", from_user=self.user, data="housing_terms_accepted"))

        # ورود شماره مستأجر
        self.dispatcher.dispatch(IncomingMessage(message_id=1, from_user=self.user, text="09123456789"))

        # اکنون در مرحله ۲ (شماره مالک) هستیم
        state = self.fsm_manager.get_state(self.user_id)
        self.assertEqual(state.current_field_index, 1)

        # کلیک روی دکمه بازگشت به مرحله قبل
        cb_back = CallbackQuery(id="c_b", from_user=self.user, data="order_step_back")
        res_back = self.dispatcher.dispatch_callback(cb_back)
        self.assertIn("مرحله 1 از 7", res_back.text)
        self.assertIn("شماره تلفن همراه مستأجر", res_back.text)

        # وضعیت FSM به مرحله ۰ بازگشته باشد
        state_after = self.fsm_manager.get_state(self.user_id)
        self.assertEqual(state_after.current_field_index, 0)

        # کلیک روی انصراف
        cb_cancel = CallbackQuery(id="c_can", from_user=self.user, data="order_cancel")
        res_cancel = self.dispatcher.dispatch_callback(cb_cancel)
        self.assertIn("لغو گردید", res_cancel.text)
        self.assertIsNone(self.fsm_manager.get_state(self.user_id))


if __name__ == "__main__":
    unittest.main()
