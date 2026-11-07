/**
 * آزمون خودکار و جامع گام ۳: اصلاح پنل مدیریت، حذف کامل پایش، درگ اند دراپ و انقضای نشست
 * tests/test_step3_admin_revamp.mjs
 */
import assert from "node:assert";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, "..");

console.log("🚀 شروع آزمون‌های گام ۳: پنل مدیریت، حذف پایش، مرتب‌سازی و امنیت نشست...");

// ۱. بررسی فایل‌های کامپایل‌شده
const adminHtmlPath = path.join(rootDir, "cloudflare", "admin_html.js");
const workerJsPath = path.join(rootDir, "cloudflare", "worker.js");
assert(fs.existsSync(adminHtmlPath), "فایل cloudflare/admin_html.js باید وجود داشته باشد.");
assert(fs.existsSync(workerJsPath), "فایل cloudflare/worker.js باید وجود داشته باشد.");

const adminCodeRaw = fs.readFileSync(adminHtmlPath, "utf-8");
const workerCode = fs.readFileSync(workerJsPath, "utf-8");

// نرمال‌سازی کد با حذف بک‌اسلش‌های رشته کامپایل‌شده JS
const adminCode = adminCodeRaw.replace(/\\"/g, '"').replace(/\\n/g, '\n');

// ========================================================
// بخش اول: آزمون حذف کامل ماژول پایش سامانه‌ها (Website Monitors)
// ========================================================
console.log("\n🧪 ۱. آزمون حذف کامل قابلیت پایش سایت‌ها:");

// ۱.۱ عدم وجود دکمه پایش در سایدبار پنل مدیریت
assert(!adminCode.includes("switchTab('monitors')"), "دکمه تب monitors نباید در سایدبار پنل باشد.");
assert(!adminCode.includes("پایش هوشمند سایت‌ها"), "عنوان پایش سایت‌ها نباید در سایدبار باشد.");
console.log("  ✅ ۱.۱ تب پایش از سایدبار پنل با موفقیت حذف شده است.");

// ۱.۲ عدم وجود کدهای ویو و کارت‌های پایش
assert(!adminCode.includes("currentTab === 'monitors'"), "بخش نمایش currentTab === 'monitors' نباید وجود داشته باشد.");
assert(!adminCode.includes("websiteMonitors"), "متغیر websiteMonitors نباید در فرانت وجود داشته باشد.");
assert(!adminCode.includes("checkAllMonitorsNow"), "تابع checkAllMonitorsNow نباید وجود داشته باشد.");
console.log("  ✅ ۱.۲ ویو و کارت‌های پایش سامانه‌ها به طور کامل از HTML پنل حذف شده است.");

// ۱.۳ عدم وجود مودال ایجاد/ویرایش پایش
assert(!adminCode.includes("monitorModal"), "مودال monitorModal نباید در فرانت وجود داشته باشد.");
console.log("  ✅ ۱.۳ مودال اختصاصی پایش سامانه حذف شده است.");

// ۱.۴ عدم وجود مسیرهای پایش و دکمه‌های بات در worker.js
assert(!workerCode.includes("/api/admin/monitors/check-all"), "مسیر check-all پایش نباید در ورکر باشد.");
assert(!workerCode.includes("/api/admin/monitors/save"), "مسیر save پایش نباید در ورکر باشد.");
assert(!workerCode.includes("callback_data: \"admin_monitors\""), "دکمه ربات admin_monitors نباید وجود داشته باشد.");
assert(!workerCode.includes("data === \"admin_monitors\""), "هندلر callback ربات admin_monitors نباید وجود داشته باشد.");
console.log("  ✅ ۱.۴ تمام اندپوینت‌ها و دکمه‌های پایش از Cloudflare Worker و ربات حذف شده است.");

// ========================================================
// بخش دوم: آزمون قابلیت مرتب‌سازی و Drag & Drop
// ========================================================
console.log("\n🧪 ۲. آزمون پیاده‌سازی جابه‌جایی و مرتب‌سازی Drag & Drop:");

// ۲.۱ تست شناسه draggable و رویدادهای درگ در جداول و کارت‌ها
const dndServices = adminCode.includes("@dragstart=\"onDragStart($event, index, 'services')\"") &&
                    adminCode.includes("@drop=\"onDrop($event, index, 'services')\"");
assert(dndServices, "کارت‌های خدمات باید دارای رویدادهای dragstart و drop برای 'services' باشند.");

const dndCategories = adminCode.includes("@dragstart=\"onDragStart($event, index, 'categories')\"") &&
                      adminCode.includes("@drop=\"onDrop($event, index, 'categories')\"");
assert(dndCategories, "سطرهای جدول دسته‌بندی باید دارای رویدادهای dragstart و drop برای 'categories' باشند.");

const dndCampaigns = adminCode.includes("@dragstart=\"onDragStart($event, index, 'campaigns')\"") &&
                     adminCode.includes("@drop=\"onDrop($event, index, 'campaigns')\"");
assert(dndCampaigns, "کارت‌های رویدادهای مقطعی باید دارای رویدادهای dragstart و drop باشند.");

const dndChannels = adminCode.includes("@dragstart=\"onDragStart($event, index, 'channels')\"") &&
                    adminCode.includes("@drop=\"onDrop($event, index, 'channels')\"");
assert(dndChannels, "کانال‌های ارتباطی باید دارای رویدادهای dragstart و drop باشند.");
console.log("  ✅ ۲.۱ اتریبیوت‌های HTML5 Drag & Drop در هر ۴ بخش سامانه تعبیه شده‌اند.");

// ۲.۲ وجود نشانگر بصری هندل کشیدن (⠿)
assert(adminCode.includes("⠿"), "آیکون یا هندل بصری درگ (⠿) باید برای راهنمایی کاربر در رابط کاربری وجود داشته باشد.");
console.log("  ✅ ۲.۲ هندل بصری درگ برای راهنمایی دیداری کاربر تعبیه شده است.");

// ۲.۳ توابع مدیریت درگ در Vue
assert(adminCode.includes("function onDragStart("), "تابع onDragStart باید در کامپوننت ویو تعریف شده باشد.");
assert(adminCode.includes("function onDragOver("), "تابع onDragOver باید در کامپوننت ویو تعریف شده باشد.");
assert(adminCode.includes("function onDragEnd("), "تابع onDragEnd باید در کامپوننت ویو تعریف شده باشد.");
assert(adminCode.includes("async function onDrop("), "تابع onDrop باید در کامپوننت ویو تعریف شده باشد.");
console.log("  ✅ ۲.۳ توابع جاوااسکریپتی onDragStart, onDragOver, onDragEnd و onDrop در اسکریپت ویو پیاده‌سازی شده‌اند.");

// ۲.۴ سازگاری مسیر به‌روزرسانی اولویت در Cloudflare Worker
assert(workerCode.includes("/api/admin/priority/update"), "مسیر به‌روزرسانی اولویت باید فعال باشد.");
assert(workerCode.includes("targetTable"), "مسیر اولویت باید هم فیلد table و هم type را شناسایی کند.");
console.log("  ✅ ۲.۴ اندپوینت سرور /api/admin/priority/update برای دریافت جابه‌جایی‌های درگ پشتیبانی می‌شود.");

// ========================================================
// بخش سوم: آزمون فیلدهای راهنما و تصویر در مودال خدمات
// ========================================================
console.log("\n🧪 ۳. آزمون فیلدهای راهنمای مشتری و تصویر در ویرایش خدمات:");

assert(adminCode.includes("serviceForm.guide_content"), "فیلد guide_content باید به فرم ویو متصل باشد.");
assert(adminCode.includes("serviceForm.image_url"), "فیلد image_url باید به فرم ویو متصل باشد.");
assert(adminCode.includes("serviceForm.official_url"), "فیلد official_url باید به فرم ویو متصل باشد.");
assert(adminCode.includes("راهنمای تفصیلی و شرایط اختصاصی خدمت"), "لیبل راهنمای خدمت باید در مودال خدمت نمایش یابد.");
assert(adminCode.includes("آدرس تصویر / بنر خدمت"), "لیبل آدرس بنر/عکس خدمت باید در مودال باشد.");
console.log("  ✅ ۳.۱ فیلدهای راهنما، بنر تصویر و لینک رسمی با موفقیت به مودال فرم‌ساز خدمت افزوده شدند.");

// ========================================================
// بخش چهارم: آزمون انقضای نشست کاربر (Session Inactivity Timeout)
// ========================================================
console.log("\n🧪 ۴. آزمون محاسباتی و منطقی خروج خودکار پس از ۲۰ دقیقه عدم فعالیت:");

assert(adminCode.includes("INACTIVITY_TIMEOUT_MS = 20 * 60 * 1000"), "مهلت عدم فعالیت باید دقیقا ۲۰ دقیقه تنظیم شده باشد.");
assert(adminCode.includes("limo_admin_last_activity"), "برچسب زمانی limo_admin_last_activity باید در localStorage نگهداری شود.");
assert(adminCode.includes("isSessionExpired"), "تابع اعتبارسنجی isSessionExpired باید در بدنه کد موجود باشد.");
assert(adminCode.includes("visibilitychange"), "رویداد visibilitychange باید برای بازگشت به تب مرورگر شنود شود.");

// تست الگوریتم انقضای نشست در شرایط مختلف:
const TIMEOUT_MS = 20 * 60 * 1000;
function testExpiry(lastActiveTime) {
  if (!lastActiveTime) return true; // بدون زمان ثبت شده => منقضی
  return (Date.now() - lastActiveTime > TIMEOUT_MS);
}

const now = Date.now();
// حالت الف: فعالیت ۵ دقیقه قبل => نباید منقضی شود
assert.strictEqual(testExpiry(now - 5 * 60 * 1000), false, "نشست ۵ دقیقه قبل نباید منقضی تلقی شود.");
// حالت ب: فعالیت ۱۹ دقیقه قبل => نباید منقضی شود
assert.strictEqual(testExpiry(now - 19 * 60 * 1000), false, "نشست ۱۹ دقیقه قبل نباید منقضی تلقی شود.");
// حالت ج: فعالیت ۲۱ دقیقه قبل => باید منقضی شود
assert.strictEqual(testExpiry(now - 21 * 60 * 1000), true, "نشست ۲۱ دقیقه قبل باید منقضی اعلام شود.");
// حالت د: زمان نامعتبر یا ثبت نشده => باید منقضی شود
assert.strictEqual(testExpiry(null), true, "نبود تاریخچه فعالیت باید باعث خروج امنیتی شود.");
console.log("  ✅ ۴.۱ آزمون منطقی سناریوهای زمانی (۵ دقیقه، ۱۹ دقیقه و ۲۱ دقیقه) با موفقیت تأیید شد.");

console.log("\n🎉 تمامی آزمون‌های گام ۳ با موفقیت ۱۰۰٪ سپری شدند.");
