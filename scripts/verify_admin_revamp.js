// scripts/verify_admin_revamp.js
// آزمون جامع و زنده تمام قابلیت‌های بازآرایی پنل مدیریت کافی‌نت لیمو

const BASE_URL = "https://limo-cafe-bot.bakhtar-visasup.workers.dev";
const AUTH_HEADER = "Basic " + Buffer.from("admin:limo_admin_2026").toString("base64");

async function runTests() {
  console.log("🚀 Starting comprehensive live verification of Admin Dashboard Revamp...\n");
  let passed = 0;
  let failed = 0;

  function assert(condition, message) {
    if (condition) {
      console.log(`  ✅ [PASS] ${message}`);
      passed++;
    } else {
      console.error(`  ❌ [FAIL] ${message}`);
      failed++;
    }
  }

  // 1. تست بارگذاری صفحه /admin و بررسی طراحی ستون راست (Right-Sidebar Layout)
  console.log("--- 1. تست بارگذاری پنل مدیریت تحت وب (/admin) ---");
  try {
    const res = await fetch(`${BASE_URL}/admin`);
    const html = await res.text();
    assert(res.status === 200, "صفحه /admin با وضعیت HTTP 200 پاسخ می‌دهد.");
    assert(html.includes("w-68 bg-slate-900"), "سایدبار راست تیره با عرض استاندارد w-68 وجود دارد.");
    assert(html.includes("سطل زباله (۳۰ روزه)"), "ماژول سطل زباله ۳۰ روزه در منو قرار دارد.");
    assert(html.includes("پشتیبان‌گیری داده‌ها"), "ماژول پشتیبان‌گیری در منو قرار دارد.");
    assert(html.includes("پل همگام‌سازی با نرم‌افزار کافی‌نت"), "بخش Shop Sync Bridge در صفحه وجود دارد.");
  } catch (e) {
    assert(false, "خطا در بارگذاری /admin: " + e.message);
  }

  // 2. تست اندپوینت آماری و داده‌های اصلی ادمین (/api/admin/data)
  console.log("\n--- 2. تست احراز هویت و دریافت داده‌های اولیه داشبورد ---");
  try {
    const res = await fetch(`${BASE_URL}/api/admin/data`, {
      headers: { Authorization: AUTH_HEADER }
    });
    const data = await res.json();
    assert(res.status === 200 && data.ok === true, "احراز هویت ادمین موفقیت‌آمیز است و ok: true بازمی‌گردد.");
    assert(data.stats && typeof data.stats.total_orders === 'number', "آمار کل سفارشات در stats برگردانده شد.");
    assert(Array.isArray(data.orders), "آرایه سفارشات معتبر است.");
    assert(Array.isArray(data.monitors), "آرایه مانیتورها معتبر است.");
  } catch (e) {
    assert(false, "خطا در /api/admin/data: " + e.message);
  }

  // 3. تست ایجاد دستی مشتری جدید در CRM (/api/admin/customer/create)
  console.log("\n--- 3. تست ثبت مشتری دستی جدید در CRM ---");
  let testUserId = null;
  const mockTgId = 880000000 + Math.floor(Math.random() * 90000);
  try {
    const res = await fetch(`${BASE_URL}/api/admin/customer/create`, {
      method: "POST",
      headers: { Authorization: AUTH_HEADER, "Content-Type": "application/json" },
      body: JSON.stringify({
        full_name: "تست ربات لیمو آزمون CRM",
        phone_number: "09129998877",
        national_code: "0012345678",
        alien_code: "99887766",
        telegram_id: mockTgId,
        username: "limo_crm_test",
        notes: "ثبت شده توسط آزمون خودکار برای اعتبارسنجی CRM"
      })
    });
    const data = await res.json();
    assert(res.status === 200 && data.ok === true, "مشتری دستی با موفقیت ایجاد شد.");
    testUserId = data.id;
    assert(typeof testUserId === 'number' && testUserId > 0, `شناسه مشتری جدید ایجاد شد: #${testUserId}`);
  } catch (e) {
    assert(false, "خطا در ایجاد مشتری: " + e.message);
  }

  // 4. تست شارژ دستی کیف پول متقاضی (/api/admin/wallet/adjust)
  console.log("\n--- 4. تست شارژ دستی کیف پول مشتری در CRM ---");
  try {
    const res = await fetch(`${BASE_URL}/api/admin/wallet/adjust`, {
      method: "POST",
      headers: { Authorization: AUTH_HEADER, "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: testUserId,
        amount: 350000,
        notes: "شارژ آزمایشی کیف پول جهت تست CRM لیمو",
        type: "TOPUP"
      })
    });
    const data = await res.json();
    assert(res.status === 200 && data.ok === true, "شارژ دستی کیف پول متقاضی با موفقیت اعمال شد.");
  } catch (e) {
    assert(false, "خطا در شارژ کیف پول: " + e.message);
  }

  // 5. تست دریافت پرونده جامع مشتری (Customer Dossier)
  console.log("\n--- 5. تست دریافت پرونده جامع متقاضی (Dossier) ---");
  try {
    const res = await fetch(`${BASE_URL}/api/admin/customer/dossier?user_id=${testUserId}`, {
      headers: { Authorization: AUTH_HEADER }
    });
    const data = await res.json();
    assert(res.status === 200 && data.ok === true, "پرونده متقاضی با موفقیت فراخوانی شد.");
    assert(data.dossier && data.dossier.user.full_name === "تست ربات لیمو آزمون CRM", "اطلاعات هویتی متقاضی در پرونده مطابقت دارد.");
    assert(data.dossier.user.username === "limo_crm_test", "نام کاربری تلگرام متقاضی ذخیره و فراخوانی شد.");
    assert(data.dossier.wallet.balance === 350000, "مانده کیف پول پس از شارژ دستی ۳۵۰,۰۰۰ تومان است.");
  } catch (e) {
    assert(false, "خطا در پرونده مشتری: " + e.message);
  }

  // 6. تست چرخه کامل سطل زباله ۳۰ روزه: حذف نرم‌افزاری -> نمایش در سطل -> بازیابی -> حذف دائمی
  console.log("\n--- 6. تست چرخه کامل سطل زباله ۳۰ روزه (Soft Delete Trash) ---");
  try {
    // ۶-۱: انتقال مشتری به سطل زباله
    const delRes = await fetch(`${BASE_URL}/api/admin/customer/delete`, {
      method: "POST",
      headers: { Authorization: AUTH_HEADER, "Content-Type": "application/json" },
      body: JSON.stringify({ id: testUserId })
    });
    assert(delRes.status === 200, "درخواست حذف نرم‌افزاری مشتری با موفقیت ارسال شد.");

    // ۶-۲: بررسی وجود مشتری در سطل زباله ۳۰ روزه با مهلت انقضا
    const trashRes = await fetch(`${BASE_URL}/api/admin/trash/items`, {
      headers: { Authorization: AUTH_HEADER }
    });
    const trashData = await trashRes.json();
    const itemInTrash = (trashData.items || []).find(i => i.table === 'user' && i.id === testUserId);
    assert(!!itemInTrash, "مشتری حذف‌شده در لیست سطل زباله ۳۰ روزه یافت شد.");
    assert(itemInTrash && itemInTrash.days_left >= 29, `مهلت نگهداری در سطل زباله محاسبه شد: ${itemInTrash?.days_left} روز مانده`);

    // ۶-۳: بازیابی مشتری از سطل زباله (Restore)
    const restoreRes = await fetch(`${BASE_URL}/api/admin/trash/restore`, {
      method: "POST",
      headers: { Authorization: AUTH_HEADER, "Content-Type": "application/json" },
      body: JSON.stringify({ table: 'user', id: testUserId })
    });
    const restoreData = await restoreRes.json();
    assert(restoreData.ok === true, "مشتری با موفقیت از سطل زباله بازیابی شد.");

    // ۶-۴: بررسی خروج از سطل زباله
    const trashRes2 = await fetch(`${BASE_URL}/api/admin/trash/items`, {
      headers: { Authorization: AUTH_HEADER }
    });
    const trashData2 = await trashRes2.json();
    const itemInTrash2 = (trashData2.items || []).find(i => i.table === 'user' && i.id === testUserId);
    assert(!itemInTrash2, "مشتری بازیابی‌شده دیگر در سطل زباله وجود ندارد و فعال است.");

    // ۶-۵: حذف مجدد و پاک‌سازی دائمی جهت تمیز ماندن دیتابیس (Permanent Purge)
    await fetch(`${BASE_URL}/api/admin/customer/delete`, {
      method: "POST",
      headers: { Authorization: AUTH_HEADER, "Content-Type": "application/json" },
      body: JSON.stringify({ id: testUserId })
    });
    const purgeRes = await fetch(`${BASE_URL}/api/admin/trash/purge`, {
      method: "POST",
      headers: { Authorization: AUTH_HEADER, "Content-Type": "application/json" },
      body: JSON.stringify({ table: 'user', id: testUserId })
    });
    const purgeData = await purgeRes.json();
    assert(purgeData.ok === true, "پاک‌سازی و حذف همیشگی (Purge) مشتری آزمایشی با موفقیت انجام شد.");
  } catch (e) {
    assert(false, "خطا در تست سطل زباله: " + e.message);
  }

  // 7. تست ذخیره خدمت، فرم‌ساز فیلدهای پویا و تنظیم هزینه شاهدان
  console.log("\n--- 7. تست فرم‌ساز خدمات و تنظیم هزینه شاهدان ---");
  try {
    // ابتدا شناسه خدمت کد رهگیری را پیدا می‌کنیم
    const svcListRes = await fetch(`${BASE_URL}/api/admin/services`, { headers: { Authorization: AUTH_HEADER } });
    const svcListData = await svcListRes.json();
    const housingSvc = (svcListData.services || []).find(s => s.code === "HOUSING_TRACKING_CODE") || { id: 7 };

    const res = await fetch(`${BASE_URL}/api/admin/service/save`, {
      method: "POST",
      headers: { Authorization: AUTH_HEADER, "Content-Type": "application/json" },
      body: JSON.stringify({
        id: housingSvc.id,
        category_id: housingSvc.category_id || 1,
        code: "HOUSING_TRACKING_CODE",
        title: "کد رهگیری قرارداد مسکن (سامانه خودنویس)",
        witness_fee: 3500000,
        required_fields: {
          landlord_name: { label: "نام موجر", type: "text", required: true },
          tenant_name: { label: "نام مستأجر", type: "text", required: true },
          postal_code: { label: "کد پستی ملک", type: "text", required: true }
        }
      })
    });
    const data = await res.json();
    assert(res.status === 200 && data.ok === true, "خدمت با فیلدهای فرم‌ساز پویا و هزینه شاهدان ذخیره شد.");
  } catch (e) {
    assert(false, "خطا در ذخیره خدمت: " + e.message);
  }

  // 8. تست تغییر وضعیت کانال ارتباطی
  console.log("\n--- 8. تست فعال/غیرفعال‌سازی کانال ارتباطی ---");
  try {
    const res = await fetch(`${BASE_URL}/api/admin/channel/toggle`, {
      method: "POST",
      headers: { Authorization: AUTH_HEADER, "Content-Type": "application/json" },
      body: JSON.stringify({ id: 1, is_active: 1 })
    });
    const data = await res.json();
    assert(res.status === 200 && data.ok === true, "تغییر وضعیت فعال‌سازی کانال ارتباطی با موفقیت ثبت شد.");
  } catch (e) {
    assert(false, "خطا در تغییر وضعیت کانال: " + e.message);
  }

  // 9. تست پایش بلادرنگ و سریع همه سایت‌ها (/api/admin/monitors/check-all)
  console.log("\n--- 9. تست پایش فوری و اندازه‌گیری تاخیر سامانه‌ها ---");
  try {
    const res = await fetch(`${BASE_URL}/api/admin/monitors/check-all`, {
      method: "POST",
      headers: { Authorization: AUTH_HEADER }
    });
    const data = await res.json();
    assert(res.status === 200 && data.ok === true, "بررسی فوری همه سایت‌ها با موفقیت اجرا شد.");
    assert(data.count > 0, `تعداد ${data.count} سامانه با اندازه‌گیری تاخیر میلی‌ثانیه‌ای پایش شدند.`);
  } catch (e) {
    assert(false, "خطا در پایش سامانه‌ها: " + e.message);
  }

  // 10. تست پشتیبان‌گیری کامل از پایگاه داده (/api/admin/backup/export)
  console.log("\n--- 10. تست دانلود فایل پشتیبان کامل دیتابیس (JSON Dump) ---");
  try {
    const res = await fetch(`${BASE_URL}/api/admin/backup/export`, {
      headers: { Authorization: AUTH_HEADER }
    });
    assert(res.status === 200, "اندپوینت پشتیبان‌گیری با کد ۲۰۰ پاسخ داد.");
    const contentType = res.headers.get("content-type") || "";
    assert(contentType.includes("application/json"), "خروجی با فرمت application/json ارسال شد.");
    const backupData = await res.json();
    assert(backupData.software === "کافی نت لیمو", "نام سامانه در فایل پشتیبان معتبر است.");
    assert(backupData.tables && Array.isArray(backupData.tables.users), "جدول کاربران در پشتیبان وجود دارد.");
    assert(Array.isArray(backupData.tables.orders), "جدول سفارشات در پشتیبان وجود دارد.");
    assert(Array.isArray(backupData.tables.service_items), "جدول خدمات در پشتیبان وجود دارد.");
  } catch (e) {
    assert(false, "خطا در پشتیبان‌گیری: " + e.message);
  }

  console.log(`\n==================================================`);
  console.log(`نتایج نهایی آزمون: ${passed} آزمون موفق، ${failed} آزمون ناموفق`);
  console.log(`==================================================\n`);

  if (failed > 0) {
    process.exit(1);
  }
}

runTests();
