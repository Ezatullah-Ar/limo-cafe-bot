-- ========================================================
-- ساختار جداول پایگاه داده ابری Cloudflare D1 (SQLite)
-- سامانه «کافی نت لیمو»
-- ========================================================

-- ۱. جدول کاربران
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    username TEXT,
    phone_number TEXT,
    role TEXT NOT NULL DEFAULT 'CUSTOMER',
    is_active INTEGER NOT NULL DEFAULT 1,
    national_code TEXT,
    alien_code TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    deleted_at DATETIME
);
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);

-- ۲. دسته‌بندی خدمات
CREATE TABLE IF NOT EXISTS service_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    order_priority INTEGER NOT NULL DEFAULT 0,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
,
    deleted_at DATETIME);

-- ۳. آیتم‌های خدمت در کاتالوگ
CREATE TABLE IF NOT EXISTS service_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL REFERENCES service_categories(id) ON DELETE CASCADE,
    code TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    official_url TEXT,
    required_fields TEXT NOT NULL DEFAULT '{}',
    required_docs TEXT NOT NULL DEFAULT '[]',
    base_fee INTEGER NOT NULL DEFAULT 0,
    order_priority INTEGER NOT NULL DEFAULT 0,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
,
    deleted_at DATETIME);

-- ۴. سفارش‌ها و پرونده‌های مشتریان
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tracking_code TEXT UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    service_id INTEGER NOT NULL REFERENCES service_items(id),
    status TEXT NOT NULL DEFAULT 'PENDING',
    form_data TEXT NOT NULL DEFAULT '{}',
    operator_notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
,
    deleted_at DATETIME);
CREATE INDEX IF NOT EXISTS idx_orders_tracking_code ON orders(tracking_code);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

-- ۵. تاریخچه تغییر وضعیت سفارش‌ها (Audit Logs)
CREATE TABLE IF NOT EXISTS order_audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    actor_id INTEGER NOT NULL,
    from_status TEXT NOT NULL,
    to_status TEXT NOT NULL,
    note TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ۶. جدول یادآورهای هوشمند تقویمی
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    shamsi_date TEXT NOT NULL,
    target_date DATETIME NOT NULL,
    is_sent INTEGER NOT NULL DEFAULT 0,
    sent_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_reminders_target_date ON reminders(target_date);
CREATE INDEX IF NOT EXISTS idx_reminders_is_sent ON reminders(is_sent);

-- ۷. جدول پایش هوشمند سایت‌های هدف
CREATE TABLE IF NOT EXISTS website_monitors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    check_interval_minutes INTEGER NOT NULL DEFAULT 15,
    last_checked_at DATETIME,
    uptime_status TEXT NOT NULL DEFAULT 'UNKNOWN',
    service_status TEXT NOT NULL DEFAULT 'UNKNOWN',
    last_response_time_ms INTEGER,
    last_http_code INTEGER,
    status_message TEXT,
    detection_rule TEXT NOT NULL DEFAULT '{}',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
,
    deleted_at DATETIME);

-- ۸. لاگ‌های پایش سایت‌ها
CREATE TABLE IF NOT EXISTS monitor_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    monitor_id INTEGER NOT NULL REFERENCES website_monitors(id) ON DELETE CASCADE,
    checked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    uptime_status TEXT NOT NULL,
    service_status TEXT NOT NULL,
    http_code INTEGER,
    response_time_ms INTEGER,
    details TEXT
);

