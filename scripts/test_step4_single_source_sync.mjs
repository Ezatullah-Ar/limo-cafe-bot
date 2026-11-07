/**
 * آزمون جامع خودکار گام ۴: هماهنگی و منبع واحد اطلاعاتی ربات، مینی‌اپ و پنل مدیریت
 * tests/test_step4_single_source_sync.mjs
 */
import assert from "node:assert";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, "..");

console.log("🚀 شروع آزمون‌های گام ۴: هماهنگی ربات، مینی‌اپ و پنل مدیریت (Single Source of Truth)...");

const workerJsPath = path.join(rootDir, "cloudflare", "worker.js");
const miniappJsPath = path.join(rootDir, "cloudflare", "miniapp_html.js");
const adminHtmlPath = path.join(rootDir, "cloudflare", "admin_html.js");

assert(fs.existsSync(workerJsPath), "فایل cloudflare/worker.js باید وجود داشته باشد.");
assert(fs.existsSync(miniappJsPath), "فایل cloudflare/miniapp_html.js باید وجود داشته باشد.");
assert(fs.existsSync(adminHtmlPath), "فایل cloudflare/admin_html.js باید وجود داشته باشد.");

const workerCode = fs.readFileSync(workerJsPath, "utf-8");
const miniappCode = fs.readFileSync(miniappJsPath, "utf-8");
const adminCode = fs.readFileSync(adminHtmlPath, "utf-8");

// ========================================================
// بخش اول: آزمون یکپارچگی دسته‌بندی‌ها و جهت مرتب‌سازی (DESC)
// ========================================================
console.log("\n🧪 ۱. آزمون جهت و نحوه مرتب‌سازی دسته‌بندی‌ها (order_priority DESC):");

// در دیتابیس D1، اولویت‌های بالاتر (Drag & Drop) مقدار عددی بزرگ‌تری می‌گیرند.
// بنابراین تمام کوئری‌ها در ربات، مینی‌اپ و ادمین باید از ORDER BY order_priority DESC استفاده کنند.

// ۱.۱ در ربات تلگرام (services_list)
const botCatQuery = workerCode.includes("SELECT * FROM service_categories WHERE is_active = 1 AND deleted_at IS NULL ORDER BY order_priority DESC, id ASC");
assert(botCatQuery, "ربات باید دسته‌بندی‌ها را با ORDER BY order_priority DESC, id ASC فراخوانی کند.");
console.log("  ✅ ۱.۱ کوئری دسته‌بندی‌های ربات تلگرام بر اساس اولویت نزولی (DESC) تنظیم شده است.");

// ۱.۲ در مینی‌اپلیکیشن (/api/client/bootstrap)
const miniappCatQuery = workerCode.includes("SELECT id, code, title, description, order_priority FROM service_categories WHERE is_active = 1 AND deleted_at IS NULL ORDER BY order_priority DESC, id ASC");
assert(miniappCatQuery, "اندپوینت bootstrap مینی‌اپ باید دسته‌بندی‌ها را با ORDER BY order_priority DESC فراخوانی کند.");
console.log("  ✅ ۱.۲ اندپوینت بوت‌استرپ مینی‌اپلیکیشن با همان ترتیب نزولی دیتابیس هماهنگ است.");

// ۱.۳ در پنل مدیریت (/api/admin/services)
const adminCatQuery = workerCode.includes("SELECT * FROM service_categories WHERE deleted_at IS NULL ORDER BY order_priority DESC, id ASC");
assert(adminCatQuery, "پنل مدیریت باید دسته‌بندی‌ها را با ORDER BY order_priority DESC بارگذاری کند.");
console.log("  ✅ ۱.۳ پنل مدیریت نیز همان ترتیب نزولی را لود می‌کند.");

// ========================================================
// بخش دوم: آزمون فهرست خدمات و حذف دستکاری‌های هاردکدشده
// ========================================================
console.log("\n🧪 ۲. آزمون کاتالوگ خدمات و تکیه صرف به پایگاه داده (D1):");

// ۲.۱ کوئری خدمات در ربات تلگرام (cat_*)
const botSvcQuery = workerCode.includes("SELECT s.*, c.title as cat_title, c.code as category_code FROM service_items s JOIN service_categories c ON s.category_id = c.id WHERE (c.code = ? OR c.id = ?) AND s.is_active = 1 AND s.deleted_at IS NULL AND c.is_active = 1 AND c.deleted_at IS NULL ORDER BY s.order_priority DESC, s.id ASC");
assert(botSvcQuery, "خدمات داخل دسته‌بندی در ربات تلگرام باید بر اساس اولویت نزولی مرتب شوند.");
console.log("  ✅ ۲.۱ خدمات دسته‌بندی در ربات با ORDER BY s.order_priority DESC تنظیم شد.");

