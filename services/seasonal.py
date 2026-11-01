"""
سرویس مدیریت ثبت‌نام‌های مقطعی، رویدادهای زمان‌دار و اعلان‌های تقویمی (services/seasonal.py)
سامانه «کافی نت لیمو».
شامل چرخه وضعیت‌های زمانی (Asia/Tehran)، ممانعت از ثبت‌نام خارج از بازه، و مدیریت اعلان‌ها.
"""

import logging
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from core.models import SeasonalCampaign, User
from core.calendar import get_current_jalali, format_jalali_date, gregorian_to_jalali

logger = logging.getLogger("seasonal")

# منطقه زمانی رسمی ایران (UTC+3:30)
TEHRAN_TZ_OFFSET = timedelta(hours=3, minutes=30)


class SeasonalService:
    """سرویس مدیریت ثبت‌نام‌های مقطعی و رویدادهای تقویمی."""

    @staticmethod
    def create_campaign(
        session: Session,
        code: str,
        title: str,
        description: str,
        start_at: datetime,
        end_at: datetime,
        base_fee: int = 0,
        form_schema: Optional[Dict[str, Any]] = None,
        status: str = "DRAFT"
    ) -> SeasonalCampaign:
        """ایجاد یک ثبت‌نام مقطعی جدید در سامانه."""
        if start_at.tzinfo is None:
            start_at = start_at.replace(tzinfo=timezone.utc)
        if end_at.tzinfo is None:
            end_at = end_at.replace(tzinfo=timezone.utc)

        if end_at <= start_at:
            raise ValueError("زمان پایان ثبت‌نام باید پس از زمان شروع باشد.")

        campaign = SeasonalCampaign(
            code=code.strip().upper(),
            title=title.strip(),
            description=description.strip(),
            start_at=start_at,
            end_at=end_at,
            base_fee=base_fee,
            form_schema=form_schema or {},
            status=status,
            is_active=True
        )
        session.add(campaign)
        session.commit()
        session.refresh(campaign)
        logger.info("Seasonal campaign '%s' (#%d) created with status=%s", campaign.code, campaign.id, status)
        return campaign

    @staticmethod
    def evaluate_campaign_status(campaign: SeasonalCampaign, now_utc: Optional[datetime] = None) -> str:
        """
        ارزیابی خودکار وضعیت ثبت‌نام بر مبنای زمان واقعی (مستقل از فعالیت کاربر).
        وضعیت‌ها:
        - DRAFT: پیش‌نویس
        - SUSPENDED: متوقف‌شده توسط مدیر
        - SCHEDULED: هنوز شروع نشده
        - ACTIVE: فعال و باز
        - EXPIRING_SOON: مهلت رو به پایان (کمتر از ۲۴ ساعت)
        - ENDED: پایان‌یافته
        """
        if not campaign.is_active or campaign.status == "SUSPENDED":
            return "SUSPENDED"
        if campaign.status == "DRAFT":
            return "DRAFT"

        now = now_utc or datetime.now(timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        start = campaign.start_at if campaign.start_at.tzinfo else campaign.start_at.replace(tzinfo=timezone.utc)
        end = campaign.end_at if campaign.end_at.tzinfo else campaign.end_at.replace(tzinfo=timezone.utc)

        if now < start:
            return "SCHEDULED"
        elif start <= now <= end:
            if end - now <= timedelta(hours=24):
                return "EXPIRING_SOON"
            return "ACTIVE"
        else:
            return "ENDED"

    @staticmethod
    def sync_all_campaign_statuses(session: Session, now_utc: Optional[datetime] = None) -> int:
        """بروزرسانی همگام وضعیت تمامی کمپین‌ها در پایگاه داده."""
        campaigns = session.query(SeasonalCampaign).all()
        updated_count = 0
        for c in campaigns:
            if c.status in ["DRAFT", "SUSPENDED"] and not c.is_active:
                continue
            new_status = SeasonalService.evaluate_campaign_status(c, now_utc)
            if c.status != new_status:
                c.status = new_status
                c.updated_at = datetime.now(timezone.utc)
                updated_count += 1
        if updated_count > 0:
            session.commit()
            logger.info("Synced statuses for %d seasonal campaigns", updated_count)
        return updated_count

    @staticmethod
    def is_registration_open(session: Session, campaign_id_or_code: Any, now_utc: Optional[datetime] = None) -> Tuple[bool, str, Optional[SeasonalCampaign]]:
        """
        بررسی قطعی باز بودن ثبت‌نام و ممانعت از ثبت خارج از بازه مجاز.
        خروجی: (مجاز بودن: bool, علت یا پیام فارسی: str, شیء کمپین: Optional[SeasonalCampaign])
        """
        q = session.query(SeasonalCampaign)
        if isinstance(campaign_id_or_code, int):
            campaign = q.filter_by(id=campaign_id_or_code).first()
        else:
            campaign = q.filter_by(code=str(campaign_id_or_code).strip().upper()).first()

        if not campaign:
            return False, "رویداد ثبت‌نام مورد نظر در سامانه یافت نشد.", None

        current_status = SeasonalService.evaluate_campaign_status(campaign, now_utc)

        if current_status == "DRAFT":
            return False, "این ثبت‌نام در وضعیت پیش‌نویس است و هنوز منتشر نگردیده است.", campaign
        elif current_status == "SUSPENDED":
            return False, "ثبت‌نام این خدمت موقتاً توسط مدیریت سامانه متوقف شده است.", campaign
        elif current_status == "SCHEDULED":
            jy, jm, jd = gregorian_to_jalali(campaign.start_at.year, campaign.start_at.month, campaign.start_at.day)
            start_str = format_jalali_date(jy, jm, jd)
            return False, f"مهلت ثبت‌نام هنوز آغاز نشده است.\nتاریخ شروع: {start_str}", campaign
        elif current_status == "ENDED":
            jy, jm, jd = gregorian_to_jalali(campaign.end_at.year, campaign.end_at.month, campaign.end_at.day)
            end_str = format_jalali_date(jy, jm, jd)
            return False, f"مهلت قانونی ثبت‌نام این خدمت در تاریخ {end_str} به پایان رسیده است.", campaign
        elif current_status in ["ACTIVE", "EXPIRING_SOON"]:
            return True, "ثبت‌نام فعال و مجاز است.", campaign

        return False, "وضعیت ثبت‌نام نامعتبر است.", campaign

    @staticmethod
    def get_active_campaigns(session: Session, now_utc: Optional[datetime] = None) -> List[SeasonalCampaign]:
        """دریافت لیست کمپین‌های فعال جهت نمایش در کاتالوگ ربات."""
        SeasonalService.sync_all_campaign_statuses(session, now_utc)
        return (
            session.query(SeasonalCampaign)
            .filter(
                SeasonalCampaign.is_active.is_(True),
                SeasonalCampaign.status.in_(["ACTIVE", "EXPIRING_SOON"])
            )
            .order_by(SeasonalCampaign.end_at.asc())
            .all()
        )

    @staticmethod
    def format_campaign_card(campaign: SeasonalCampaign) -> str:
        """تولید متن رسمی کارت معرفی ثبت‌نام مقطعی به همراه شرایط و تاریخ شمسی."""
        s_jy, s_jm, s_jd = gregorian_to_jalali(campaign.start_at.year, campaign.start_at.month, campaign.start_at.day)
        e_jy, e_jm, e_jd = gregorian_to_jalali(campaign.end_at.year, campaign.end_at.month, campaign.end_at.day)

        start_shamsi = format_jalali_date(s_jy, s_jm, s_jd)
        end_shamsi = format_jalali_date(e_jy, e_jm, e_jd)

        fee_str = f"{campaign.base_fee:,} ریال" if campaign.base_fee > 0 else "طبق تعرفه مصوب"

        status_icon = "🟢 فعال" if campaign.status == "ACTIVE" else "⚠️ مهلت رو به پایان"

        return (
            f"⏰ <b>{campaign.title}</b>\n\n"
            f"📝 <b>توضیحات:</b>\n{campaign.description}\n\n"
            f"📅 <b>آغاز مهلت:</b> {start_shamsi}\n"
            f"⏳ <b>پایان مهلت:</b> {end_shamsi}\n"
            f"💰 <b>تعرفه پایه:</b> {fee_str}\n"
            f"📌 <b>وضعیت کنونی:</b> {status_icon}\n\n"
            "<i>(توجه: اطلاعات بر اساس اعلام رسمی مراجع ذی‌صلاح درج گردیده است)</i>"
        )