-- ۷. نشست‌های فعال گفتگوی زنده با پشتیبانی (چت دوطرفه)
CREATE TABLE IF NOT EXISTS active_support_sessions (
    telegram_id INTEGER PRIMARY KEY,
    full_name TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ۸. کیف پول کاربران
CREATE TABLE IF NOT EXISTS wallets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    balance INTEGER NOT NULL DEFAULT 0,
    is_frozen INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_wallets_user_id ON wallets(user_id);

-- ۹. تراکنش‌های مالی کیف پول
CREATE TABLE IF NOT EXISTS wallet_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wallet_id INTEGER NOT NULL REFERENCES wallets(id) ON DELETE CASCADE,
    amount INTEGER NOT NULL,
    transaction_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING',
    tracking_ref TEXT UNIQUE NOT NULL,
    receipt_file_id TEXT,
    operator_id INTEGER,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_wallet_tx_wallet_id ON wallet_transactions(wallet_id);
CREATE INDEX IF NOT EXISTS idx_wallet_tx_ref ON wallet_transactions(tracking_ref);
CREATE INDEX IF NOT EXISTS idx_wallet_tx_status ON wallet_transactions(status);

-- ۱۰. تیکت‌ها و گفتگوهای پشتیبانی
CREATE TABLE IF NOT EXISTS support_threads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'NEW',
    assigned_operator_id INTEGER,
    related_order_id INTEGER REFERENCES orders(id) ON DELETE SET NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_support_threads_user_id ON support_threads(user_id);
CREATE INDEX IF NOT EXISTS idx_support_threads_status ON support_threads(status);

-- ۱۱. پیام‌های گفتگوی پشتیبانی
CREATE TABLE IF NOT EXISTS support_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id INTEGER NOT NULL REFERENCES support_threads(id) ON DELETE CASCADE,
    sender_role TEXT NOT NULL DEFAULT 'CUSTOMER',
    sender_id INTEGER NOT NULL,
    message_text TEXT,
    file_id TEXT,
    file_type TEXT,
    is_read INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_support_messages_thread_id ON support_messages(thread_id);

-- ۱۲. ثبت‌نام‌های مقطعی و زمان‌دار
CREATE TABLE IF NOT EXISTS seasonal_campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    start_at DATETIME NOT NULL,
    end_at DATETIME NOT NULL,
    status TEXT NOT NULL DEFAULT 'DRAFT',
    base_fee INTEGER NOT NULL DEFAULT 0,
    form_schema TEXT NOT NULL DEFAULT '{}',
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
,
    deleted_at DATETIME);
CREATE INDEX IF NOT EXISTS idx_seasonal_code ON seasonal_campaigns(code);
CREATE INDEX IF NOT EXISTS idx_seasonal_status ON seasonal_campaigns(status);

-- ۱۳. کانال‌های ارتباطی و شبکه‌های اجتماعی
CREATE TABLE IF NOT EXISTS communication_channels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    value TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    order_priority INTEGER NOT NULL DEFAULT 0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
,
    deleted_at DATETIME);
CREATE INDEX IF NOT EXISTS idx_comm_channels_key ON communication_channels(key);

-- ۱۴. تنظیمات سراسری سیستم
CREATE TABLE IF NOT EXISTS system_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL,
    description TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_settings_key ON system_settings(key);

-- ========================================================
-- داده‌های اولیه مصوب (Initial Seeding)
-- ========================================================

-- دسته‌بندی‌های کاتالوگ
INSERT OR IGNORE INTO service_categories (id, code, title, description, order_priority, is_active)
VALUES 
(1, 'STUDENT_SERVICES', '🎓 خدمات دانشجویی و آزمون‌ها', 'امور ثبت‌نام آزمون‌های سراسری، تاییدیه تحصیلی، کد صحت و سامانه‌های آموزشی', 1, 1),
(2, 'CONSULAR_INTERNATIONAL', '🌐 امور کنسولی و بین‌الملل', 'نوبت‌دهی تثبیت هویت، سامانه امور دانشجویان بین‌الملل (ادب) و پذیرش اتباع', 2, 1);