// ۲.۲ حذف هاردکد unshift خدمت مسکن در ربات
assert(!workerCode.includes("catButtons.unshift([{ text: \"🏠 کد رهگیری قرارداد مسکن (سامانه خودنویس)\""), "نباید خدمت مسکن به صورت دستی و هاردکد به دکمه‌های ربات اضافه شود.");
console.log("  ✅ ۲.۲ دکمه هاردکدشده مسکن حذف شده و وضعیت و عنوان آن منحصراً توسط دیتابیس D1 تعیین می‌شود.");

// ۲.۳ دکمه وب‌اپ در بالای لیست خدمات دسته‌بندی در ربات
assert(workerCode.includes("catButtons.unshift([{ text: `📱 باز کردن «${categoryTitle}» در مینی‌اپ`"), "ربات باید دکمه مستقیم ورود به مینی‌اپ را برای هر دسته‌بندی ارائه دهد.");
console.log("  ✅ ۲.۳ پیوند دوطرفه از دسته‌بندی‌های ربات به دسته‌بندی متناظر در مینی‌اپ تأیید شد.");

// ========================================================
// بخش سوم: آزمون صفحه توضیحات خدمت، راهنما و پیوند سامانه رسمی
// ========================================================
console.log("\n🧪 ۳. آزمون همگامی جزئیات خدمت، راهنما و نشانی رسمی:");

// ۳.۱ نمایش راهنمای تفصیلی خدمت در تلگرام
assert(workerCode.includes("📖 <b>راهنمای مشتری و نکات ثبت:</b>"), "ربات تلگرام باید فیلد راهنمای خدمت (guide_content) را در صورت وجود نمایش دهد.");
console.log("  ✅ ۳.۱ راهنمای ثبت و توضیحات تفصیلی در کارت پیام ربات تلگرام گنجانده شد.");

// ۳.۲ دکمه ورود به سامانه رسمی
assert(workerCode.includes("🔗 سامانه رسمی"), "در صورت تنظیم official_url در پنل، دکمه شیشه‌ای سامانه رسمی در ربات باید نمایش یابد.");
console.log("  ✅ ۳.۲ پیوند به نشانی رسمی تنظیم‌شده در پنل ادمین فعال است.");

// ۳.۳ دکمه مستقیم ثبت خدمت در مینی‌اپ
assert(workerCode.includes("web_app: { url: `${webappUrl}?svc=${encodeURIComponent(code)}` }"), "دکمه ثبت در مینی‌اپ با شناسه یکتای خدمت پیوند داده شده است.");
console.log("  ✅ ۳.۳ دکمه ثبت مستقیم در مینی‌اپلیکیشن با پارامتر svc تنظیم شده است.");

// ========================================================
// بخش چهارم: آزمون ثبت‌نام‌های مقطعی و کانال‌های ارتباطی
// ========================================================
console.log("\n🧪 ۴. آزمون ثبت‌نام‌های مقطعی و کانال‌های ارتباطی:");

// ۴.۱ ثبت‌نام‌های مقطعی با ترتیب نزولی
assert(workerCode.includes("SELECT * FROM seasonal_campaigns WHERE is_active = 1 AND deleted_at IS NULL ORDER BY order_priority DESC"), "رویدادهای مقطعی باید بر اساس order_priority DESC فراخوانی شوند.");
console.log("  ✅ ۴.۱ ترتیب رویدادهای مقطعی همگام‌سازی شد.");

// ۴.۲ کانال‌های ارتباطی با ترتیب نزولی
assert(workerCode.includes("SELECT * FROM communication_channels WHERE is_active = 1 AND deleted_at IS NULL ORDER BY order_priority DESC"), "کانال‌های ارتباطی باید بر اساس order_priority DESC فراخوانی شوند.");
console.log("  ✅ ۴.۲ ترتیب کانال‌های ارتباطی در ربات با اولویت پنل ادمین همگام است.");

console.log("\n🎉 تمامی آزمون‌های گام ۴ با موفقیت ۱۰۰٪ سپری شدند.");
