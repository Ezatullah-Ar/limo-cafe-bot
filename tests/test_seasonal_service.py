"""
آزمون‌های خودکار سرویس ثبت‌نام‌های مقطعی و رویدادهای زمان‌دار (tests/test_seasonal_service.py)
سامانه «کافی نت لیمو» - فاز ۴.
پوشش چرخه‌حیات زمانی، قفل زمانی (Hard-Gate)، فیلتر وضعیت‌ها، و تولید کارت‌های اطلاع‌رسانی.
"""

import unittest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.database import Base
from core.models import SeasonalCampaign
from services.seasonal import SeasonalService


class TestSeasonalService(unittest.TestCase):
    """مجموعه آزمون‌های جامع سرویس ثبت‌نام‌های مقطعی."""

    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.now = datetime(2026, 10, 30, 12, 0, 0, tzinfo=timezone.utc)

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_create_campaign_validation(self):
        """آزمون ایجاد کمپین و اعتبارسنجی بازه زمانی شروع و پایان."""
        start = self.now + timedelta(days=1)
        end = self.now + timedelta(days=5)

        campaign = SeasonalService.create_campaign(
            session=self.session,
            code="KONKUR_1405",
            title="ثبت‌نام نوبت دوم کنکور سراسری",
            description="ثبت‌نام اینترنتی در سایت سنجش",
            start_at=start,
            end_at=end,
            base_fee=500000,
            status="SCHEDULED"
        )
        self.assertIsNotNone(campaign.id)
        self.assertEqual(campaign.code, "KONKUR_1405")
        self.assertTrue(campaign.is_active)

        # تاریخ پایان قبل از تاریخ شروع باید خطا دهد
        with self.assertRaises(ValueError):
            SeasonalService.create_campaign(
                session=self.session,
                code="INVALID",
                title="خطا",
                description="تست خطا",
                start_at=end,
                end_at=start
            )

    def test_evaluate_campaign_lifecycle_statuses(self):
        """آزمون ارزیابی وضعیت‌های مختلف چرخه حیات (DRAFT, SUSPENDED, SCHEDULED, ACTIVE, EXPIRING_SOON, ENDED)."""
        # ۱. پیش‌نویس (DRAFT)
        c_draft = SeasonalCampaign(
            code="C_DRAFT",
            title="پیش‌نویس",
            start_at=self.now - timedelta(days=1),
            end_at=self.now + timedelta(days=1),
            status="DRAFT",
            is_active=True
        )
        self.assertEqual(SeasonalService.evaluate_campaign_status(c_draft, self.now), "DRAFT")

        # ۲. متوقف‌شده (SUSPENDED)
        c_suspended = SeasonalCampaign(
            code="C_SUSP",
            title="متوقف",
            start_at=self.now - timedelta(days=1),
            end_at=self.now + timedelta(days=1),
            status="SUSPENDED",
            is_active=True
        )
        self.assertEqual(SeasonalService.evaluate_campaign_status(c_suspended, self.now), "SUSPENDED")

        # ۳. زمان‌بندی‌شده (SCHEDULED) - هنوز شروع نشده
        c_sched = SeasonalCampaign(
            code="C_SCHED",
            title="شروع نشده",
            start_at=self.now + timedelta(days=2),
            end_at=self.now + timedelta(days=5),
            status="SCHEDULED",
            is_active=True
        )
        self.assertEqual(SeasonalService.evaluate_campaign_status(c_sched, self.now), "SCHEDULED")

        # ۴. فعال (ACTIVE) - بیش از ۲۴ ساعت مانده
        c_active = SeasonalCampaign(
            code="C_ACTIVE",
            title="فعال",
            start_at=self.now - timedelta(days=2),
            end_at=self.now + timedelta(days=3),
            status="ACTIVE",
            is_active=True
        )
        self.assertEqual(SeasonalService.evaluate_campaign_status(c_active, self.now), "ACTIVE")

        # ۵. مهلت رو به پایان (EXPIRING_SOON) - کمتر از ۲۴ ساعت مانده
        c_expiring = SeasonalCampaign(
            code="C_EXP",
            title="در حال اتمام",
            start_at=self.now - timedelta(days=2),
            end_at=self.now + timedelta(hours=12),
            status="ACTIVE",
            is_active=True
        )
        self.assertEqual(SeasonalService.evaluate_campaign_status(c_expiring, self.now), "EXPIRING_SOON")

        # ۶. پایان‌یافته (ENDED)
        c_ended = SeasonalCampaign(
            code="C_ENDED",
            title="منقضی شده",
            start_at=self.now - timedelta(days=5),
            end_at=self.now - timedelta(hours=1),
            status="ACTIVE",
            is_active=True
        )
        self.assertEqual(SeasonalService.evaluate_campaign_status(c_ended, self.now), "ENDED")

    def test_sync_all_campaign_statuses(self):
        """آزمون همگام‌سازی وضعیت چند کمپین در پایگاه داده."""
        c1 = SeasonalCampaign(code="C1", title="C1", description="توضیح ۱", start_at=self.now - timedelta(days=2), end_at=self.now + timedelta(days=2), status="SCHEDULED", is_active=True)
        c2 = SeasonalCampaign(code="C2", title="C2", description="توضیح ۲", start_at=self.now - timedelta(days=5), end_at=self.now - timedelta(days=1), status="ACTIVE", is_active=True)
        self.session.add_all([c1, c2])
        self.session.commit()

        updated = SeasonalService.sync_all_campaign_statuses(self.session, self.now)
        self.assertEqual(updated, 2)

        self.session.refresh(c1)
        self.session.refresh(c2)
        self.assertEqual(c1.status, "ACTIVE")
        self.assertEqual(c2.status, "ENDED")

    def test_is_registration_open_hard_gate(self):
        """آزمون قفل ممانعت از ثبت‌نام در شرایط خارج از موعد یا غیرمجاز."""
        c_sched = SeasonalCampaign(code="SCHED", title="کنکور بعدا", description="توضیح کنکور", start_at=self.now + timedelta(days=2), end_at=self.now + timedelta(days=5), status="SCHEDULED", is_active=True)
        c_ended = SeasonalCampaign(code="ENDED", title="وام دانشجویی تمام", description="توضیح وام", start_at=self.now - timedelta(days=5), end_at=self.now - timedelta(days=1), status="ENDED", is_active=True)
        c_active = SeasonalCampaign(code="OPEN", title="انتخاب واحد", description="توضیح انتخاب واحد", start_at=self.now - timedelta(days=1), end_at=self.now + timedelta(days=1), status="ACTIVE", is_active=True)
        self.session.add_all([c_sched, c_ended, c_active])
        self.session.commit()

        # ۱. بررسی کمپین زمان‌بندی‌شده
        ok, msg, camp = SeasonalService.is_registration_open(self.session, "SCHED", self.now)
        self.assertFalse(ok)
        self.assertIn("مهلت ثبت‌نام هنوز آغاز نشده است", msg)

        # ۲. بررسی کمپین منقضی‌شده
        ok, msg, camp = SeasonalService.is_registration_open(self.session, "ENDED", self.now)
        self.assertFalse(ok)
        self.assertIn("به پایان رسیده است", msg)

        # ۳. بررسی کمپین باز
        ok, msg, camp = SeasonalService.is_registration_open(self.session, "OPEN", self.now)
        self.assertTrue(ok)
        self.assertIn("فعال و مجاز", msg)

        # ۴. کد نامعتبر
        ok, msg, camp = SeasonalService.is_registration_open(self.session, "NON_EXISTENT", self.now)
        self.assertFalse(ok)
        self.assertIn("یافت نشد", msg)

    def test_get_active_campaigns(self):
        """آزمون فیلتر کمپین‌های در دسترس عموم."""
        c1 = SeasonalCampaign(code="C1", title="فعال ۱", description="توضیح ۱", start_at=self.now - timedelta(days=1), end_at=self.now + timedelta(days=3), status="ACTIVE", is_active=True)
        c2 = SeasonalCampaign(code="C2", title="فعال ۲ رو به پایان", description="توضیح ۲", start_at=self.now - timedelta(days=1), end_at=self.now + timedelta(hours=5), status="ACTIVE", is_active=True)
        c3 = SeasonalCampaign(code="C3", title="منقضی", description="توضیح ۳", start_at=self.now - timedelta(days=5), end_at=self.now - timedelta(days=1), status="ENDED", is_active=True)
        self.session.add_all([c1, c2, c3])
        self.session.commit()

        actives = SeasonalService.get_active_campaigns(self.session, self.now)
        self.assertEqual(len(actives), 2)
        codes = [c.code for c in actives]
        self.assertIn("C1", codes)
        self.assertIn("C2", codes)
        self.assertNotIn("C3", codes)

    def test_format_campaign_card(self):
        """آزمون تولید متن نمایشی و رسمی کارت ثبت‌نام مقطعی."""
        campaign = SeasonalCampaign(
            code="HEJRAT",
            title="ثبت‌نام کارت آمایش اتباع",
            description="ثبت‌نام و نوبت‌دهی تمدید کارت آمایش در دفاتر کفالت",
            start_at=datetime(2026, 10, 20, 8, 0, 0, tzinfo=timezone.utc),
            end_at=datetime(2026, 11, 5, 18, 0, 0, tzinfo=timezone.utc),
            base_fee=3500000,
            status="ACTIVE",
            is_active=True
        )
        card_text = SeasonalService.format_campaign_card(campaign)
        self.assertIn("ثبت‌نام کارت آمایش اتباع", card_text)
        self.assertIn("3,500,000 ریال", card_text)
        self.assertIn("آغاز مهلت:", card_text)
        self.assertIn("پایان مهلت:", card_text)
        self.assertIn("🟢 فعال", card_text)


if __name__ == "__main__":
    unittest.main()
