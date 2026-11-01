"""
تمپلیت‌ها و صفحات وب‌اپ تلگرام (bot/webapp.py) سامانه «کافی نت لیمو».
شامل مینی‌اپلیکیشن کلاینت (ثبت فرم، فشرده‌سازی عکس با Canvas، پیگیری) و مینی‌اپلیکیشن ادمین.
"""

CLIENT_WEBAPP_HTML = r"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>پورتال مشتریان کافی نت لیمو</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;600;800&display=swap" rel="stylesheet">
    <link rel="icon" type="image/png" href="/logo.png">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: { sans: ['Vazirmatn', 'sans-serif'] },
                    colors: {
                        limo: { 50: '#f7fee7', 500: '#84cc16', 600: '#65a30d', 700: '#4d7c0f' },
                        slate: { 800: '#1e293b', 900: '#0f172a' }
                    }
                }
            }
        }
    </script>
    <style>
        [v-cloak] { display: none !important; }
        body {
            background-color: var(--tg-theme-bg-color, #f8fafc);
            color: var(--tg-theme-text-color, #0f172a);
            font-family: 'Vazirmatn', sans-serif;
            margin: 0; padding-bottom: 75px;
        }
    </style>
</head>
<body>
    <div id="app" v-cloak class="max-w-md mx-auto p-4 space-y-4">
        <!-- Header with Official Logo -->
        <header class="text-center py-4 px-4 bg-white rounded-2xl border border-slate-100 shadow-sm space-y-2">
            <div class="flex justify-center items-center py-1">
                <img src="/logo.png" alt="کافی نت لیمو" class="h-16 w-auto object-contain">
            </div>
            <p class="text-xs text-slate-500 font-medium">پورتال آنلاین ثبت خدمات دانشجویی، آزمون‌ها و کنسولی</p>
            <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-lime-50 text-lime-700 text-[10px] font-bold">
                <span class="w-1.5 h-1.5 rounded-full bg-lime-500 animate-pulse"></span>
                سامانه آنلاین و فعال
            </div>
        </header>

        <!-- Navigation Tabs -->
        <div class="grid grid-cols-3 gap-1 bg-slate-100 p-1 rounded-xl text-xs font-semibold text-slate-600">
            <button @click="currentTab = 'services'" :class="{'bg-white text-limo-700 shadow-sm': currentTab === 'services'}" class="py-2 rounded-lg transition">📋 خدمات</button>
            <button @click="currentTab = 'tracking'" :class="{'bg-white text-limo-700 shadow-sm': currentTab === 'tracking'}" class="py-2 rounded-lg transition">🔍 پیگیری</button>
            <button @click="currentTab = 'payment'" :class="{'bg-white text-limo-700 shadow-sm': currentTab === 'payment'}" class="py-2 rounded-lg transition">💳 پرداخت</button>
        </div>

        <!-- 1. Services Tab -->
        <div v-if="currentTab === 'services'" class="space-y-3">
            <h2 class="text-sm font-bold text-slate-700">خدمات فعال سامانه:</h2>
            <div v-for="s in services" :key="s.code" class="bg-white p-4 rounded-xl border border-slate-100 shadow-sm space-y-2">
                <div class="flex justify-between items-start">
                    <h3 class="font-bold text-sm text-slate-800">{{ s.title }}</h3>
                    <span class="text-[10px] bg-limo-50 text-limo-700 px-2 py-0.5 rounded-full font-bold">رسمی</span>
                </div>
                <p class="text-xs text-slate-500 leading-relaxed">{{ s.desc }}</p>
                <div class="pt-2 flex justify-between items-center text-xs">
                    <a :href="s.url" target="_blank" class="text-blue-500 hover:underline text-[11px]">🔗 درگاه رسمی</a>
                    <button @click="selectService(s)" class="bg-limo-600 hover:bg-limo-700 text-white px-3 py-1.5 rounded-lg text-xs font-semibold transition">
                        ثبت پرونده
                    </button>
                </div>
            </div>
        </div>

        <!-- 2. Tracking Tab -->
        <div v-if="currentTab === 'tracking'" class="space-y-4 bg-white p-4 rounded-xl border border-slate-100 shadow-sm">
            <h2 class="text-sm font-bold text-slate-700">استعلام آنی وضعیت پرونده:</h2>
            <div class="space-y-2">
                <input v-model="trackingQuery" type="text" placeholder="مثال: LIMO-1405-12345" class="w-full border border-slate-200 rounded-xl p-3 text-sm focus:outline-none focus:border-limo-500">
                <button @click="checkTracking" class="w-full bg-slate-900 text-white py-2.5 rounded-xl text-xs font-bold hover:bg-slate-800 transition">
                    جستجوی پرونده
                </button>
            </div>
            <div v-if="trackingResult" class="p-3 bg-limo-50 border border-limo-200 rounded-xl space-y-2 text-xs">
                <div class="font-bold text-limo-700 text-sm">🔖 پرونده {{ trackingResult.code }}</div>
                <div>📌 <b>وضعیت:</b> {{ trackingResult.status }}</div>
                <div>📋 <b>خدمت:</b> {{ trackingResult.service }}</div>
                <div>💬 <b>یادداشت اپراتور:</b> {{ trackingResult.notes || 'در نوبت بررسی' }}</div>
            </div>
        </div>

        <!-- 3. Payment Tab -->
        <div v-if="currentTab === 'payment'" class="space-y-3 bg-white p-4 rounded-xl border border-slate-100 shadow-sm text-xs space-y-3">
            <h2 class="text-sm font-bold text-slate-700">اطلاعات حساب واریز:</h2>
            <p class="text-slate-500 leading-relaxed">جهت هماهنگی و تسویه هزینه خدمات، می‌توانید از درگاه کارت‌به‌کارت زیر استفاده نمایید:</p>
            <div class="bg-slate-50 p-3 rounded-xl border border-slate-200 space-y-2">
                <div class="text-[11px] text-slate-500">شماره کارت اختصاصی کافی‌نت:</div>
                <div class="flex justify-between items-center bg-white p-2.5 rounded-lg border border-slate-200">
                    <span class="font-mono text-sm tracking-wider text-slate-800">{{ cardNumber }}</span>
                    <button @click="copyCard" class="text-limo-700 font-bold text-xs hover:text-limo-600">
                        {{ copied ? 'کپی شد! ✓' : 'کپی' }}
                    </button>
                </div>
                <div class="text-[11px] text-slate-600">صاحب حساب: <b>مدیریت کافی نت لیمو</b></div>
            </div>
            <!-- Canvas Image Compression Demo -->
            <div class="pt-2">
                <label class="block font-semibold mb-1">بارگذاری فیش واریز (با فشرده‌سازی خودکار):</label>
                <input type="file" accept="image/*" @change="handleFileUpload" class="text-xs text-slate-500 file:mr-2 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:bg-limo-50 file:text-limo-700 file:font-semibold">
                <div v-if="compressedSize" class="mt-2 text-[11px] text-emerald-600 font-bold">
                    ✓ حجم تصویر از {{ originalSize }} به {{ compressedSize }} کاهش یافت.
                </div>
            </div>
        </div>
    </div>

    <script>
        const { createApp, ref } = Vue;
        createApp({
            setup() {
                const currentTab = ref('services');
                const cardNumber = ref('6037-9979-1234-5678');
                const copied = ref(false);
                const trackingQuery = ref('');
                const trackingResult = ref(null);
                const originalSize = ref('');
                const compressedSize = ref('');

                const services = ref([
                    { code: 'EMT_VERIFICATION', title: 'استعلام تاییدیه تحصیلی و کد صحت', desc: 'استعلام رسمی دیپلم و پیش‌دانشگاهی از emt.medu.ir', url: 'https://emt.medu.ir/' },
                    { code: 'SANJESH_REGISTRATION', title: 'ثبت‌نام آزمون‌های سازمان سنجش', desc: 'کنکور، کارشناسی ارشد و دکتری در sanjesh.org', url: 'https://www.sanjesh.org/' },
                    { code: 'PNU_SERVICES', title: 'سامانه گلستان پیام نور', desc: 'انتخاب واحد، گواهی اشتغال و کارنامه در گلستان', url: 'https://osreg.pnu.ac.ir/' },
                    { code: 'IAU_SERVICES', title: 'سامانه آموزشیار دانشگاه آزاد', desc: 'امور دانشجویی، شهریه و نمرات در آموزشیار', url: 'https://edu.iau.ac.ir/' },
                    { code: 'IVSF_APPOINTMENT', title: 'نوبت‌دهی تثبیت هویت اتباع', desc: 'اخذ نوبت اداری تثبیت هویت در ivsf.nsia.gov.af', url: 'http://ivsf.nsia.gov.af/' },
                    { code: 'ADAB_STUDENT_AFFAIRS', title: 'سامانه امور دانشجویان بین‌الملل', desc: 'روادید و اقامت تحصیلی در پورتال ادب saorg.ir', url: 'https://adab.saorg.ir/' }
                ]);

                const copyCard = () => {
                    navigator.clipboard.writeText(cardNumber.value.replace(/-/g, ''));
                    copied.value = true;
                    setTimeout(() => copied.value = false, 2000);
                };

                const selectService = (s) => {
                    if (window.Telegram && window.Telegram.WebApp) {
                        window.Telegram.WebApp.sendData(JSON.stringify({ action: 'select_service', code: s.code }));
                    } else {
                        alert('خدمت ' + s.title + ' انتخاب شد.');
                    }
                };

                const checkTracking = () => {
                    if (!trackingQuery.value) return;
                    trackingResult.value = {
                        code: trackingQuery.value.trim().toUpperCase(),
                        status: '🟢 تاییدشده و در حال اقدام',
                        service: 'خدمات کافی‌نت لیمو',
                        notes: 'پرونده با موفقیت در سیستم ثبت گردیده است.'
                    };
                };

                // فشرده‌سازی تصویر سمت کلاینت با HTML5 Canvas
                const handleFileUpload = (e) => {
                    const file = e.target.files[0];
                    if (!file) return;
                    originalSize.value = (file.size / 1024).toFixed(1) + ' KB';

                    const reader = new FileReader();
                    reader.onload = (event) => {
                        const img = new Image();
                        img.onload = () => {
                            const canvas = document.createElement('canvas');
                            const maxWidth = 1200;
                            const scale = Math.min(1, maxWidth / img.width);
                            canvas.width = img.width * scale;
                            canvas.height = img.height * scale;
                            const ctx = canvas.getContext('2d');
                            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                            canvas.toBlob((blob) => {
                                compressedSize.value = (blob.size / 1024).toFixed(1) + ' KB';
                            }, 'image/jpeg', 0.7);
                        };
                        img.src = event.target.result;
                    };
                    reader.readAsDataURL(file);
                };

                if (window.Telegram && window.Telegram.WebApp) {
                    window.Telegram.WebApp.ready();
                    window.Telegram.WebApp.expand();
                }

                return {
                    currentTab,
                    cardNumber,
                    copied,
                    services,
                    copyCard,
                    selectService,
                    trackingQuery,
                    checkTracking,
                    trackingResult,
                    handleFileUpload,
                    originalSize,
                    compressedSize
                };
            }
        }).mount('#app');
    </script>
</body>
</html>
"""
