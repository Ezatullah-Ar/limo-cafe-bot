"""
سرویس مدیریت کاتالوگ خدمات و کاربران سامانه «کافی نت لیمو».
این ماژول دسته‌بندی‌های ۶ گانه مصوب، خدمات استاندارد، شرایط مسکن و ثبت کاربران را در دیتابیس مدیریت می‌کند.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from core.models import User, ServiceCategory, ServiceItem, CommunicationChannel, SystemSetting

HOUSING_TERMS_TEXT = (
    "📋 <b>شرایط و الزامات دریافت کد رهگیری مسکن (سامانه خودنویس):</b>\n\n"
    "۱. <b>مسئولیت صحت اطلاعات:</b> کلیه اطلاعات ارسالی باید واقعی، صحیح و مطابق مدارک هویتی و مالکیتی طرفین باشد. "
    "مسئولیت قانونی هرگونه مغایرت اطلاعات تماماً بر عهده متقاضی است.\n\n"
    "۲. <b>مالکیت شماره‌های تماس:</b> شماره تماس مستأجر باید حتماً به نام شخص مستأجر، و شماره تماس صاحب‌خانه به نام خود مالک باشد "
    "(جهت دریافت پیامک تایید و احراز هویت سامانه املاک).\n\n"
    "۳. <b>کد ملی مالک:</b> ثبت کد ملی ۱۰ رقمی مالک (موجر) جهت استعلام مالکیت ثبتی الزامی است.\n\n"
    "۴. <b>اطلاعات مالی و مدت قرارداد:</b> مبالغ رهن (ودیعه)، اجاره ماهانه و مدت زمان قرارداد اجاره باید دقیق قید شوند.\n\n"
    "۵. <b>مشخصات ملک:</b> شناسه قبض برق و کد پستی ۱۰ رقمی محل سکونت باید دقیق و دارای تاییدیه پستی باشند.\n\n"
    "۶. <b>شماره کارت مالک:</b> درج شماره کارت ۱۶ رقمی مالک جهت ثبت در سامانه برای واریز کرایه خانه الزامی است.\n\n"
    "۷. <b>شاهدان معتبر ایرانی:</b> ثبت قرارداد نیازمند دو شاهد معتبر ایرانی است. شما می‌توانید مشخصات دو شاهد را شخصاً معرفی فرمایید، "
    "یا درخواست تأمین دو شاهد رسمی توسط کافی‌نت لیمو (با هزینه مصوب ۳۵۰،۰۰۰ تومان) را ثبت نمایید.\n\n"
    "🔒 <b>محرمانگی کامل:</b> کلیه اطلاعات حساس مالی و هویتی شما کاملاً رمزنگاری و حفاظت شده و در لاگ‌ها یا گزارش‌های عمومی افشا نخواهند شد.\n\n"
    "جهت ادامه فرآیند و آغاز ورود اطلاعات در ربات، لطفاً دکمه «✅ شرایط را خواندم و می‌پذیرم» را انتخاب فرمایید:"
)

INITIAL_CATALOG_DATA = [
    {
        "code": "ALIEN_AND_CODES",
        "title": "🌐 امور اتباع و کدها",
        "description": "کد فیدا، کد ادب، کد رهگیری مسکن و خدمات مرتبط با اتباع و مهاجرین",
        "order_priority": 1,
        "services": [
            {
                "code": "HOUSING_TRACKING_CODE",
                "title": "کد رهگیری قرارداد مسکن (سامانه خودنویس)",
                "description": (
                    "صدور رسمی کد رهگیری قراردادهای اجاره مسکن در سامانه خودنویس و املاک کشور "
                    "به همراه احراز هویت پیامکی و ثبت مشخصات طرفین و شاهدان معتبر."
                ),
                "official_url": "https://srem.mrud.ir/",
                "required_docs": [
                    "تصویر یا فایل قرارداد / اجاره‌نامه قبلی یا توافق‌نامه",
                    "تصویر قبض برق یا تاییدیه کد پستی ملک"
                ],
                "required_fields": {
                    "tenant_phone": "شماره تلفن همراه مستأجر (به نام خود مستأجر)",
                    "landlord_phone": "شماره تلفن همراه صاحب‌خانه (به نام خود مالک)",
                    "landlord_national_id": "کد ملی ۱۰ رقمی مالک (موجر)",
                    "deposit_and_rent": "مبلغ ودیعه (رهن)، اجاره ماهانه و مدت قرارداد",
                    "postal_code_and_bill": "شناسه قبض برق و کد پستی ۱۰ رقمی ملک استیجاری",
                    "landlord_card_number": "شماره کارت بانکی ۱۶ رقمی مالک جهت واریز کرایه خانه",
                    "witness_mode": "نحوه تأمین دو شاهد ایرانی (معرفی توسط متقاضی یا تأمین توسط کافی‌نت)"
                },
                "base_fee": 0,
                "order_priority": 1
            },
            {
                "code": "FIDA_CODE",
                "title": "دریافت و استعلام کد فیدا اتباع (FIDA)",
                "description": (
                    "دریافت شناسه ۱۲ رقمی اختصاصی فیدا جهت امور بانکی، بیمه، دانشگاه و امور اداری اتباع غیرایرانی."
                ),
                "official_url": "http://fida.ir/",
                "required_docs": [
                    "تصویر صفحه اول گذرنامه یا مدرک اقامتی معتبر"
                ],
                "required_fields": {
                    "passport_number": "شماره گذرنامه یا مدرک اقامتی",
                    "full_name_en": "نام و نام خانوادگی به انگلیسی مطابق گذرنامه",
                    "birth_date": "تاریخ تولد به میلادی",
                    "nationality": "ملیت متقاضی",
                    "mobile_phone": "شماره همراه در دسترس"
                },
                "base_fee": 0,
                "order_priority": 2
            },
            {
                "code": "ADAB_STUDENT_AFFAIRS",
                "title": "سامانه امور دانشجویان بین‌الملل (ادب)",
                "description": (
                    "ثبت و پیگیری امور روادید تحصیلی، تمدید اقامت، امور کنسولی و "
                    "پذیرش دانشجویان غیرایرانی در درگاه پورتال ادب سازمان امور دانشجویان (saorg.ir)."
                ),
                "official_url": "https://adab.saorg.ir/PortalADAB/Home/LandingPage",
                "required_docs": [
                    "تصویر صفحه اول گذرنامه با اعتبار معتبر",
                    "تصویر نامه پذیرش یا گواهی اشتغال به تحصیل دانشگاه"
                ],
                "required_fields": {
                    "passport_number": "شماره گذرنامه معتبر متقاضی",
                    "tracking_or_fara_code": "کد فراگیر / شناسه پیگیری سامانه ادب",
                    "target_university": "نام دانشگاه محل تحصیل در ایران",
                    "study_level": "مقطع تحصیلی (کارشناسی / ارشد / دکتری)"
                },
                "base_fee": 0,
                "order_priority": 3
            },
            {
                "code": "IVSF_APPOINTMENT",
                "title": "سامانه نوبت‌دهی تثبیت هویت اتباع",
                "description": (
                    "اخذ نوبت اداری الکترونیکی جهت تثبیت هویت، تایید اسناد و امور "
                    "هویتی اتباع در سامانه رسمی نوبت‌دهی تثبیت هویت (ivsf.nsia.gov.af)."
                ),
                "official_url": "http://ivsf.nsia.gov.af/",
                "required_docs": [
                    "تصویر تذکره الکترونیکی یا برگه تثبیت هویت قبلی",
                    "تصویر صفحه اول گذرنامه یا مدرک اقامتی معتبر"
                ],
                "required_fields": {
                    "identity_code": "شماره تذکره یا شناسه هویتی متقاضی",
                    "full_name": "نام و نام خانوادگی مطابق مدارک رسمی",
                    "phone_number": "شماره تلفن همراه متقاضی",
                    "preferred_city": "شهر یا نمایندگی مورد تقاضا"
                },
                "base_fee": 0,
                "order_priority": 4
            }
        ]
    },
    {
        "code": "UNIVERSITY_SERVICES",
        "title": "🎓 خدمات دانشگاهی و آزمون‌ها",
        "description": "ثبت‌نام آزمون‌های سراسری سنجش، انتخاب رشته، پیام نور گلستان، آزاد آموزشیار و تاییدیه تحصیلی",
        "order_priority": 2,
        "services": [
            {
                "code": "SANJESH_REGISTRATION",
                "title": "ثبت‌نام آزمون‌های سراسری سازمان سنجش",
                "description": (
                    "ثبت‌نام، ویرایش اطلاعات، دریافت کد سوابق تحصیلی مای‌مدیو و "
                    "پیگیری آزمون‌های سراسری (کنکور سراسری، کارشناسی ارشد و دکتری)."
                ),
                "official_url": "https://www.sanjesh.org/",
                "required_docs": [
                    "فایل عکس پرسنلی ۴×۳ استاندارد (حجم کمتر از ۷۰ کیلوبایت)",
                    "تصویر مدرک مقطع قبلی یا کارنامه دیپلم"
                ],
                "required_fields": {
                    "exam_type": "نوع آزمون (سراسری / کارشناسی ارشد / دکتری)",
                    "national_id": "کد ملی داوطلب",
                    "mobile_phone": "شماره همراه به نام متقاضی",
                    "military_status": "وضعیت نظام وظیفه (برای آقایان)",
                    "quota_type": "سهمیه مناطق / ایثارگران"
                },
                "base_fee": 0,
                "order_priority": 1
            },
            {
                "code": "UNIVERSITY_ENROLLMENT",
                "title": "انتخاب رشته و ثبت‌نام دانشگاه",
                "description": (
                    "مشاوره و ثبت انتخاب رشته تخصصی آزمون‌های سراسری و دانشگاه آزاد، "
                    "و ثبت‌نام اینترنتی پذیرفته‌شدگان نهایی دانشگاه‌ها."
                ),
                "official_url": "https://sanjesh.org/",
                "required_docs": [
                    "کارنامه اولیه آزمون سراسری",
                    "تصویر شناسنامه و کارت ملی"
                ],
                "required_fields": {
                    "national_id": "کد ملی داوطلب",
                    "exam_code": "شماره داوطلبی یا پرونده آزمون",
                    "preferred_majors": "رشته‌ها و دوره‌های اولویت‌دار",
                    "mobile_phone": "شماره تماس داوطلب"
                },
                "base_fee": 0,
                "order_priority": 2
            },
            {
                "code": "EMT_VERIFICATION",
                "title": "استعلام تاییدیه تحصیلی و کد صحت",
                "description": (
                    "درخواست استعلام رسمی مدارک تحصیلی (دیپلم، پیش‌دانشگاهی یا دانشگاهی) "
                    "و دریافت تاییدیه یا کد صحت ۲۰ رقمی از سامانه‌های وزارت آموزش و پرورش و وزارت علوم."
                ),
                "official_url": "https://emt.medu.ir/",
                "required_docs": [
                    "تصویر باکیفیت مدرک تحصیلی یا گواهی موقت",
                    "تصویر کارت ملی یا شناسنامه"
                ],
                "required_fields": {
                    "national_id": "کد ملی ۱۰ رقمی",
                    "education_level": "مقطع تحصیلی (دیپلم / پیش‌دانشگاهی / کارشناسی)",
                    "school_or_university": "نام مدرسه یا دانشگاه محل تحصیل",
                    "graduation_year": "سال فراغت از تحصیل",
                    "destination_org": "نام دانشگاه یا سازمان استعلام‌گیرنده"
                },
                "base_fee": 0,
                "order_priority": 3
            },
            {
                "code": "PNU_SERVICES",
                "title": "سامانه گلستان دانشگاه پیام نور",
                "description": (
                    "امور انتخاب واحد، دریافت کارنامه، ثبت درخواست گواهی اشتغال به تحصیل، "
                    "تسویه حساب و امور مالی در درگاه جامع آموزش پیام نور (سیستم گلستان)."
                ),
                "official_url": "https://osreg.pnu.ac.ir/forms/authenticateuser/main.htm",
                "required_docs": [
                    "تصویر کارت دانشجویی پیام نور"
                ],
                "required_fields": {
                    "student_id": "شماره دانشجویی گلستان",
                    "national_id": "کد ملی ۱۰ رقمی دانشجو",
                    "request_type": "عنوان درخواست (انتخاب واحد / گواهی اشتغال / کارنامه)",
                    "study_branch": "رشته و مقطع تحصیلی"
                },
                "base_fee": 0,
                "order_priority": 4
            },
            {
                "code": "IAU_SERVICES",
                "title": "سامانه آموزشیار دانشگاه آزاد اسلامی",
                "description": (
                    "انتخاب واحد، پرداخت شهریه، اخذ مجوز امتحان، مشاهده نمرات و "
                    "درخواست‌های آموزشی در سامانه سراسری آموزشیار دانشگاه آزاد."
                ),
                "official_url": "https://edu.iau.ac.ir/",
                "required_docs": [
                    "تصویر کارت دانشجویی یا آخرین برگ انتخاب واحد"
                ],
                "required_fields": {
                    "student_id": "شماره دانشجویی آموزشیار",
                    "national_id": "کد ملی دانشجو",
                    "campus_name": "استان و واحد دانشگاهی",
                    "request_type": "نوع اقدام در سامانه آموزشیار"
                },
                "base_fee": 0,
                "order_priority": 5
            }
        ]
    },
    {
        "code": "TICKETS_TRAVEL",
        "title": "✈️ بلیت هواپیما، قطار و اتوبوس",
        "description": "رزرو و صدور آنلاین بلیت قطار، هواپیما (داخلی و بین‌المللی) و اتوبوس‌های بین‌شهری",
        "order_priority": 3,
        "services": [
            {
                "code": "TRAIN_TICKET",
                "title": "رزرو و صدور بلیت قطار",
                "description": (
                    "رزرو قطارهای رجا، فدک، سفیر در تمام خطوط ریلی کشور با سالن‌های کوپه‌ای و اتوبوسی."
                ),
                "official_url": "https://raja.ir/",
                "required_docs": [
                    "تصویر کارت ملی یا شناسنامه مسافران"
                ],
                "required_fields": {
                    "origin_city": "شهر مبدأ",
                    "destination_city": "شهر مقصد",
                    "travel_date": "تاریخ رفت (روز/ماه/سال شمسی)",
                    "passenger_count": "تعداد مسافران",
                    "national_id": "کد ملی مسافر اصلی",
                    "mobile_phone": "شماره تلفن همراه جهت دریافت پیامک بلیت"
                },
                "base_fee": 0,
                "order_priority": 1
            },
            {
                "code": "FLIGHT_TICKET",
                "title": "رزرو بلیت هواپیما (داخلی و خارجی)",
                "description": (
                    "جست‌وجو و صدور پروازهای چارتری و سیستمی ایرلاین‌های معتبر کشور."
                ),
                "official_url": "https://limo-cafe.ir/",
                "required_docs": [
                    "تصویر کارت ملی (پرواز داخلی) یا صفحه اول پاسپورت (پرواز خارجی)"
                ],
                "required_fields": {
                    "origin_city": "شهر یا فرودگاه مبدأ",
                    "destination_city": "شهر یا فرودگاه مقصد",
                    "travel_date": "تاریخ پرواز",
                    "passenger_count": "تعداد مسافران",
                    "national_id": "کد ملی یا شماره گذرنامه مسافر",
                    "mobile_phone": "شماره تماس مسافر"
                },
                "base_fee": 0,
                "order_priority": 2
            },
            {
                "code": "BUS_TICKET",
                "title": "رزرو و خرید بلیت اتوبوس بین‌شهری",
                "description": (
                    "صدور آنی بلیت اتوبوس‌های VIP و معمولی کلیه پایانه‌ها و مقاصد کشور."
                ),
                "official_url": "https://limo-cafe.ir/",
                "required_docs": [],
                "required_fields": {
                    "origin_city": "شهر و پایانه مبدأ",
                    "destination_city": "شهر مقصد",
                    "travel_date": "تاریخ حرکت",
                    "national_id": "کد ملی مسافر",
                    "mobile_phone": "شماره همراه مسافر"
                },
                "base_fee": 0,
                "order_priority": 3
            }
        ]
    },
    {
        "code": "GOVERNMENT_INTERNET",
        "title": "🏛 سایر خدمات اینترنتی و اداری",
        "description": "درگاه ملی دولت هوشمند، خلافی خودرو، استعلام کد پستی، ثبت‌نام سجام و خدمات دولتی",
        "order_priority": 4,
        "services": [
            {
                "code": "GOV_PORTAL",
                "title": "درگاه ملی خدمات دولت هوشمند (my.gov.ir)",
                "description": (
                    "ثبت‌نام، ورود یکپارچه، پیگیری درخواست‌های سامانه‌های دولتی و اداری."
                ),
                "official_url": "https://my.gov.ir/",
                "required_docs": [],
                "required_fields": {
                    "national_id": "کد ملی ۱۰ رقمی متقاضی",
                    "mobile_phone": "شماره همراه به نام متقاضی",
                    "request_type": "عنوان خدمت یا سامانه درخواستی در درگاه دولت"
                },
                "base_fee": 0,
                "order_priority": 1
            },
            {
                "code": "TRAFFIC_FINES",
                "title": "استعلام و پرداخت خلافی و عوارض خودرو",
                "description": (
                    "استعلام ریز جرائم رانندگی، عوارض آزادراهی و طرح ترافیک با تسویه آنی."
                ),
                "official_url": "https://rahvar120.ir/",
                "required_docs": [
                    "تصویر کارت ماشین یا برگ سبز خودرو"
                ],
                "required_fields": {
                    "plate_number": "شماره پلاک کامل خودرو",
                    "national_id": "کد ملی مالک خودرو",
                    "mobile_phone": "شماره همراه مالک خودرو"
                },
                "base_fee": 0,
                "order_priority": 2
            },
            {
                "code": "POSTAL_INQUIRY",
                "title": "استعلام کد پستی و گواهی نشانی",
                "description": (
                    "دریافت گواهی رسمی کد پستی ده‌رقمی معتبر و تاییدیه نشانی از شرکت ملی پست."
                ),
                "official_url": "https://gnaf.post.ir/",
                "required_docs": [
                    "تصویر قبض برق یا سند/اجاره‌نامه محل سکونت"
                ],
                "required_fields": {
                    "province_and_city": "استان و شهر محل سکونت",
                    "full_address": "نشانی دقیق پستی همراه با پلاک و واحد",
                    "mobile_phone": "شماره همراه متقاضی"
                },
                "base_fee": 0,
                "order_priority": 3
            },
            {
                "code": "SEJAM_REGISTER",
                "title": "ثبت‌نام و احراز هویت سجام",
                "description": (
                    "ثبت‌نام در سامانه جامع اطلاعات مشتریان (سجام) و دریافت کد بورسی جهت معاملات سهام."
                ),
                "official_url": "https://daneshkadeh.sejam.ir/",
                "required_docs": [
                    "تصویر کارت ملی و شناسنامه متقاضی"
                ],
                "required_fields": {
                    "national_id": "کد ملی ۱۰ رقمی متقاضی",
                    "mobile_phone": "شماره همراه به نام خود متقاضی",
                    "bank_iban": "شماره شبا بانکی به نام متقاضی (IR...)"
                },
                "base_fee": 0,
                "order_priority": 4
            }
        ]
    },
    {
        "code": "PORTAL_AND_WALLET",
        "title": "📂 درخواست‌های من، کیف پول و پیگیری سفارش",
        "description": "مشاهده و پیگیری پرونده‌ها، گردش مالی کیف پول و استعلام رهگیری",
        "order_priority": 5,
        "services": []
    },
    {
        "code": "SUPPORT_AND_CONTACT",
        "title": "💬 گفت‌وگو با پشتیبانی و ارتباط با ما",
        "description": "گفت‌وگوی برخط با اپراتورها و مشاهده کانال‌های ارتباطی کافی‌نت لیمو",
        "order_priority": 6,
        "services": []
    }
]

INITIAL_COMMUNICATION_CHANNELS = [
    {"key": "PHONE", "title": "تلفن تماس کافی‌نت", "value": "09120000000", "is_active": True, "order_priority": 1},
    {"key": "TELEGRAM", "title": "کانال و پشتیبانی تلگرام", "value": "https://t.me/LimoCafeBot", "is_active": True, "order_priority": 2},
    {"key": "EITAA", "title": "کانال رسمی ایتا", "value": "https://eitaa.com/limocafe", "is_active": True, "order_priority": 3},
    {"key": "RUBIKA", "title": "کانال روبیکا", "value": "https://rubika.ir/limocafe", "is_active": True, "order_priority": 4},
    {"key": "BALE", "title": "کانال بله", "value": "https://ble.ir/limocafe", "is_active": True, "order_priority": 5},
    {"key": "INSTAGRAM", "title": "صفحه اینستاگرام", "value": "https://instagram.com/limocafe", "is_active": True, "order_priority": 6},
    {"key": "WORKING_HOURS", "title": "ساعت کاری پشتیبانی", "value": "همه‌روزه از ۸:۰۰ صبح الی ۲۱:۰۰ شب", "is_active": True, "order_priority": 7}
]

INITIAL_SYSTEM_SETTINGS = [
    {"key": "witness_provision_fee", "value": "3500000", "description": "هزینه تامین دو شاهد رسمی مسکن توسط کافی نت (به ریال)"},
    {"key": "enable_animations", "value": "0", "description": "فعال‌سازی انیمیشن‌های سبک تلگرام (1=فعال، 0=غیرفعال)"}
]


class CatalogService:
    """سرویس کوئری و مدیریت کاتالوگ خدمات در دیتابیس."""

    @staticmethod
    def seed_initial_catalog(session: Session) -> None:
        """
        ثبت امن و تکرارپذیر (Idempotent) دسته‌بندی‌های ۶ گانه، کاتالوگ خدمات، کانال‌های ارتباطی و تنظیمات سراسری.
        """
        for cat_data in INITIAL_CATALOG_DATA:
            category = session.query(ServiceCategory).filter_by(code=cat_data["code"]).first()
            if not category:
                category = ServiceCategory(
                    code=cat_data["code"],
                    title=cat_data["title"],
                    description=cat_data["description"],
                    order_priority=cat_data["order_priority"],
                    is_active=True
                )
                session.add(category)
                session.flush()
            else:
                category.title = cat_data["title"]
                category.description = cat_data["description"]
                category.order_priority = cat_data["order_priority"]
                session.flush()

            for svc_data in cat_data.get("services", []):
                service = session.query(ServiceItem).filter_by(code=svc_data["code"]).first()
                if not service:
                    service = ServiceItem(
                        category_id=category.id,
                        code=svc_data["code"],
                        title=svc_data["title"],
                        description=svc_data["description"],
                        official_url=svc_data.get("official_url"),
                        required_docs=svc_data.get("required_docs", []),
                        required_fields=svc_data.get("required_fields", {}),
                        base_fee=svc_data.get("base_fee", 0),
                        order_priority=svc_data.get("order_priority", 0),
                        is_active=True
                    )
                    session.add(service)
                else:
                    service.category_id = category.id
                    service.title = svc_data["title"]
                    service.description = svc_data["description"]
                    service.required_fields = svc_data.get("required_fields", {})
                    service.required_docs = svc_data.get("required_docs", [])

        # ثبت امن کانال‌های ارتباطی اولیه
        for ch_data in INITIAL_COMMUNICATION_CHANNELS:
            ch = session.query(CommunicationChannel).filter_by(key=ch_data["key"]).first()
            if not ch:
                ch = CommunicationChannel(
                    key=ch_data["key"],
                    title=ch_data["title"],
                    value=ch_data["value"],
                    is_active=ch_data["is_active"],
                    order_priority=ch_data["order_priority"]
                )
                session.add(ch)

        # ثبت تنظیمات اولیه سیستم (شامل تعرفه شاهد مسکن ۳۵۰ هزار تومان)
        for st_data in INITIAL_SYSTEM_SETTINGS:
            st = session.query(SystemSetting).filter_by(key=st_data["key"]).first()
            if not st:
                st = SystemSetting(
                    key=st_data["key"],
                    value=st_data["value"],
                    description=st_data.get("description")
                )
                session.add(st)

        session.flush()

    @staticmethod
    def get_categories(session: Session, active_only: bool = True) -> List[ServiceCategory]:
        """دریافت لیست دسته‌بندی‌های کاتالوگ."""
        query = session.query(ServiceCategory)
        if active_only:
            query = query.filter(ServiceCategory.is_active.is_(True))
        return query.order_by(ServiceCategory.order_priority.asc()).all()

    @staticmethod
    def get_services_by_category(session: Session, category_code: str, active_only: bool = True) -> List[ServiceItem]:
        """
        دریافت خدمات متعلق به یک دسته‌بندی مشخص با پشتیبانی کامل از کدهای تاریخی.
        """
        code_mapping = {
            "STUDENT_SERVICES": "UNIVERSITY_SERVICES",
            "CONSULAR_INTERNATIONAL": "ALIEN_AND_CODES"
        }
        target_code = code_mapping.get(category_code, category_code)

        query = session.query(ServiceItem).join(ServiceCategory).filter(
            (ServiceCategory.code == target_code) | (ServiceCategory.code == category_code)
        )
        if active_only:
            query = query.filter(ServiceItem.is_active.is_(True))
        return query.order_by(ServiceItem.order_priority.asc()).all()

    @staticmethod
    def get_service_by_code(session: Session, code: str) -> Optional[ServiceItem]:
        """یافتن یک خدمت با استفاده از شناسه کد یکتا."""
        return session.query(ServiceItem).filter_by(code=code).first()

    @staticmethod
    def get_or_create_user(
        session: Session,
        telegram_id: int,
        full_name: str,
        username: Optional[str] = None,
        role: str = "CUSTOMER"
    ) -> User:
        """یافتن یا ایجاد کاربر در سامانه به صورت اتمیک."""
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            user = User(
                telegram_id=telegram_id,
                full_name=full_name,
                username=username,
                role=role
            )
            session.add(user)
            session.flush()
        else:
            if user.full_name != full_name or user.username != username:
                user.full_name = full_name
                user.username = username
        return user

    @staticmethod
    def get_channels(session: Session, active_only: bool = True) -> List[CommunicationChannel]:
        """دریافت لیست کانال‌ها و شبکه‌های ارتباطی کافی‌نت لیمو."""
        query = session.query(CommunicationChannel)
        if active_only:
            query = query.filter(CommunicationChannel.is_active.is_(True))
        return query.order_by(CommunicationChannel.order_priority.asc()).all()

    @staticmethod
    def update_channel(
        session: Session,
        key: str,
        value: str,
        is_active: Optional[bool] = None,
        title: Optional[str] = None
    ) -> Optional[CommunicationChannel]:
        """به‌روزرسانی یک راه ارتباطی با کلید یکتا."""
        ch = session.query(CommunicationChannel).filter_by(key=key).first()
        if ch:
            ch.value = value
            if is_active is not None:
                ch.is_active = is_active
            if title is not None:
                ch.title = title
            session.flush()
        return ch

    @staticmethod
    def get_setting(session: Session, key: str, default: Optional[str] = None) -> Optional[str]:
        """خواندن مقدار یک تنظیم سراسری از جدول system_settings."""
        st = session.query(SystemSetting).filter_by(key=key).first()
        if st and st.value is not None:
            return st.value
        return default

    @staticmethod
    def set_setting(
        session: Session,
        key: str,
        value: str,
        description: Optional[str] = None
    ) -> SystemSetting:
        """ثبت یا به‌روزرسانی تنظیم سراسری."""
        st = session.query(SystemSetting).filter_by(key=key).first()
        if not st:
            st = SystemSetting(key=key, value=value, description=description)
            session.add(st)
        else:
            st.value = value
            if description:
                st.description = description
        session.flush()
        return st

    @staticmethod
    def get_witness_fee(session: Session) -> int:
        """
        دریافت تعرفه مصوب تأمین دو شاهد رسمی مسکن (به ریال).
        مبلغ پیش‌فرض مصوب ۳۵۰،۰۰۰ تومان (۳،۵۰۰،۰۰۰ ریال) است.
        """
        val_str = CatalogService.get_setting(session, "witness_provision_fee", "3500000")
        try:
            return int(val_str)
        except (ValueError, TypeError):
            return 3500000