-- خدمات جامع کاتالوگ (۶ خدمت مصوب)
INSERT OR IGNORE INTO service_items (id, category_id, code, title, description, official_url, required_fields, required_docs, base_fee, order_priority, is_active)
VALUES 
(
    1, 1, 'EMT_VERIFICATION',
    'استعلام تاییدیه تحصیلی و کد صحت',
    'دریافت استعلام رسمی مدرک دیپلم و پیش‌دانشگاهی از سامانه وزارت آموزش و پرورش (emt.medu.ir) جهت ثبت‌نام دانشگاه.',
    'https://emt.medu.ir/',
    '{"national_id": "کد ملی ۱۰ رقمی", "education_level": "مقطع تحصیلی", "school_or_university": "نام مدرسه یا دانشگاه", "graduation_year": "سال فراغت از تحصیل", "destination_org": "نام دانشگاه یا سازمان استعلام‌گیرنده"}',
    '["تصویر مدرک تحصیلی یا گواهی موقت", "تصویر کارت ملی یا شناسنامه"]',
    0, 1, 1
),
(
    2, 1, 'SANJESH_REGISTRATION',
    'ثبت‌نام آزمون‌های سازمان سنجش',
    'ثبت‌نام، ویرایش اطلاعات، دریافت کد سوابق تحصیلی مای‌مدیو و آزمون‌های سراسری سازمان سنجش.',
    'https://www.sanjesh.org/',
    '{"exam_type": "نوع آزمون (سراسری / ارشد / دکتری)", "national_id": "کد ملی داوطلب", "mobile_phone": "شماره همراه به نام متقاضی", "military_status": "وضعیت نظام وظیفه", "quota_type": "سهمیه مناطق / ایثارگران"}',
    '["عکس پرسنلی ۴×۳ استاندارد", "تصویر مدرک مقطع قبلی یا کارنامه دیپلم"]',
    0, 2, 1
),
(
    3, 1, 'PNU_SERVICES',
    'سامانه گلستان دانشگاه پیام نور',
    'امور انتخاب واحد، کارنامه، گواهی اشتغال به تحصیل، تسویه حساب و امور مالی در سامانه جامع گلستان پیام نور.',
    'https://osreg.pnu.ac.ir/forms/authenticateuser/main.htm',
    '{"student_id": "شماره دانشجویی گلستان", "national_id": "کد ملی دانشجو", "request_type": "نوع درخواست (انتخاب واحد / گواهی / کارنامه)", "study_branch": "رشته و مقطع تحصیلی"}',
    '["تصویر کارت دانشجویی پیام نور"]',
    0, 3, 1
),
(
    4, 1, 'IAU_SERVICES',
    'سامانه آموزشیار دانشگاه آزاد اسلامی',
    'انتخاب واحد، پرداخت شهریه، اخذ مجوز امتحان، مشاهده نمرات و درخواست‌های آموزشی در درگاه آموزشیار.',
    'https://edu.iau.ac.ir/',
    '{"student_id": "شماره دانشجویی آموزشیار", "national_id": "کد ملی دانشجو", "campus_name": "استان و واحد دانشگاهی", "request_type": "نوع اقدام در سامانه آموزشیار"}',
    '["تصویر کارت دانشجویی یا برگ انتخاب واحد قبلی"]',
    0, 4, 1
),
(
    5, 2, 'IVSF_APPOINTMENT',
    'سامانه نوبت‌دهی تثبیت هویت اتباع',
    'اخذ نوبت اداری الکترونیکی جهت تثبیت هویت، تایید اسناد و امور هویتی اتباع در سامانه رسمی نوبت‌دهی (ivsf.nsia.gov.af).',
    'http://ivsf.nsia.gov.af/',
    '{"identity_code": "شماره تذکره یا شناسه هویتی متقاضی", "full_name": "نام و نام خانوادگی مطابق مدارک رسمی", "phone_number": "شماره تلفن همراه متقاضی", "preferred_city": "شهر یا نمایندگی مورد تقاضا"}',
    '["تصویر تذکره الکترونیکی یا برگه تثبیت هویت قبلی", "تصویر صفحه اول گذرنامه یا مدرک اقامتی معتبر"]',
    0, 1, 1
),
(
    6, 2, 'ADAB_STUDENT_AFFAIRS',
    'سامانه امور دانشجویان بین‌الملل (ادب)',
    'ثبت و پیگیری امور روادید تحصیلی، تمدید اقامت، امور کنسولی و پذیرش دانشجویان غیرایرانی در پورتال ادب (saorg.ir).',
    'https://adab.saorg.ir/PortalADAB/Home/LandingPage',
    '{"passport_number": "شماره گذرنامه معتبر متقاضی", "tracking_or_fara_code": "کد فراگیر / شناسه پیگیری سامانه ادب", "target_university": "نام دانشگاه محل تحصیل در ایران", "study_level": "مقطع تحصیلی (کارشناسی / ارشد / دکتری)"}',
    '["تصویر صفحه اول گذرنامه با اعتبار معتبر", "تصویر نامه پذیرش یا گواهی اشتغال به تحصیل"]',
    0, 2, 1
);

