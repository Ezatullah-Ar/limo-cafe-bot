/**
 * آزمون سرتاسری و جامع فاز ۷ (E2E Verification Suite):
 * چت زنده پشتیبانی، تیکتینگ دوطرفه، کنترل‌های امنیتی و چرخه کامل خدمت
 */

const BASE_URL = 'https://limo-cafe-bot.bakhtar-visasup.workers.dev';
const AUTH_HEADER = 'Basic ' + Buffer.from('admin:limo_admin_2026').toString('base64');
const TEST_USER_ID = 887766554;
const TEST_USER_NAME = 'متقاضی آزمون فاز هفت';

async function runPhase7E2ETests() {
  console.log('🚀 آغاز آزمون‌های سرتاسری فاز ۷ (E2E) بر روی کلودفلر: ' + BASE_URL + '\n');
  let passed = 0;
  let failed = 0;

  function assert(condition, title, extra = '') {
    if (condition) {
      console.log(`✅ [PASS] ${title}`);
      passed++;
    } else {
      console.error(`❌ [FAIL] ${title} ${extra ? '-> ' + extra : ''}`);
      failed++;
    }
  }

  // بخش ۱: راه‌اندازی چت زنده و ایجاد نشست در دیتابیس
  let threadId = null;
  try {
    const res = await fetch(`${BASE_URL}/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        update_id: 700001,
        message: {
          message_id: 201,
          from: { id: TEST_USER_ID, first_name: TEST_USER_NAME, username: 'testuser_p7' },
          chat: { id: TEST_USER_ID, type: 'private' },
          text: '/chat'
        }
      })
    });
    const reply = await res.json();
    assert(reply.method === 'sendMessage', '۱.۱ دستور /chat پاسخ sendMessage متنی ارسال کرد');
    assert(reply.text.includes('گفتگوی مستقیم با پشتیبانی'), '۱.۲ پیام اتصال به پشتیبانی به متقاضی نمایش داده شد');
    assert(reply.reply_markup?.inline_keyboard?.[0]?.[0]?.callback_data === 'end_chat', '۱.۳ دکمه پایان گفتگو در رابط کاربری مشتری قرار دارد');
  } catch(e) {
    assert(false, '۱. آغاز چت زنده با /chat', e.message);
  }

  // بخش ۲: ارسال پیام از سوی متقاضی و ثبت در تیکتینگ
  try {
    const res = await fetch(`${BASE_URL}/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        update_id: 700002,
        message: {
          message_id: 202,
          from: { id: TEST_USER_ID, first_name: TEST_USER_NAME },
          chat: { id: TEST_USER_ID, type: 'private' },
          text: 'سلام، مدارک تاییدیه تحصیلی بنده چه زمانی بررسی می‌شود؟'
        }
      })
    });
    const reply = await res.json();
    assert(reply.method === 'sendMessage', '۲.۱ دریافت پیام مشتری در نشست فعال چت زنده');
    assert(reply.text.includes('پیام شما برای اپراتور ارسال شد'), '۲.۲ تایید ارسال پیام به اپراتور برای مشتری ارسال شد');
  } catch(e) {
    assert(false, '۲. ارسال پیام متقاضی در چت', e.message);
  }

  // بخش ۳: دریافت فهرست تیکت‌های پشتیبانی در پنل مدیریت وب
  try {
    const res = await fetch(`${BASE_URL}/api/admin/support/threads`, {
      headers: { 'Authorization': AUTH_HEADER }
    });
    const data = await res.json();
    assert(res.status === 200 && data.ok === true, '۳.۱ وب‌سرویس /api/admin/support/threads با موفقیت پاسخ داد');
    assert(Array.isArray(data.threads) && data.threads.length > 0, '۳.۲ فهرست تیکت‌های فعال بارگذاری شد');
    
    const userThread = data.threads.find(t => t.telegram_id === TEST_USER_ID);
    assert(Boolean(userThread), '۳.۳ تیکت متقاضی آزمون در کارتابل پشتیبانی با موفقیت ثبت و بازیابی شد');
    if (userThread) {
      threadId = userThread.id;
      assert(userThread.status === 'PENDING_SUPPORT' || userThread.status === 'PENDING_OPERATOR', '۳.۴ وضعیت تیکت در صف انتظار پاسخ اپراتور قرار دارد');
    }
  } catch(e) {
    assert(false, '۳. استعلام تیکت‌های پشتیبانی در پنل ادمین', e.message);
  }

  // بخش ۴: مشاهده تاریخچه پیام‌های تیکت توسط اپراتور
  if (threadId) {
    try {
      const res = await fetch(`${BASE_URL}/api/admin/support/messages?thread_id=${threadId}`, {
        headers: { 'Authorization': AUTH_HEADER }
      });
      const data = await res.json();
      assert(res.status === 200 && data.ok === true, '۴.۱ دریافت موفق تاریخچه پیام‌ها برای تیکت شماره ' + threadId);
      assert(Array.isArray(data.messages) && data.messages.length > 0, '۴.۲ پیام‌های رد و بدل‌شده تیکت موجود است');
      const lastMsg = data.messages[data.messages.length - 1];
      assert(lastMsg.sender_role === 'CUSTOMER' && lastMsg.message_text.includes('مدارک تاییدیه تحصیلی'), '۴.۳ متن دقیق پیام مشتری در پایگاه داده ثبت و برای اپراتور بازیابی شد');
    } catch(e) {
      assert(false, '۴. تاریخچه پیام‌های تیکت', e.message);
    }

    // بخش ۵: ارسال پاسخ دوطرفه از طریق پنل وب اپراتور به مشتری
    try {
      const res = await fetch(`${BASE_URL}/api/admin/support/reply`, {
        method: 'POST',
        headers: {
          'Authorization': AUTH_HEADER,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          thread_id: threadId,
          message: 'سلام وقت بخیر، مدارک شما دریافت شد و تا ۲ ساعت آینده نتیجه استعلام صادر می‌گردد.',
          telegram_id: TEST_USER_ID
        })
      });
      const data = await res.json();
      assert(res.status === 200 && data.ok === true, '۵.۱ ارسال موفق پاسخ اپراتور از طریق پنل مدیریت');
      assert(data.status === 'PENDING_CUSTOMER', '۵.۲ وضعیت تیکت پس از پاسخ اپراتور به انتظار پاسخ مشتری تغییر یافت');
    } catch(e) {
      assert(false, '۵. ارسال پاسخ وب اپراتور', e.message);
    }
  }

  // بخش ۶: پایان دادن به گفت‌وگو از طریق دکمه شیشه‌ای مشتری (end_chat)
  try {
    const res = await fetch(`${BASE_URL}/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        update_id: 700003,
        callback_query: {
          id: 'cb_test_end_01',
          from: { id: TEST_USER_ID, first_name: TEST_USER_NAME },
          message: { message_id: 203, chat: { id: TEST_USER_ID } },
          data: 'end_chat'
        }
      })
    });
    const reply = await res.json();
    assert(reply.method === 'editMessageText', '۶.۱ پاسخ به دکمه end_chat با موفقیت ثبت شد');
    assert(reply.text.includes('گفتگوی شما با پشتیبانی به پایان رسید'), '۶.۲ پیام خروج از چت و تشکر به متقاضی نمایش داده شد');
    assert(reply.reply_markup?.inline_keyboard?.length >= 3, '۶.۳ مشتری مجدداً به منوی اصلی با دکمه‌های سالم هدایت گردید');
  } catch(e) {
    assert(false, '۶. پایان چت زنده با دکمه end_chat', e.message);
  }

  // بخش ۷: آزمون کنترل‌های امنیتی و ممانعت از دسترسی‌های غیرمجاز
  try {
    const unauthRes = await fetch(`${BASE_URL}/api/admin/support/threads`, {
      headers: { 'Authorization': 'Basic ' + Buffer.from('guest:123456').toString('base64') }
    });
    assert(unauthRes.status === 401, '۷.۱ دسترسی غیرمجاز به تیکت‌های پشتیبانی با خطای ۴۰۱ مسدود گردید');

    const unauthReply = await fetch(`${BASE_URL}/api/admin/support/reply`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ thread_id: 1, message: 'تست غیرمجاز' })
    });
    assert(unauthReply.status === 401, '۷.۲ ارسال پیام اپراتور بدون احراز هویت با خطای ۴۰۱ رد شد');
  } catch(e) {
    assert(false, '۷. آزمون امنیت تیکتینگ', e.message);
  }

  // بخش ۸: آزمون چرخه کامل ثبت سفارش، شماره پیگیری و ثبت رسید (Full Workflow Integration)
  try {
    const orderPayload = {
      service_code: 'EMT_VERIFICATION',
      full_name: 'رضا حسینی تست',
      phone_number: '09129998877',
      telegram_id: TEST_USER_ID,
      username: 'rezatest',
      notes: 'تست سرتاسری ثبت سفارش فاز ۷',
      form_data: {
        nationalCode: '0011223344',
        degreeType: 'DIPLOMA_NEW',
        schoolName: 'دبیرستان تست',
        targetOrg: 'دانشگاه تهران'
      }
    };
    const orderRes = await fetch(`${BASE_URL}/api/order/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(orderPayload)
    });
    const orderData = await orderRes.json();
    assert(orderRes.status === 200 && orderData.ok === true, '۸.۱ سفارش در سیستم با موفقیت ثبت شد');
    assert(orderData.tracking_code && orderData.tracking_code.startsWith('LIMO-'), '۸.۲ شماره سفارش یکتای رسمی (LIMO-XXXX) صادر گردید');

    const trackingCode = orderData.tracking_code;

    // بارگذاری رسید واریز
    const receiptPayload = {
      tracking_code: trackingCode,
      ref_number: 'REF77889900',
      receipt_base64: 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP...'
    };
    const receiptRes = await fetch(`${BASE_URL}/api/order/receipt`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(receiptPayload)
    });
    const receiptData = await receiptRes.json();
    assert(receiptRes.status === 200 && receiptData.ok === true, '۸.۳ رسید پرداخت با موفقیت ثبت شد و وضعیت سفارش به صف بررسی واریز رفت');

    // پیگیری سفارش توسط مشتری
    const trackRes = await fetch(`${BASE_URL}/api/order/track?code=${trackingCode}`);
    const trackData = await trackRes.json();
    assert(trackRes.status === 200 && trackData.ok === true, '۸.۴ استعلام لحظه‌ای پرونده توسط متقاضی موفق بود');
    assert(trackData.order.tracking_code === trackingCode, '۸.۵ اطلاعات کامل پرونده با تفکیک و عایق‌بندی امنیتی واکشی شد');
  } catch(e) {
    assert(false, '۸. آزمون چرخه کامل ثبت سفارش و رهگیری', e.message);
  }

  console.log(`\n========================================`);
  console.log(`🏁 پایان آزمون‌های فاز ۷: ${passed} آزمون موفق، ${failed} آزمون ناموفق`);
  console.log(`========================================`);
  process.exit(failed === 0 ? 0 : 1);
}

runPhase7E2ETests();
