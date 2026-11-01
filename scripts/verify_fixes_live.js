/**
 * اسکریپت آزمون جامع و زنده کلودفلر برای تایید ۳ درخواست کاربر
 * ۱. حذف تصویر لگو از /start و پیام متنی تمیز
 * ۲. فعال و سالم بودن تمامی دکمه‌های فهرست خدمات و جزییات سرویس‌ها
 * ۳. امنیت پنل ادمین (نام کاربری + رمز عبور) و حذف درج خودکار ناامن
 */

const BASE_URL = 'https://limo-cafe-bot.bakhtar-visasup.workers.dev';

async function runTests() {
  console.log('🚀 شروع آزمون‌های زنده روی ورکر کلودفلر: ' + BASE_URL + '\n');
  let passed = 0;
  let failed = 0;

  function assert(condition, testName, detail = '') {
    if (condition) {
      console.log(`✅ [PASS] ${testName}`);
      passed++;
    } else {
      console.error(`❌ [FAIL] ${testName} ${detail ? '-> ' + detail : ''}`);
      failed++;
    }
  }

  // ۱. تست دستور /start بدون تصویر
  try {
    const res = await fetch(`${BASE_URL}/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        update_id: 900001,
        message: {
          message_id: 101,
          from: { id: 987654321, first_name: 'کاربر تست', username: 'testuser' },
          chat: { id: 987654321, type: 'private' },
          text: '/start'
        }
      })
    });
    const reply = await res.json();
    assert(reply.method === 'sendMessage', '۱. دستور /start به صورت sendMessage (متن خالص بدون sendPhoto) ارسال می‌شود');
    assert(!reply.photo, '۱.۱ فیلد عکس (photo) به طور کامل از پاسخ /start حذف شده است');
    assert(reply.text && reply.text.includes('کافی نت لیمو'), '۱.۲ متن پیام خوش‌آمدگویی حاوی عنوان کافی‌نت لیمو است');
    assert(reply.reply_markup && reply.reply_markup.inline_keyboard && reply.reply_markup.inline_keyboard.length >= 4, '۱.۳ دکمه‌های شیشه‌ای منوی اصلی به صورت کامل وجود دارند');
  } catch(e) {
    assert(false, '۱. تست دستور /start', e.message);
  }

  // ۲. تست دکمه فهرست خدمات (services_list)
  try {
    const res = await fetch(`${BASE_URL}/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        update_id: 900002,
        callback_query: {
          id: 'cb_test_001',
          from: { id: 987654321, first_name: 'کاربر تست' },
          message: { message_id: 101, chat: { id: 987654321, type: 'private' }, text: 'منو' },
          data: 'services_list'
        }
      })
    });
    const reply = await res.json();
    assert(reply.method === 'editMessageText', '۲. پاسخ به دکمه فهرست خدمات از نوع editMessageText است');
    assert(reply.text && reply.text.includes('دسته‌بندی خدمات'), '۲.۱ متن فهرست خدمات به درستی نمایش داده شد');
    const flatButtons = (reply.reply_markup?.inline_keyboard || []).flat();
    const callbacks = flatButtons.map(b => b.callback_data);
    assert(callbacks.includes('cat_ALIEN_AND_CODES'), '۲.۲ دکمه امور اتباع و کدها موجود است');
    assert(callbacks.includes('cat_UNIVERSITY_SERVICES'), '۲.۳ دکمه خدمات دانشگاهی و آزمون‌ها موجود است');
    assert(callbacks.includes('cat_TICKETS_TRAVEL'), '۲.۴ دکمه بلیت سفر موجود است');
    assert(callbacks.includes('cat_GOVERNMENT_INTERNET'), '۲.۵ دکمه خدمات دولتی و اینترنتی موجود است');
  } catch(e) {
    assert(false, '۲. تست دکمه فهرست خدمات', e.message);
  }

  // ۳. تست کلیک روی دسته‌بندی دانشگاهی (cat_UNIVERSITY_SERVICES)
  try {
    const res = await fetch(`${BASE_URL}/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        update_id: 900003,
        callback_query: {
          id: 'cb_test_002',
          from: { id: 987654321 },
          message: { message_id: 101, chat: { id: 987654321 }, text: 'دسته‌ها' },
          data: 'cat_UNIVERSITY_SERVICES'
        }
      })
    });
    const reply = await res.json();
    assert(reply.method === 'editMessageText', '۳. پیمایش به دسته خدمات دانشگاهی پاسخ درجا می‌دهد');
    const flatButtons = (reply.reply_markup?.inline_keyboard || []).flat();
    const svcCallbacks = flatButtons.map(b => b.callback_data);
    assert(svcCallbacks.includes('svc_SANJESH_REGISTRATION'), '۳.۱ آزمون سازمان سنجش در دسته دانشگاهی قرار دارد');
    assert(svcCallbacks.includes('svc_PNU_SERVICES'), '۳.۲ سامانه گلستان پیام نور در دسته دانشگاهی قرار دارد');
    assert(svcCallbacks.includes('svc_IAU_SERVICES'), '۳.۳ سامانه آموزشیار دانشگاه آزاد در دسته دانشگاهی قرار دارد');
    assert(svcCallbacks.includes('svc_EMT_VERIFICATION'), '۳.۴ تاییدیه تحصیلی در دسته دانشگاهی قرار دارد');
  } catch(e) {
    assert(false, '۳. تست دسته خدمات دانشگاهی', e.message);
  }

  // ۴. تست کلیک روی دسته‌بندی امور اتباع (cat_ALIEN_AND_CODES)
  try {
    const res = await fetch(`${BASE_URL}/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        update_id: 900004,
        callback_query: {
          id: 'cb_test_003',
          from: { id: 987654321 },
          message: { message_id: 101, chat: { id: 987654321 }, text: 'دسته‌ها' },
          data: 'cat_ALIEN_AND_CODES'
        }
      })
    });
    const reply = await res.json();
    const flatButtons = (reply.reply_markup?.inline_keyboard || []).flat();
    const svcCallbacks = flatButtons.map(b => b.callback_data);
    assert(svcCallbacks.includes('svc_HOUSING_TRACKING_CODE'), '۴.۱ کد رهگیری مسکن در دسته اتباع و کدها موجود است');
    assert(svcCallbacks.includes('svc_FIDA_CODE'), '۴.۲ کد فیدا در دسته اتباع موجود است');
    assert(svcCallbacks.includes('svc_IVSF_APPOINTMENT'), '۴.۳ نوبت تثبیت هویت در دسته اتباع موجود است');
  } catch(e) {
    assert(false, '۴. تست دسته امور اتباع', e.message);
  }

  // ۵. تست نمایش جزییات یک خدمت با تعرفه و دکمه‌های سالم (svc_SANJESH_REGISTRATION)
  try {
    const res = await fetch(`${BASE_URL}/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        update_id: 900005,
        callback_query: {
          id: 'cb_test_004',
          from: { id: 987654321 },
          message: { message_id: 101, chat: { id: 987654321 }, text: 'خدمت' },
          data: 'svc_SANJESH_REGISTRATION'
        }
      })
    });
    const reply = await res.json();
    assert(reply.method === 'editMessageText', '۵. پاسخ به دکمه خدمت سنجش موفق است');
    assert(reply.text.includes('ثبت‌نام آزمون‌های سازمان سنجش'), '۵.۱ عنوان خدمت در پیام درج شده است');
    assert(reply.text.includes('تعرفه خدمت:') && reply.text.includes('تومان'), '۵.۲ تعرفه مصوب خدمت به تومان قید شده است');
    const flatButtons = (reply.reply_markup?.inline_keyboard || []).flat();
    assert(flatButtons.some(b => b.web_app && b.web_app.url.includes('svc=SANJESH_REGISTRATION')), '۵.۳ دکمه ثبت مستقیم در مینی‌اپلیکیشن فعال است');
    assert(flatButtons.some(b => b.callback_data === 'contact_operator'), '۵.۴ دکمه هماهنگی با اپراتور فعال است');
    assert(flatButtons.some(b => b.callback_data === 'services_list'), '۵.۵ دکمه بازگشت به فهرست خدمات فعال است');
  } catch(e) {
    assert(false, '۵. تست جزییات خدمت سنجش', e.message);
  }

  // ۶. تست امنیتی صفحه ورود داشبورد مدیریت (/admin)
  try {
    const res = await fetch(`${BASE_URL}/admin`);
    const html = await res.text();
    assert(res.status === 200, '۶. صفحه /admin با موفقیت لود می‌شود');
    assert(html.includes('adminUsernameInput') && html.includes('نام کاربری مدیریت'), '۶.۱ فیلد نام کاربری مدیریت در فرم ورود تعبیه شده است');
    assert(html.includes('adminPasswordInput') && html.includes('رمز عبور مدیریت'), '۶.۲ فیلد رمز عبور مدیریت در فرم ورود تعبیه شده است');
    assert(!html.includes('درج خودکار و ورود'), '۶.۳ دکمه ناامن «درج خودکار و ورود» به طور کامل حذف شده است');
    assert(!html.includes('select-all">limo_admin_2026<'), '۶.۴ رمز عبور آشکار (Plaintext) از ظاهر صفحه حذف شده است');
  } catch(e) {
    assert(false, '۶. تست ظاهر امنیتی صفحه /admin', e.message);
  }

  // ۷. تست رد احراز هویت با نام کاربری یا رمز اشتباه
  try {
    const wrongAuth = 'Basic ' + Buffer.from('admin:wrongpass').toString('base64');
    const res = await fetch(`${BASE_URL}/api/admin/data`, {
      headers: { 'Authorization': wrongAuth }
    });
    assert(res.status === 401, '۷. ورود با رمز عبور اشتباه مسدود شد (HTTP 401 Unauthorized)');
  } catch(e) {
    assert(false, '۷. تست پسورد اشتباه', e.message);
  }

  try {
    const wrongUser = 'Basic ' + Buffer.from('intruder:limo_admin_2026').toString('base64');
    const res = await fetch(`${BASE_URL}/api/admin/data`, {
      headers: { 'Authorization': wrongUser }
    });
    assert(res.status === 401, '۷.۱ ورود با نام کاربری ناشناس مسدود شد (HTTP 401 Unauthorized)');
  } catch(e) {
    assert(false, '۷.۱ تست یوزر اشتباه', e.message);
  }

  // ۸. تست موفقیت احراز هویت با نام کاربری و رمز عبور صحیح (Basic Auth)
  try {
    const validBasic = 'Basic ' + Buffer.from('admin:limo_admin_2026').toString('base64');
    const res = await fetch(`${BASE_URL}/api/admin/data`, {
      headers: { 'Authorization': validBasic }
    });
    const data = await res.json();
    assert(res.status === 200 && data.ok === true, '۸. ورود موفق با نام کاربری admin و رمز عبور صحیح');
    assert(data.stats && typeof data.stats.total_orders === 'number', '۸.۱ داده‌های آماری داشبورد با موفقیت دریافت شد');
    assert(Array.isArray(data.orders), '۸.۲ لیست سفارش‌ها برای ادمین معتبر بارگذاری شد');
  } catch(e) {
    assert(false, '۸. تست لاگین معتبر با نام کاربری و رمز', e.message);
  }

  // ۹. تست موفقیت احراز هویت با هدرهای اختصاصی (x-admin-username + x-admin-key)
  try {
    const res = await fetch(`${BASE_URL}/api/admin/data`, {
      headers: {
        'x-admin-username': 'admin',
        'x-admin-key': 'limo_admin_2026'
      }
    });
    const data = await res.json();
    assert(res.status === 200 && data.ok === true, '۹. ورود موفق با هدرهای استاندارد دوگانه (x-admin-username و x-admin-key)');
  } catch(e) {
    assert(false, '۹. تست هدرهای دوگانه', e.message);
  }

  // ۱۰. تست دریافت کاتالوگ خدمات عمومی برای مینی‌اپلیکیشن
  try {
    const res = await fetch(`${BASE_URL}/api/catalog/services`);
    const data = await res.json();
    assert(res.status === 200 && data.ok === true, '۱۰. وب‌سرویس عمومی کاتالوگ مینی‌اپ پاسخ صحیح داد');
    assert(Array.isArray(data.categories) && data.categories.length >= 6, '۱۰.۱ دسته‌بندی‌ها به طور کامل بارگذاری شدند');
    assert(Array.isArray(data.services) && data.services.length >= 10, '۱۰.۲ فهرست خدمات با دسته‌بندی متناسب در دسترس است');
  } catch(e) {
    assert(false, '۱۰. تست کاتالوگ مینی‌اپ', e.message);
  }

  console.log(`\n========================================`);
  console.log(`🏁 نتیجه کل آزمون‌های زنده: ${passed} آزمون موفق، ${failed} آزمون ناموفق`);
  console.log(`========================================`);
  process.exit(failed === 0 ? 0 : 1);
}

runTests();
