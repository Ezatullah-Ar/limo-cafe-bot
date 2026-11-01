-- Phase 8 D1 Tables & Seeding
CREATE TABLE IF NOT EXISTS order_audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    actor_id INTEGER NOT NULL,
    from_status TEXT NOT NULL,
    to_status TEXT NOT NULL,
    note TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS communication_channels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    value TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    order_priority INTEGER NOT NULL DEFAULT 0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_comm_channels_key ON communication_channels(key);

CREATE TABLE IF NOT EXISTS system_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL,
    description TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_settings_key ON system_settings(key);

-- Seed System Settings
INSERT OR IGNORE INTO system_settings (key, value, description)
VALUES 
('witness_provision_fee', '3500000', 'هزینه تامین شاهد رسمی توسط کافی نت (به ریال)'),
('enable_animations', '0', 'فعال‌سازی انیمیشن‌های سبک تلگرام (1=فعال، 0=غیرفعال)');

-- Seed Channels
INSERT OR IGNORE INTO communication_channels (key, title, value, is_active, order_priority)
VALUES
('PHONE', 'تلفن تماس کافی‌نت', '09120000000', 1, 1),
('TELEGRAM', 'کانال و پشتیبانی تلگرام', 'https://t.me/LimoCafeBot', 1, 2),
('EITAA', 'کانال رسمی ایتا', 'https://eitaa.com/limocafe', 1, 3),
('RUBIKA', 'کانال روبیکا', 'https://rubika.ir/limocafe', 1, 4),
('BALE', 'کانال بله', 'https://ble.ir/limocafe', 1, 5),
('INSTAGRAM', 'صفحه اینستاگرام', 'https://instagram.com/limocafe', 1, 6),
('WORKING_HOURS', 'ساعت کاری دفتر', 'همه‌روزه از ۸:۰۰ صبح الی ۲۱:۰۰ شب', 1, 7);
