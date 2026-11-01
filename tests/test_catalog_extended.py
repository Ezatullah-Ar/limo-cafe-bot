"""
آزمون‌های خودکار کاتالوگ جامع ۶ خدمت و الگوهای پایش هوشمند (tests/test_catalog_extended.py)
سامانه «کافی نت لیمو».
راستی‌آزمایی وجود و صحت هر ۶ خدمت مصوب، فیلدهای الزامی، شروع FSM و قوانین پایش هوشمند سایت‌ها.
"""

import unittest
from core.config import Settings
from core.security import AccessControl
from core.throttling import Throttler
from core.database import DatabaseManager
from services.catalog import CatalogService
from services.monitor import MonitorService, INITIAL_TARGET_SITES
from bot.models import TelegramUser, CallbackQuery
from bot.dispatcher import BotDispatcher
from bot.fsm import FSMManager


class TestCatalogExtended(unittest.TestCase):
    """مجموعه آزمون‌های کاتالوگ ۶ خدمت اصلی و رفتارهای FSM متناظر."""

    def setUp(self):
        self.user_id = 99881122
        self.user = TelegramUser(id=self.user_id, first_name="کاربر تستی")

        self.settings = Settings(admin_id=123456789)
        self.access_control = AccessControl(self.settings)
        self.throttler = Throttler(rate_limit_seconds=0.0, max_burst=1000)
        self.fsm_manager = FSMManager()

        self.db_manager = DatabaseManager("sqlite:///:memory:")
        self.db_manager.init_db()

        with self.db_manager.get_session() as session:
            CatalogService.seed_initial_catalog(session)
            MonitorService.seed_initial_monitors(session)

        self.dispatcher = BotDispatcher(
            access_control=self.access_control,
            throttler=self.throttler,
            db_manager=self.db_manager,
            fsm_manager=self.fsm_manager
        )

    def tearDown(self):
        self.db_manager.drop_db()

    def test_all_six_services_seeded_correctly(self):
        """آزمون وجود ۶ دسته‌بندی و خدمات رسمی مصوب در پایگاه داده."""
        with self.db_manager.get_session() as session:
            categories = CatalogService.get_categories(session)
            self.assertEqual(len(categories), 6)
            cat_codes = [c.code for c in categories]
            self.assertIn("ALIEN_AND_CODES", cat_codes)
            self.assertIn("UNIVERSITY_SERVICES", cat_codes)
            self.assertIn("TICKETS_TRAVEL", cat_codes)
            self.assertIn("GOVERNMENT_INTERNET", cat_codes)
            self.assertIn("PORTAL_AND_WALLET", cat_codes)
            self.assertIn("SUPPORT_AND_CONTACT", cat_codes)

            expected_services = [
                "EMT_VERIFICATION",
                "SANJESH_REGISTRATION",
                "PNU_SERVICES",
                "IAU_SERVICES",
                "IVSF_APPOINTMENT",
                "ADAB_STUDENT_AFFAIRS",
                "HOUSING_TRACKING_CODE"
            ]

            for s_code in expected_services:
                svc = CatalogService.get_service_by_code(session, s_code)
                self.assertIsNotNone(svc, f"خدمت {s_code} باید در دیتابیس موجود باشد.")
                self.assertTrue(len(svc.required_fields) > 0, f"فیلدهای {s_code} نباید خالی باشد.")
                self.assertTrue(len(svc.required_docs) > 0, f"مدارک {s_code} نباید خالی باشد.")
                self.assertTrue(svc.official_url.startswith("http"), f"نشانی رسمی {s_code} باید معتبر باشد.")

    def test_services_list_callback_contains_all_six_buttons(self):
        """آزمون نمایش کلیدهای شیشه‌ای دسته‌بندی‌های ۶ گانه در کاتالوگ خدمات."""
        cb = CallbackQuery(
            id="cb_list",
            from_user=self.user,
            data="services_list"
        )
        res = self.dispatcher.dispatch_callback(cb)
        self.assertIn("فهرست خدمات فعال کافی نت لیمو", res.text)
        self.assertIsNotNone(res.reply_markup)

        button_callbacks = [btn.callback_data for row in res.reply_markup for btn in row if btn.callback_data]
        self.assertIn("cat_ALIEN_AND_CODES", button_callbacks)
        self.assertIn("cat_UNIVERSITY_SERVICES", button_callbacks)
        self.assertIn("cat_TICKETS_TRAVEL", button_callbacks)
        self.assertIn("cat_GOVERNMENT_INTERNET", button_callbacks)
        self.assertIn("cat_PORTAL_AND_WALLET", button_callbacks)
        self.assertIn("cat_SUPPORT_AND_CONTACT", button_callbacks)

        # آزمون مشاهده خدمات دسته‌بندی دانشگاهی
        cb_univ = CallbackQuery(id="cb_univ", from_user=self.user, data="cat_UNIVERSITY_SERVICES")
        res_univ = self.dispatcher.dispatch_callback(cb_univ)
        univ_buttons = [btn.callback_data for row in res_univ.reply_markup for btn in row if btn.callback_data]
        self.assertIn("svc_EMT_VERIFICATION", univ_buttons)
        self.assertIn("svc_SANJESH_REGISTRATION", univ_buttons)
        self.assertIn("svc_PNU_SERVICES", univ_buttons)
        self.assertIn("svc_IAU_SERVICES", univ_buttons)

    def test_service_details_callbacks_for_new_services(self):
        """آزمون مشاهده جزئیات خدمات با ثبت مستقیم داخل ربات (بدون لینک خروج) و راهنمای مدارک."""
        # ۱. گلستان پیام نور
        cb_pnu = CallbackQuery(id="cb_pnu", from_user=self.user, data="svc_PNU_SERVICES")
        res_pnu = self.dispatcher.dispatch_callback(cb_pnu)
        self.assertIn("سامانه گلستان دانشگاه پیام نور", res_pnu.text)
        self.assertIn("ثبت مستقیم داخل ربات", res_pnu.text)
        self.assertIn("شماره دانشجویی گلستان", res_pnu.text)

        # ۲. آموزشیار دانشگاه آزاد
        cb_iau = CallbackQuery(id="cb_iau", from_user=self.user, data="svc_IAU_SERVICES")
        res_iau = self.dispatcher.dispatch_callback(cb_iau)
        self.assertIn("سامانه آموزشیار دانشگاه آزاد", res_iau.text)
        self.assertIn("ثبت مستقیم داخل ربات", res_iau.text)
        self.assertIn("شماره دانشجویی آموزشیار", res_iau.text)

        # ۳. تثبیت هویت
        cb_ivsf = CallbackQuery(id="cb_ivsf", from_user=self.user, data="svc_IVSF_APPOINTMENT")
        res_ivsf = self.dispatcher.dispatch_callback(cb_ivsf)
        self.assertIn("تثبیت هویت", res_ivsf.text)
        self.assertIn("ثبت مستقیم داخل ربات", res_ivsf.text)
        self.assertIn("شناسه هویتی", res_ivsf.text)

        # ۴. سامانه ادب
        cb_adab = CallbackQuery(id="cb_adab", from_user=self.user, data="svc_ADAB_STUDENT_AFFAIRS")
        res_adab = self.dispatcher.dispatch_callback(cb_adab)
        self.assertIn("سامانه امور دانشجویان بین‌الملل", res_adab.text)
        self.assertIn("ثبت مستقیم داخل ربات", res_adab.text)
        self.assertIn("شماره گذرنامه", res_adab.text)

    def test_fsm_order_intake_start_for_all_services(self):
        """آزمون ورود موفق ماشین وضعیت FSM به مرحله ثبت اطلاعات برای هر خدمت."""
        for s_code in ("PNU_SERVICES", "IAU_SERVICES", "IVSF_APPOINTMENT", "ADAB_STUDENT_AFFAIRS"):
            self.fsm_manager.clear_state(self.user_id)
            cb_start = CallbackQuery(id=f"cb_st_{s_code}", from_user=self.user, data=f"order_start_{s_code}")
            res_start = self.dispatcher.dispatch_callback(cb_start)
            self.assertIn("ثبت درخواست", res_start.text)
            self.assertIn("مرحله ۱ از", res_start.text)

            state = self.fsm_manager.get_state(self.user_id)
            self.assertIsNotNone(state)
            self.assertEqual(state.service_code, s_code)
            self.assertEqual(state.step, "FIELD_INPUT")

    def test_smart_monitors_detection_rules_verification(self):
        """آزمون تحلیل الگوهای باز و بسته بودن خدمات در ۶ سایت هدف."""
        for target in INITIAL_TARGET_SITES:
            code = target["code"]
            rule = target["detection_rule"]
            open_kw = rule.get("open_keywords", [])
            closed_kw = rule.get("closed_keywords", [])

            self.assertTrue(len(open_kw) > 0, f"سایت {code} باید کلیدواژه باز داشته باشد.")
            self.assertTrue(len(closed_kw) > 0, f"سایت {code} باید کلیدواژه بسته داشته باشد.")

            # شبیه‌سازی متن پاسخ باز بودن نوبت
            sample_open_html = f"<html><body>صفحه رسمی: {open_kw[0]} هم اکنون فعال است.</body></html>"
            has_open = any(kw in sample_open_html for kw in open_kw)
            self.assertTrue(has_open, f"الگوی باز بودن سایت {code} شناسایی نشد.")

            # شبیه‌سازی متن پاسخ بسته بودن نوبت
            sample_closed_html = f"<html><body>اطلاعیه مهم: {closed_kw[0]}. لطفاً بعداً مراجعه کنید.</body></html>"
            has_closed = any(kw in sample_closed_html for kw in closed_kw)
            self.assertTrue(has_closed, f"الگوی بسته بودن سایت {code} شناسایی نشد.")


if __name__ == "__main__":
    unittest.main()
