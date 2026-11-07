/**
 * آزمون خودکار جامع گام ۵: بررسی واکنش‌گرایی (Responsive Design) در ابعاد موبایل، تبلت و دسکتاپ
 * tests/test_step5_responsive_qa.mjs
 */
import assert from "node:assert";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, "..");

console.log("🚀 شروع آزمون‌های گام ۵: ارزیابی ریسپانسیو در ابعاد موبایل (۳۶۰px)، تبلت و دسکتاپ...");

const miniappJsPath = path.join(rootDir, "cloudflare", "miniapp_html.js");
const adminHtmlPath = path.join(rootDir, "cloudflare", "admin_html.js");

assert(fs.existsSync(miniappJsPath), "فایل cloudflare/miniapp_html.js باید وجود داشته باشد.");
assert(fs.existsSync(adminHtmlPath), "فایل cloudflare/admin_html.js باید وجود داشته باشد.");

const miniappRaw = fs.readFileSync(miniappJsPath, "utf-8");
const adminRaw = fs.readFileSync(adminHtmlPath, "utf-8");

const miniappHtml = miniappRaw.replace(/\\"/g, '"').replace(/\\n/g, '\n');
const adminHtml = adminRaw.replace(/\\"/g, '"').replace(/\\n/g, '\n');

// ========================================================
// بخش اول: متاتگ‌های Viewport و مدیریت حاشیه‌های امن (Safe Area)
// ========================================================
console.log("\n🧪 ۱. آزمون تنظیمات Viewport و Safe Area Insets در موبایل:");

// ۱.۱ متاتگ Viewport مینی‌اپلیکیشن
assert(miniappHtml.includes('name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover"'), "مینی‌اپ باید از viewport-fit=cover جهت تطابق با بریدگی صفحه (Notch) و دکمه هوم استفاده کند.");
console.log("  ✅ ۱.۱ متاتگ Viewport مینی‌اپ با viewport-fit=cover تایید شد.");

// ۱.۲ حاشیه امن نوار ناوبری پایین صفحه مینی‌اپ
assert(miniappHtml.includes("env(safe-area-inset-bottom"), "نوار پایین صفحه مینی‌اپ باید پدینگ حاشیه امن داشته باشد.");
console.log("  ✅ ۱.۲ پدینگ تطبیقی safe-area-inset-bottom در مینی‌اپ تعبیه شد.");

// ۱.۳ متاتگ Viewport پنل مدیریت
assert(adminHtml.includes('name="viewport" content="width=device-width, initial-scale=1.0"'), "پنل ادمین باید دارای متاتگ استاندارد responsive viewport باشد.");
console.log("  ✅ ۱.۳ متاتگ Viewport پنل مدیریت برای صفحات موبایل و تبلت فعال است.");

// ========================================================
// بخش دوم: آزمون واکنش‌گرایی جداول در صفحه ۳۶۰px (Overflow-X Auto)
// ========================================================
console.log("\n🧪 ۲. آزمون ریسپانسیو بودن جداول و جلوگیری از اسکرول ناخواسته صفحه در موبایل:");

// بررسی وجود محفظه اسکرول افقی مستقل برای تمامی جداول
const tableCount = (adminHtml.match(/<table/g) || []).length;
const overflowContainerCount = (adminHtml.match(/class="overflow-x-auto">/g) || []).length;

assert(tableCount > 0, "حداقل باید چند جدول مدیریتی در پنل وجود داشته باشد.");
assert.strictEqual(tableCount, overflowContainerCount, `تمامی ${tableCount} جدول باید داخل محفظه overflow-x-auto قرار گیرند تا در صفحه ۳۶۰px از کادر بیرون نزنند.`);
console.log(`  ✅ ۲.۱ تمامی ${tableCount} جدول پنل مدیریت دارای پوشش overflow-x-auto هستند.`);

// ========================================================
// بخش سوم: آزمون منوی کشویی واکنش‌گرا (Off-Canvas Drawer) در تبلت و موبایل
// ========================================================
console.log("\n🧪 ۳. آزمون سایدبار واکنش‌گرا در حالت دسکتاپ، تبلت و موبایل:");

// ۳.۱ دکمه منوی همبرگری برای موبایل و تبلت (xl:hidden)
assert(adminHtml.includes('xl:hidden') && adminHtml.includes('mobileSidebarOpen = true'), "دکمه باز کردن منو در ابعاد موبایل و تبلت باید موجود باشد.");
console.log("  ✅ ۳.۱ دکمه باز کردن سایدبار به صورت منوی همبرگری در تبلت و موبایل تعبیه شده است.");

// ۳.۲ پس‌زمینه نیمه‌شفاف و کلیک برای بستن
assert(adminHtml.includes('mobileSidebarOpen = false'), "کلیک روی لایه بک‌دراپ یا دکمه ضربدر باید سایدبار موبایل را ببندد.");
console.log("  ✅ ۳.۲ قابلیت بستن خودکار سایدبار کشویی در موبایل با کلیک روی پس‌زمینه تأیید شد.");

// ۳.۳ بستن خودکار منو پس از انتخاب تب
assert(adminHtml.includes("mobileSidebarOpen.value = false"), "پس از کلیک روی هر آیتم، سایدبار موبایل باید خودکار بسته شود.");
console.log("  ✅ ۳.۳ بستن خودکار منو پس از سوئیچ تب تأیید شد.");

// ========================================================
// بخش چهارم: آزمون اسکرول‌پذیری و واکنش‌گرایی مودال‌ها
// ========================================================
console.log("\n🧪 ۴. آزمون ریسپانسیو بودن پنجره‌های شناور (Modals):");

// ۴.۱ محدودیت ارتفاع و اسکرول داخلی برای دستگاه‌های با ارتفاع کم
assert(adminHtml.includes('max-h-[92vh]') || adminHtml.includes('max-h-[90vh]'), "مودال‌ها باید حداکثر ارتفاع ۹۰ تا ۹۲ درصد ارتفاع صفحه داشته باشند.");
assert(adminHtml.includes('overflow-y-auto'), "بدنه مودال‌ها باید دارای اسکرول عمودی مجزا باشند تا دکمه ذخیره در دسترس بماند.");
console.log("  ✅ ۴.۱ اسکرول‌پذیری داخلی و ساختار ریسپانسیو پنجره‌های مودال تأیید شد.");

// ۴.۲ ساختار واکنش‌گرای مینی‌اپ در تبلت و دسکتاپ
assert(miniappHtml.includes('max-w-md md:max-w-xl mx-auto'), "مینی‌اپ باید در تبلت و دسکتاپ عرض متناسب md:max-w-xl با وسط‌چین داشته باشد.");
console.log("  ✅ ۴.۲ ساختار عرض مینی‌اپ در موبایل و دسکتاپ تطبیق یافت.");

console.log("\n🎉 تمامی آزمون‌های ریسپانسیو و کنترل کیفی گام ۵ با موفقیت ۱۰۰٪ سپری شدند.");