-- ۶ سایت هدف پایش هوشمند
INSERT OR IGNORE INTO website_monitors (id, code, title, url, is_active, check_interval_minutes, uptime_status, service_status, detection_rule)
VALUES 
(1, 'IVSF', 'سامانه دریافت نوبت تثبیت هویت', 'http://ivsf.nsia.gov.af/', 1, 15, 'UNKNOWN', 'UNKNOWN', '{"open_keywords": ["نوبت دهی", "دریافت نوبت", "ثبت نام"], "closed_keywords": ["تکمیل ظرفیت", "نوبتی وجود ندارد", "بسته است", "غیرفعال"]}'),
(2, 'ADAB_SAORG', 'سامانه امور دانشجویان بین‌الملل (ادب)', 'https://adab.saorg.ir/PortalADAB/Home/LandingPage', 1, 15, 'UNKNOWN', 'UNKNOWN', '{"open_keywords": ["ثبت نام دانشجو", "پذیرش دانشجویان", "ورود متقاضی"], "closed_keywords": ["مهلت به پایان رسیده", "سامانه غیرفعال است"]}'),
(3, 'PNU_GOLESTAN', 'سامانه گلستان دانشگاه پیام نور', 'https://osreg.pnu.ac.ir/forms/authenticateuser/main.htm', 1, 15, 'UNKNOWN', 'UNKNOWN', '{"open_keywords": ["ورود به سیستم", "شناسه کاربری", "کد امنیتی"], "closed_keywords": ["سیستم موقتاً قطع است", "در دست تعمیر"]}'),
(4, 'IAU_EDU', 'سامانه آموزشی دانشگاه آزاد (آموزشیار)', 'https://edu.iau.ac.ir/', 1, 15, 'UNKNOWN', 'UNKNOWN', '{"open_keywords": ["ورود به سامانه", "دانشجویان", "انتخاب واحد"], "closed_keywords": ["سیستم در حال به‌روزرسانی است", "قطع موقت"]}'),
(5, 'SANJESH', 'سازمان سنجش آموزش کشور', 'https://www.sanjesh.org/', 1, 15, 'UNKNOWN', 'UNKNOWN', '{"open_keywords": ["ثبت نام آزمون", "سیستم ثبت نام", "آغاز نام نویسی"], "closed_keywords": ["مهلت ثبت نام به پایان رسید", "پایان مهلت ثبت نام"]}'),
(6, 'EMT_MEDU', 'سامانه دریافت تأییدیه تحصیلی (آموزش و پرورش)', 'https://emt.medu.ir/', 1, 15, 'UNKNOWN', 'UNKNOWN', '{"open_keywords": ["ثبت نام استعلام مدارک", "ثبت تاییدیه تحصیلی", "پیگیری استعلام"], "closed_keywords": ["سامانه در دسترس نیست", "در حال بروزرسانی"]}');

-- تنظیمات اولیه سراسری سیستم
INSERT OR IGNORE INTO system_settings (key, value, description)
VALUES 
('witness_provision_fee', '3500000', 'هزینه تامین شاهد رسمی توسط کافی نت (به ریال)'),
('enable_animations', '0', 'فعال‌سازی انیمیشن‌های سبک تلگرام (1=فعال، 0=غیرفعال)');

-- راه‌های ارتباطی اولیه
INSERT OR IGNORE INTO communication_channels (key, title, value, is_active, order_priority)
VALUES
('PHONE', 'تلفن تماس کافی‌نت', '09120000000', 1, 1),
('TELEGRAM', 'کانال و پشتیبانی تلگرام', 'https://t.me/LimoCafeBot', 1, 2),
('EITAA', 'کانال رسمی ایتا', 'https://eitaa.com/limocafe', 1, 3),
('RUBIKA', 'کانال روبیکا', 'https://rubika.ir/limocafe', 1, 4),
('BALE', 'کانال بله', 'https://ble.ir/limocafe', 1, 5),
('INSTAGRAM', 'صفحه اینستاگرام', 'https://instagram.com/limocafe', 1, 6);

