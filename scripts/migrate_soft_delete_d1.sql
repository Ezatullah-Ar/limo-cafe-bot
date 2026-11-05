-- افزودن ستون deleted_at جهت پشتیبانی از سطل زباله ۳۰ روزه
ALTER TABLE orders ADD COLUMN deleted_at DATETIME;
ALTER TABLE users ADD COLUMN deleted_at DATETIME;
ALTER TABLE service_items ADD COLUMN deleted_at DATETIME;
ALTER TABLE service_categories ADD COLUMN deleted_at DATETIME;
ALTER TABLE seasonal_campaigns ADD COLUMN deleted_at DATETIME;
ALTER TABLE communication_channels ADD COLUMN deleted_at DATETIME;
ALTER TABLE website_monitors ADD COLUMN deleted_at DATETIME;
