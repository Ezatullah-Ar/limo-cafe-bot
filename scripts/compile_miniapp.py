import json
import os

html_content = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>پورتال مشتریان کافی نت لیمو | Limo Cafe Portal</title>
    
    <!-- Telegram WebApp SDK -->
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    
    <!-- Vue 3 Production Build - Served Locally at Edge with Multi-CDN Resilience -->
    <script src="/vue.global.prod.js"></script>
    <script>
        if (typeof Vue === 'undefined') {
            document.write('<script src="https://cdn.jsdelivr.net/npm/vue@3/dist/vue.global.prod.js"><\\/script>');
        }
    </script>
    <script>
        if (typeof Vue === 'undefined') {
            document.write('<script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"><\/script>');
        }
    </script>
    <script>
        if (typeof Vue === 'undefined') {
            document.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/vue/3.4.21/vue.global.prod.min.js"><\/script>');
        }
    </script>
    <script>
        // جلوگیری قطعی از سفید ماندن صفحه هنگام اختلال شبکه
        setTimeout(function() {
            var el = document.getElementById('app');
            if (el && el.hasAttribute('v-cloak') && typeof Vue === 'undefined') {
                el.removeAttribute('v-cloak');
                el.innerHTML = '<div style="padding:2.5rem 1.5rem;text-align:center;font-family:sans-serif;direction:rtl;">' +
                    '<div style="font-size:3rem;margin-bottom:1rem;">📶</div>' +
                    '<h2 style="font-size:1.15rem;font-weight:900;color:#0f172a;">در حال اتصال به سرور لیمو...</h2>' +
                    '<p style="margin-top:0.6rem;font-size:0.85rem;color:#64748b;line-height:1.6;">در صورت کندی پروکسی یا فیلترشکن، اتصال اندکی زمان‌بر است. لطفاً چند لحظه شکیبا باشید یا صفحه را تازه‌سازی فرمایید.</p>' +
                    '<button onclick="location.reload()" style="margin-top:1.2rem;padding:0.6rem 1.8rem;background:linear-gradient(to right,#84cc16,#65a30d);color:#0f172a;border:none;border-radius:1rem;font-weight:900;cursor:pointer;box-shadow:0 4px 12px rgba(132,204,22,0.3);">تلاش مجدد 🔄</button>' +
                    '</div>';
            }
        }, 5000);
    </script>
    
    <!-- Preconnect & Persian Font Stack -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800;900&display=swap" media="print" onload="this.media='all'">
    <noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800;900&display=swap"></noscript>
    <link rel="icon" type="image/png" href="/logo.png">

    <!-- Tailwind CSS (Play CDN with custom config) -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Vazirmatn', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'IranSans', 'Tahoma', 'sans-serif'],
                        persian: ['Vazirmatn', 'IranSans', 'Tahoma', 'sans-serif']
                    },
                    colors: {
                        limo: {
                            50: '#f7fee7',
                            100: '#ecfccb',
                            200: '#d9f99d',
                            300: '#bef264',
                            400: '#a3e635',
                            500: '#84cc16',
                            600: '#65a30d',
                            700: '#4d7c0f',
                            800: '#3f6212',
                            900: '#365314'
                        },
                        eitaa: '#ea580c',
                        rubika: '#7e22ce',
                        bale: '#0f766e',
                        tgblue: '#0284c7'
                    },
                    boxShadow: {
                        'soft': '0 4px 20px -2px rgba(15, 23, 42, 0.05)',
                        'hover': '0 10px 25px -3px rgba(15, 23, 42, 0.08)',
                        'nav': '0 -4px 20px rgba(0, 0, 0, 0.06)'
                    }
                }
            }
        }
    </script>

    <!-- GPU-Accelerated Micro-Motion Graphics & Refined Styles -->
    <style>
        [v-cloak] { display: none !important; }
        
        body {
            background-color: #f8fafc;
            color: #0f172a;
            font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'IranSans', Tahoma, sans-serif;
            margin: 0;
            padding-bottom: calc(90px + env(safe-area-inset-bottom, 0px));
            -webkit-tap-highlight-color: transparent;
        }

        .glass-header {
            background: rgba(255, 255, 255, 0.94);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
        }

        .chat-scroll::-webkit-scrollbar { width: 4px; }
        .chat-scroll::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }

        /* موشن‌گرافیک فوق‌سبک سخت‌افزاری */
        @keyframes limoFloat {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-4px) rotate(1.5deg); }
        }
        @keyframes limoPulseGlow {
            0%, 100% { transform: scale(1); opacity: 0.9; }
            50% { transform: scale(1.08); opacity: 1; }
        }
        @keyframes shimmerSlow {
            0% { transform: translateX(100%); }
            100% { transform: translateX(-100%); }
        }
        @keyframes cardPop {
            0% { opacity: 0; transform: translateY(6px); }
            100% { opacity: 1; transform: translateY(0); }
        }

        .limo-motion-float {
            animation: limoFloat 4s ease-in-out infinite;
            will-change: transform;
        }
        .limo-motion-pulse {
            animation: limoPulseGlow 2.5s ease-in-out infinite;
            will-change: transform, opacity;
        }
        .limo-motion-pop {
            animation: cardPop 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
        .shimmer-effect {
            position: relative;
            overflow: hidden;
        }
        .shimmer-effect::after {
            content: '';
            position: absolute;
            top: 0; right: 0; bottom: 0; left: 0;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
            animation: shimmerSlow 3.5s infinite;
        }

        /* در صورت غیرفعال بودن موشن‌گرافیک از پنل ادمین */
        .motion-disabled .limo-motion-float,
        .motion-disabled .limo-motion-pulse,
        .motion-disabled .limo-motion-pop,
        .motion-disabled .shimmer-effect::after {
            animation: none !important;
            transform: none !important;
        }

        .no-scrollbar::-webkit-scrollbar { display: none; }
        .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }

        /* استایل‌های پایه ضد انسداد شبکه جهت تضمین نمایش حتی در صورت لود نشدن CDN خارجی */
        .flex { display: flex; }
        .flex-col { flex-direction: column; }
        .items-center { align-items: center; }
        .justify-between { justify-content: space-between; }
        .justify-center { justify-content: center; }
        .gap-1 { gap: 0.25rem; }
        .gap-1\.5 { gap: 0.375rem; }
        .gap-2 { gap: 0.5rem; }
        .gap-2\.5 { gap: 0.625rem; }
        .gap-3 { gap: 0.75rem; }
        .gap-4 { gap: 1rem; }
        .grid { display: grid; }
        .grid-cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .grid-cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
        .w-full { width: 100%; }
        .max-w-md { max-width: 28rem; }
        .mx-auto { margin-left: auto; margin-right: auto; }
        .min-h-screen { min-height: 100vh; }
        .relative { position: relative; }
        .sticky { position: sticky; }
        .top-0 { top: 0; }
        .z-30 { z-index: 30; }
        .rounded-xl { border-radius: 0.75rem; }
        .rounded-2xl { border-radius: 1rem; }
        .rounded-3xl { border-radius: 1.5rem; }
        .rounded-full { border-radius: 9999px; }
        .bg-white { background-color: #ffffff; }
        .bg-slate-50 { background-color: #f8fafc; }
        .bg-slate-100 { background-color: #f1f5f9; }
        .bg-slate-900 { background-color: #0f172a; }
        .text-white { color: #ffffff; }
        .text-slate-900 { color: #0f172a; }
        .text-slate-700 { color: #334155; }
        .text-slate-600 { color: #475569; }
        .text-slate-500 { color: #64748b; }
        .text-slate-400 { color: #94a3b8; }
        .border { border-width: 1px; border-style: solid; }
        .border-slate-100 { border-color: #f1f5f9; }
        .border-slate-200 { border-color: #e2e8f0; }
        .p-2 { padding: 0.5rem; }
        .p-3 { padding: 0.75rem; }
        .p-3\.5 { padding: 0.875rem; }
        .p-4 { padding: 1rem; }
        .p-5 { padding: 1.25rem; }
        .py-2 { padding-top: 0.5rem; padding-bottom: 0.5rem; }
        .py-2\.5 { padding-top: 0.625rem; padding-bottom: 0.625rem; }
        .py-3 { padding-top: 0.75rem; padding-bottom: 0.75rem; }
        .px-3 { padding-left: 0.75rem; padding-right: 0.75rem; }
        .px-4 { padding-left: 1rem; padding-right: 1rem; }
        .text-xs { font-size: 0.75rem; line-height: 1rem; }
        .text-sm { font-size: 0.875rem; line-height: 1.25rem; }
        .font-bold { font-weight: 700; }
        .font-black { font-weight: 900; }
        .cursor-pointer { cursor: pointer; }
        .transition { transition-property: all; transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); transition-duration: 150ms; }
        .shadow-soft { box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05); }

    </style>
</head>
<body class="antialiased select-none">
    <div id="app" v-cloak :class="{'motion-disabled': motionGraphicsEnabled === '0'}" class="max-w-md mx-auto min-h-screen relative flex flex-col justify-between">
        
        <!-- ======================================================== -->
        <!-- ۱. هدر مینی‌اپلیکیشن با وضعیت آنلاین، دکمه درباره ما و برند -->
        <!-- ======================================================== -->
        <header class="sticky top-0 z-30 glass-header px-4 py-3 border-b border-slate-100 flex items-center justify-between shadow-sm">
            <div class="flex items-center gap-2.5 cursor-pointer" @click="currentTab = 'home'">
                <div class="relative w-9 h-9 rounded-xl overflow-hidden bg-slate-100 flex items-center justify-center border border-slate-200/60 shadow-sm">
                    <!-- موشن‌گرافیک فوق‌سبک سخت‌افزاری لوگو با پوستر ۲.۸ کیلوبایتی -->
                    <video v-if="motionGraphicsEnabled !== '0'" autoplay loop muted playsinline poster="/motion-logo-poster.webp" class="w-full h-full object-cover">
                        <source src="/motion-logo.mp4" type="video/mp4">
                        <img src="/motion-logo-poster.webp" alt="کافی نت لیمو" class="w-full h-full object-cover">
                    </video>
                    <img v-else src="/motion-logo-poster.webp" alt="کافی نت لیمو" class="w-full h-full object-cover">
                    <span v-if="shopIsOpen" class="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-emerald-500 rounded-full border-2 border-white"></span>
                </div>
                <div>
                    <h1 class="text-xs font-black text-slate-900 leading-none">کافی‌نت آنلاین لیمو</h1>
                    <span class="text-[10px] text-slate-400 font-medium mt-0.5 block">پورتال خدمات اینترنتی و دانشجویی</span>
                </div>
            </div>
            
            <div class="flex items-center gap-2">
                <!-- دکمه دسترسی سریع درباره ما -->
                <button @click="currentTab = 'about'" 
                    :class="currentTab === 'about' ? 'bg-limo-500 text-slate-950 font-black' : 'bg-slate-100 text-slate-700 hover:bg-slate-200 font-bold'"
                    class="px-2.5 py-1 rounded-xl text-[10px] transition flex items-center gap-1 shadow-sm">
                    <span>درباره ما</span>
                    <span class="text-[11px]">ℹ️</span>
                </button>

                <!-- نشانگر وضعیت ساعات کاری -->
                <span v-if="shopIsOpen" class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 text-[10px] font-black border border-emerald-100">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-500" :class="{'animate-pulse': motionGraphicsEnabled !== '0'}"></span>
                    فعال
                </span>
                <span v-else class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-amber-50 text-amber-700 text-[10px] font-black border border-amber-100">
                    <span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
                    تعطیل
                </span>
            </div>
        </header>

        <!-- کانتینر اصلی محتوا -->
        <main class="p-4 space-y-4 flex-1">

            <!-- هشدار اختلال شبکه / نمایش کاتالوگ آفلاین -->
            <div v-if="networkError" class="p-3 bg-amber-50 border border-amber-200/80 text-amber-900 text-xs rounded-2xl flex items-center justify-between shadow-soft">
                <div class="flex items-center gap-2">
                    <span class="text-base">⚠️</span>
                    <span class="text-[11px] leading-tight">اتصال اینترنتی با سرور با کندی مواجه شد؛ اطلاعات کاتالوگ آفلاین نمایش داده می‌شوند.</span>
                </div>
                <button @click="loadInitialData(true)" :disabled="isLoadingData" class="px-2.5 py-1 bg-amber-600 hover:bg-amber-700 text-white rounded-xl font-bold text-[11px] transition shadow-sm whitespace-nowrap">
                    {{ isLoadingData ? 'در حال بررسی...' : 'تلاش مجدد 🔄' }}
                </button>
            </div>

            <!-- ======================================================== -->
            <!-- ۲. صفحه اصلی (خانه - Home Tab) -->
            <!-- ======================================================== -->
            <div v-if="currentTab === 'home'" class="space-y-4 limo-motion-pop">
                
                <!-- بنر خوش‌آمدگویی و خلاصه وضعیت کاربر -->
                <div class="relative overflow-hidden bg-gradient-to-l from-slate-900 via-slate-800 to-slate-900 rounded-3xl p-5 text-white shadow-soft shimmer-effect">
                    <div class="absolute -top-12 -left-12 w-32 h-32 bg-limo-500/20 rounded-full blur-2xl"></div>
                    <div class="relative z-10 flex justify-between items-start">
                        <div>
                            <span class="text-[11px] text-slate-300">خوش آمدید،</span>
                            <h2 class="text-base font-black text-white mt-0.5">{{ userFullName }} 👋</h2>
                            <p class="text-[11px] text-slate-400 mt-1">کلیه ثبت‌نام‌ها، آزمون‌ها و خدمات کافی‌نت بدون نیاز به مراجعه حضوری</p>
                        </div>
                        <div class="text-left bg-white/10 backdrop-blur-md px-3 py-2 rounded-2xl border border-white/10">
                            <span class="text-[9px] text-slate-300 block">کیف پول لیمو</span>
                            <span class="text-xs font-black text-limo-300">{{ formatTomans(walletBalance) }}</span>
                        </div>
                    </div>

                    <!-- دسترسی‌های سریع در قالب ۴ دکمه شفاف -->
                    <div class="grid grid-cols-4 gap-2 mt-4 pt-3 border-t border-white/10 text-center">
                        <button @click="currentTab = 'services'" class="p-2 rounded-xl bg-white/5 hover:bg-white/15 transition flex flex-col items-center gap-1">
                            <span class="text-lg">📋</span>
                            <span class="text-[10px] font-bold text-slate-200">ثبت سفارش</span>
                        </button>
                        <button @click="currentTab = 'seasonal'" class="p-2 rounded-xl bg-white/5 hover:bg-white/15 transition flex flex-col items-center gap-1 relative">
                            <span v-if="campaigns.length > 0" class="absolute top-1 right-2 w-2 h-2 rounded-full bg-rose-500" :class="{'animate-ping': motionGraphicsEnabled !== '0'}"></span>
                            <span class="text-lg">⏳</span>
                            <span class="text-[10px] font-bold text-slate-200">ثبت‌نام مقطعی</span>
                        </button>
                        <button @click="currentTab = 'chat'" class="p-2 rounded-xl bg-white/5 hover:bg-white/15 transition flex flex-col items-center gap-1 relative">
                            <span v-if="unreadSupportCount > 0" class="absolute top-1 right-2 w-4 h-4 rounded-full bg-rose-500 text-[9px] font-black flex items-center justify-center">{{ unreadSupportCount }}</span>
                            <span class="text-lg">💬</span>
                            <span class="text-[10px] font-bold text-slate-200">چت پشتیبان</span>
                        </button>
                        <button @click="currentTab = 'profile'" class="p-2 rounded-xl bg-white/5 hover:bg-white/15 transition flex flex-col items-center gap-1">
                            <span class="text-lg">🔍</span>
                            <span class="text-[10px] font-bold text-slate-200">پیگیری کار</span>
                        </button>
                    </div>
                </div>

                <!-- رویدادهای ویژه و ثبت‌نام‌های مقطعی فعال (Seasonal Highlight) -->
                <div v-if="campaigns.length > 0" class="space-y-2.5">
                    <div class="flex justify-between items-center px-1">
                        <h3 class="text-xs font-black text-slate-900 flex items-center gap-1.5">
                            <span class="text-amber-500 text-sm">🔥</span>
                            <span>ثبت‌نام‌های مقطعی و رویدادهای فعال:</span>
                        </h3>
                        <button @click="currentTab = 'seasonal'" class="text-[11px] font-bold text-limo-700 hover:underline">مشاهده همه ({{ campaigns.length }})</button>
                    </div>

                    <div class="space-y-2">
                        <div v-for="c in campaigns.slice(0, 3)" :key="c.id"
                            class="bg-white rounded-2xl p-3.5 border border-amber-200/80 shadow-soft hover:shadow-hover transition flex justify-between items-center">
                            <div class="space-y-1">
                                <div class="flex items-center gap-2">
                                    <span :class="seasonalBadgeClass(c.status)" class="text-[9px] font-bold px-2 py-0.5 rounded-full">
                                        {{ seasonalStatusLabel(c.status) }}
                                    </span>
                                    <h4 class="text-xs font-black text-slate-900">{{ c.title }}</h4>
                                </div>
                                <div class="text-[10px] text-slate-500">
                                    تعرفه: {{ formatTomans(c.base_fee || 50000) }} | مهلت: تا {{ formatDate(c.end_at) }}
                                </div>
                            </div>
                            <button @click="applyForCampaign(c)" class="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold transition shadow-sm">
                                ثبت‌نام
                            </button>
                        </div>
                    </div>
                </div>

                <!-- دسته‌بندی‌های خدمات پرکاربرد -->
                <div class="space-y-2.5">
                    <div class="flex justify-between items-center px-1">
                        <h3 class="text-xs font-black text-slate-900 flex items-center gap-1.5">
                            <span class="text-limo-600 text-sm">⚡</span>
                            <span>دسته‌بندی‌های اصلی خدمات:</span>
                        </h3>
                        <button @click="currentTab = 'services'" class="text-[11px] font-bold text-limo-700 hover:underline">لیست کامل</button>
                    </div>

                    <div class="grid grid-cols-2 gap-2.5">
                        <div v-for="cat in categories.slice(0, 4)" :key="cat.id" @click="selectCategoryAndBrowse(cat.id)"
                            class="bg-white p-3.5 rounded-2xl border border-slate-100 shadow-soft hover:shadow-hover cursor-pointer transition text-right space-y-1.5">
                            <span class="text-lg block">{{ getCategoryIcon(cat.code) }}</span>
                            <h4 class="text-xs font-black text-slate-900">{{ cat.title }}</h4>
                            <p class="text-[10px] text-slate-400 line-clamp-1">{{ cat.description || 'ثبت آنلاین و فوری' }}</p>
                        </div>
                    </div>
                </div>

                <!-- راه‌های ارتباطی و کانال‌های رسمی با رنگ‌های اختصاصی هر برنامه -->
                <div class="space-y-2.5 pt-2">
                    <h3 class="text-xs font-black text-slate-900 px-1 flex items-center gap-1.5">
                        <span class="text-blue-500 text-sm">📞</span>
                        <span>راه‌های ارتباطی و پیام‌رسان‌های کافی‌نت لیمو:</span>
                    </h3>

                    <div class="grid grid-cols-2 gap-2 text-xs font-bold text-white">
                        <!-- ایتا (نارنجی) -->
                        <a href="https://eitaa.com/Cafinet_limo" target="_blank"
                            class="p-3 rounded-2xl bg-gradient-to-r from-orange-500 to-amber-600 shadow-sm hover:opacity-95 transition flex items-center justify-between">
                            <span>پشتیبانی ایتا</span>
                            <span class="text-base">🟠</span>
                        </a>

                        <!-- تلگرام (آبی) -->
                        <a href="https://t.me/LimoCafeBot" target="_blank"
                            class="p-3 rounded-2xl bg-gradient-to-r from-sky-500 to-blue-600 shadow-sm hover:opacity-95 transition flex items-center justify-between">
                            <span>پشتیبانی تلگرام</span>
                            <span class="text-base">🔵</span>
                        </a>

                        <!-- روبیکا (بنفش) -->
                        <a href="https://rubika.ir/cafinet_limo" target="_blank"
                            class="p-3 rounded-2xl bg-gradient-to-r from-purple-600 to-indigo-600 shadow-sm hover:opacity-95 transition flex items-center justify-between">
                            <span>پشتیبانی روبیکا</span>
                            <span class="text-base">🟣</span>
                        </a>

                        <!-- بله (سبز/آبی) -->
                        <a href="https://ble.ir/cafinet_limo" target="_blank"
                            class="p-3 rounded-2xl bg-gradient-to-r from-teal-500 to-emerald-600 shadow-sm hover:opacity-95 transition flex items-center justify-between">
                            <span>پشتیبانی بله</span>
                            <span class="text-base">🟢</span>
                        </a>

                        <!-- تماس تلفنی -->
                        <a href="tel:09364519860"
                            class="col-span-2 p-3 rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-700 shadow-sm hover:opacity-95 transition flex items-center justify-between text-xs font-black">
                            <span>تلفن تماس کافی‌نت: ۰۹۳۶۴۵۱۹۸۶۰</span>
                            <span class="text-base">📞</span>
                        </a>
                    </div>
                </div>

            </div>

            <!-- ======================================================== -->
            <!-- ۳. تب خدمات و فرم سفارش آنلاین (Services Tab) -->
            <!-- ======================================================== -->
            <div v-if="currentTab === 'services'" class="space-y-3 limo-motion-pop">
                <!-- فیلتر دسته‌بندی‌ها -->
                <div class="flex gap-1.5 overflow-x-auto pb-1 no-scrollbar text-xs">
                    <button @click="selectedCategory = 'ALL'"
                        :class="selectedCategory === 'ALL' ? 'bg-slate-900 text-white shadow-sm' : 'bg-white text-slate-600 border border-slate-200'"
                        class="px-3.5 py-1.5 rounded-full font-bold whitespace-nowrap transition">
                        همه خدمات
                    </button>
                    <button v-for="cat in categories" :key="cat.id" @click="selectedCategory = cat.id"
                        :class="selectedCategory === cat.id ? 'bg-slate-900 text-white shadow-sm' : 'bg-white text-slate-600 border border-slate-200'"
                        class="px-3.5 py-1.5 rounded-full font-bold whitespace-nowrap transition">
                        {{ cat.title }}
                    </button>
                </div>

                <!-- کادر جستجو -->
                <div class="relative">
                    <input v-model="serviceSearchQuery" type="text" placeholder="جستجوی عنوان خدمت (سنجش، تثبیت هویت، گلستان...)"
                        class="w-full px-4 py-2.5 pr-9 bg-white border border-slate-200 rounded-2xl text-xs focus:outline-none focus:border-limo-500 shadow-soft">
                    <span class="absolute right-3 top-2.5 text-slate-400 text-sm">🔍</span>
                </div>

                <!-- لیست کارت‌های خدمات (بدون نمایش کدهای داخلی) -->
                <div class="space-y-2.5">
                    <div v-for="s in filteredServicesList" :key="s.id"
                        class="bg-white rounded-3xl p-4 border border-slate-100 shadow-soft hover:shadow-hover transition space-y-2.5">
                        <div class="flex justify-between items-start cursor-pointer" @click="openServiceDetail(s)">
                            <div>
                                <span class="text-[9px] font-bold text-limo-800 bg-limo-100 px-2 py-0.5 rounded-full inline-block mb-1">
                                    {{ s.category || 'خدمت تخصصی' }}
                                </span>
                                <h3 class="text-xs font-black text-slate-900 hover:text-limo-700 transition">{{ s.title }}</h3>
                            </div>
                            <span class="text-xs font-black text-emerald-600">{{ formatTomans(s.base_fee) }}</span>
                        </div>
                        <p class="text-[11px] text-slate-500 leading-relaxed cursor-pointer" @click="openServiceDetail(s)">
                            {{ s.desc || 'انجام کلیه مراحل ثبت‌نام، پیگیری و دریافت مدارک توسط کارشناس کافی‌نت لیمو.' }}
                        </p>
                        
                        <div class="pt-2 border-t border-slate-50 flex items-center justify-between">
                            <span class="text-[10px] text-slate-400 font-medium">⚡ انجام آنلاین و پیگیری لحظه‌ای</span>
                            <div class="flex gap-1.5">
                                <button @click="openServiceDetail(s)"
                                    class="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl text-xs transition flex items-center gap-1">
                                    <span>توضیحات و راهنما</span>
                                    <span>📋</span>
                                </button>
                                <button @click="openServiceDetail(s)"
                                    class="px-3.5 py-1.5 bg-gradient-to-r from-limo-500 to-lime-600 hover:from-limo-400 hover:to-lime-500 text-slate-950 font-black rounded-xl text-xs transition shadow-sm">
                                    انتخاب خدمت
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ======================================================== -->
            <!-- صفحه اختصاصی توضیحات، راهنما و شرایط خدمت (Service Detail) -->
            <!-- ======================================================== -->
            <div v-if="currentTab === 'service_detail'" class="space-y-4 limo-motion-pop">
                <div class="bg-white rounded-3xl p-5 border border-slate-100 shadow-soft space-y-4">
                    <!-- سربرگ خدمت با دکمه بازگشت -->
                    <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                        <div class="space-y-0.5">
                            <span class="text-[10px] text-limo-700 font-bold block">{{ selectedService?.category || 'خدمت آنلاین' }}</span>
                            <h2 class="text-sm font-black text-slate-900">{{ selectedService?.title }}</h2>
                        </div>
                        <button @click="currentTab = 'services'" class="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-xl text-xs font-bold transition">
                            🔙 بازگشت
                        </button>
                    </div>

                    <!-- تصویر یا بنر خدمت (در صورت وجود) -->
                    <div v-if="selectedService?.image_url" class="rounded-2xl overflow-hidden border border-slate-100 max-h-48 flex items-center justify-center bg-slate-50">
                        <img :src="selectedService.image_url" :alt="selectedService.title" class="w-full h-full object-cover">
                    </div>

                    <!-- جعبه تعرفه مصوب خدمت -->
                    <div class="p-3 bg-gradient-to-r from-limo-50 to-lime-50 rounded-2xl border border-limo-200/60 flex justify-between items-center">
                        <div class="space-y-0.5">
                            <span class="text-[10px] text-slate-500 font-medium">تعرفه مصوب کافی‌نت:</span>
                            <div class="text-sm font-black text-slate-900">{{ formatTomans(selectedService?.base_fee) }}</div>
                        </div>
                        <span class="px-2.5 py-1 bg-white/80 rounded-xl text-[10px] font-bold text-limo-800 border border-limo-200">
                            ⚡ ثبت و پیگیری الکترونیکی
                        </span>
                    </div>

                    <!-- توضیحات و راهنمای مراحل انجام کار -->
                    <div class="space-y-2">
                        <h3 class="text-xs font-black text-slate-900 flex items-center gap-1.5">
                            <span>📋</span>
                            <span>توضیحات و شرایط انجام کار:</span>
                        </h3>
                        <div class="text-xs text-slate-600 leading-relaxed bg-slate-50 p-3.5 rounded-2xl border border-slate-100 whitespace-pre-line">
                            {{ selectedService?.guide_content || selectedService?.desc || 'انجام کلیه مراحل ثبت‌نام، پیگیری و دریافت مدارک توسط کارشناس کافی‌نت لیمو.' }}
                        </div>
                    </div>

                    <!-- سامانه یا درگاه رسمی مربوطه -->
                    <div v-if="selectedService?.official_url" class="p-3 bg-blue-50/60 rounded-2xl border border-blue-100 flex justify-between items-center text-xs">
                        <div class="flex items-center gap-2">
                            <span>🏛</span>
                            <span class="font-bold text-blue-900">سامانه رسمی استعلام/ثبت‌نام:</span>
                        </div>
                        <a :href="selectedService.official_url" target="_blank" class="text-[11px] font-black text-blue-600 hover:underline flex items-center gap-1">
                            <span>مشاهده درگاه</span>
                            <span>↗</span>
                        </a>
                    </div>

                    <!-- مدارک و الزامات مورد نیاز -->
                    <div v-if="selectedService?.required_docs && selectedService.required_docs.length > 0" class="space-y-2">
                        <h3 class="text-xs font-black text-slate-900 flex items-center gap-1.5">
                            <span>📑</span>
                            <span>مدارک و اطلاعات الزامی برای ثبت:</span>
                        </h3>
                        <ul class="space-y-1.5 text-xs text-slate-700 bg-slate-50/70 p-3.5 rounded-2xl border border-slate-100">
                            <li v-for="(doc, idx) in selectedService.required_docs" :key="idx" class="flex items-center gap-2">
                                <span class="text-emerald-500 font-bold">✓</span>
                                <span>{{ doc }}</span>
                            </li>
                        </ul>
                    </div>

                    <!-- دکمه‌های اقدام -->
                    <div class="pt-2 space-y-2">
                        <button @click="openServiceForm(selectedService)"
                            class="w-full py-3 bg-gradient-to-r from-limo-500 to-lime-600 hover:from-limo-400 hover:to-lime-500 text-slate-950 font-black rounded-2xl text-xs transition shadow-sm flex items-center justify-center gap-2">
                            <span>تکمیل اطلاعات و ثبت درخواست</span>
                            <span>📝</span>
                        </button>
                        <button @click="currentTab = 'chat'"
                            class="w-full py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-2xl text-xs transition flex items-center justify-center gap-2">
                            <span>گفت‌وگو با پشتیبان درباره این خدمت</span>
                            <span>💬</span>
                        </button>
                    </div>
                </div>
            </div>

            <!-- ======================================================== -->
            <!-- ۴. فرم پویا و ارسال مدارک سفارش (Dynamic Order Form) -->
            <!-- ======================================================== -->
            <div v-if="currentTab === 'order_form'" class="bg-white rounded-3xl p-5 border border-slate-100 shadow-soft space-y-4 limo-motion-pop">
                <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                    <div>
                        <span class="text-[10px] text-limo-700 font-bold block">فرم ثبت درخواست آنلاین</span>
                        <h2 class="text-sm font-black text-slate-900">{{ selectedService?.title }}</h2>
                    </div>
                    <button @click="currentTab = 'service_detail'" class="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-xl text-xs font-bold transition">
                        ← راهنمای خدمت
                    </button>
                </div>

                <div v-if="orderError" class="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl font-medium">
                    {{ orderError }}
                </div>

                <form @submit.prevent="submitOrder" class="space-y-3.5 text-xs">
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">نام و نام خانوادگی <span class="text-rose-500">*</span></label>
                        <input v-model="orderFormData.fullName" type="text" required placeholder="مثال: علی رضایی"
                            class="w-full px-3.5 py-2.5 border border-slate-200 rounded-xl focus:border-limo-500 focus:outline-none">
                    </div>

                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">شماره تماس همراه <span class="text-rose-500">*</span></label>
                            <input v-model="orderFormData.phoneNumber" type="tel" required placeholder="09xxxxxxxxx"
                                class="w-full px-3.5 py-2.5 border border-slate-200 rounded-xl focus:border-limo-500 focus:outline-none">
                        </div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">کد ملی / شناسه فراگیر</label>
                            <input v-model="orderFormData.nationalCode" type="text" placeholder="10 رقمی"
                                class="w-full px-3.5 py-2.5 border border-slate-200 rounded-xl focus:border-limo-500 focus:outline-none">
                        </div>
                    </div>

                    <!-- فیلدهای سفارشی پویا (در صورت تعریف فیلد خاص در پنل ادمین) -->
                    <div v-for="field in dynamicFields" :key="field.key" class="space-y-1">
                        <label class="block font-bold text-slate-700">
                            {{ field.label }} <span v-if="field.required" class="text-rose-500">*</span>
                        </label>
                        <input v-if="field.type !== 'textarea'" v-model="dynamicFieldValues[field.key]" :type="field.type || 'text'" :placeholder="field.placeholder || ''"
                            :required="field.required" class="w-full px-3.5 py-2.5 border border-slate-200 rounded-xl">
                        <textarea v-else v-model="dynamicFieldValues[field.key]" rows="2" :placeholder="field.placeholder || ''"
                            :required="field.required" class="w-full px-3.5 py-2.5 border border-slate-200 rounded-xl"></textarea>
                    </div>

                    <!-- بخش آپلود فیش یا فایل‌های ضمیمه -->
                    <div class="space-y-1 pt-1">
                        <label class="block font-bold text-slate-700">بارگذاری مدارک یا تصاویر ضمیمه (اختیاری)</label>
                        <input type="file" @change="handleFileUpload" accept="image/*,application/pdf"
                            class="w-full text-[11px] text-slate-500 file:mr-2 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-slate-100 file:text-slate-700 hover:file:bg-slate-200 cursor-pointer">
                        <p v-if="uploadedFileName" class="text-[10px] text-emerald-600 font-bold mt-1">✓ فایل آماده ارسال: {{ uploadedFileName }}</p>
                    </div>

                    <!-- توضیحات و نکات سفارش -->
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">توضیحات و نکات تکمیلی شما برای اپراتور</label>
                        <textarea v-model="orderFormData.notes" rows="2" placeholder="اگر نکته‌ای مدنظر دارید بنویسید..."
                            class="w-full px-3.5 py-2.5 border border-slate-200 rounded-xl"></textarea>
                    </div>

                    <div class="pt-3 flex gap-2">
                        <button type="button" @click="currentTab = 'services'" class="px-4 py-2.5 bg-slate-100 rounded-xl font-bold text-slate-600">انصراف</button>
                        <button type="submit" :disabled="isSubmitting"
                            class="flex-1 py-2.5 bg-gradient-to-r from-limo-500 to-lime-600 hover:from-limo-400 hover:to-lime-500 text-slate-950 font-black rounded-xl transition shadow-sm">
                            {{ isSubmitting ? 'در حال ثبت سفارش...' : 'تأیید و ثبت نهایی درخواست' }}
                        </button>
                    </div>
                </form>
            </div>

            <!-- ======================================================== -->
            <!-- ۵. تب ثبت‌نام‌های مقطعی (Seasonal Tab) -->
            <!-- ======================================================== -->
            <div v-if="currentTab === 'seasonal'" class="space-y-3 limo-motion-pop">
                <div class="bg-gradient-to-l from-amber-500/15 to-white p-4 rounded-3xl border border-amber-200/80 shadow-soft">
                    <h2 class="text-xs font-black text-slate-900 flex items-center gap-1.5">
                        <span class="text-amber-500 text-base">⏳</span>
                        <span>ثبت‌نام‌های مقطعی، آزمون‌ها و رویدادهای فصلی</span>
                    </h2>
                    <p class="text-[11px] text-slate-500 mt-1">این رویدادها دارای بازه زمانی محدود هستند؛ توصیه می‌شود در اسرع وقت اقدام فرمایید.</p>
                </div>

                <div v-if="campaigns.length === 0" class="text-center py-12 bg-white rounded-3xl border border-slate-100 shadow-soft">
                    <span class="text-3xl block mb-2">🌿</span>
                    <p class="text-xs font-bold text-slate-500">در حال حاضر رویداد مقطعی فعالی ثبت نشده است.</p>
                </div>

                <div v-else class="space-y-3">
                    <div v-for="c in campaigns" :key="c.id"
                        class="bg-white rounded-3xl p-5 border border-slate-100 shadow-soft hover:shadow-hover transition space-y-3">
                        <div class="flex justify-between items-start">
                            <div>
                                <span :class="seasonalBadgeClass(c.status)" class="text-[10px] font-bold px-2.5 py-0.5 rounded-full inline-block mb-1">
                                    {{ seasonalStatusLabel(c.status) }}
                                </span>
                                <h3 class="text-sm font-black text-slate-900">{{ c.title }}</h3>
                            </div>
                            <span class="text-xs font-black text-emerald-600">{{ formatTomans(c.base_fee || 50000) }}</span>
                        </div>

                        <p class="text-[11px] text-slate-600 leading-relaxed">{{ c.description || 'ثبت‌نام رسمی توسط اپراتور با ارائه کد پیگیری سامانه مربوطه.' }}</p>

                        <div class="text-[10px] text-slate-500 bg-slate-50 p-2.5 rounded-xl border border-slate-100 flex justify-between">
                            <span>شروع: {{ formatDate(c.start_at) }}</span>
                            <span>پایان مهلت: {{ formatDate(c.end_at) }}</span>
                        </div>

                        <div class="pt-1 flex gap-2">
                            <button @click="applyForCampaign(c)"
                                class="flex-1 py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-xl text-xs transition shadow-sm">
                                ثبت‌نام در این رویداد
                            </button>
                            <button @click="remindMe(c)" class="px-3.5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl text-xs transition" title="یادآوری قبل از اتمام مهلت">
                                🔔 یادآوری
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ======================================================== -->
            <!-- ۶. تب گفت‌وگوی زنده با پشتیبانی (Live Chat Tab) -->
            <!-- ======================================================== -->
            <div v-if="currentTab === 'chat'" class="bg-white rounded-3xl border border-slate-100 shadow-soft flex flex-col h-[75vh] overflow-hidden limo-motion-pop">
                <!-- هدر چت -->
                <div class="p-3.5 bg-slate-50 border-b border-slate-100 flex justify-between items-center">
                    <div class="flex items-center gap-2">
                        <div class="w-8 h-8 rounded-full bg-limo-500 text-slate-950 font-black text-xs flex items-center justify-center">
                            ل
                        </div>
                        <div>
                            <h3 class="text-xs font-black text-slate-900">پشتیبانی آنلاین کافی‌نت لیمو</h3>
                            <span class="text-[10px] text-emerald-600 font-medium">پاسخگویی مستقیم کارشناس</span>
                        </div>
                    </div>
                    <button @click="fetchSupportMessages" class="p-1.5 text-slate-400 hover:text-slate-600 text-xs" title="بروزرسانی پیام‌ها">🔄</button>
                </div>

                <!-- استریم پیام‌ها -->
                <div ref="chatContainer" class="flex-1 p-4 space-y-3 overflow-y-auto chat-scroll bg-slate-50/50">
                    <div v-if="chatMessages.length === 0" class="text-center py-10 text-slate-400 text-xs space-y-2">
                        <span class="text-2xl block">💬</span>
                        <p>هنوز پیامی ارسال نشده است. سوال یا درخواست خود را بنویسید تا اپراتور پاسخ دهد.</p>
                    </div>

                    <div v-for="m in chatMessages" :key="m.id"
                        :class="m.sender_role === 'CUSTOMER' ? 'mr-auto text-left' : 'ml-auto text-right'"
                        class="max-w-[80%] space-y-1">
                        <div :class="m.sender_role === 'CUSTOMER' ? 'bg-slate-900 text-white rounded-2xl rounded-bl-sm' : 'bg-white text-slate-800 border border-slate-200 rounded-2xl rounded-br-sm shadow-sm'"
                            class="p-3 text-xs leading-relaxed">
                            {{ m.message_text }}
                        </div>
                        <span class="text-[9px] text-slate-400 px-1 block">{{ formatDate(m.created_at) }}</span>
                    </div>
                </div>

                <!-- کادر ارسال پیام -->
                <div class="p-3 bg-white border-t border-slate-100 flex gap-2">
                    <input v-model="newChatMessage" @keydown.enter="sendChatMessage" type="text" placeholder="پیام خود را بنویسید..."
                        class="flex-1 px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-2xl text-xs focus:outline-none focus:border-limo-500">
                    <button @click="sendChatMessage" :disabled="isSendingMessage || !newChatMessage.trim()"
                        class="px-4 py-2.5 bg-gradient-to-r from-limo-500 to-lime-600 hover:from-limo-400 hover:to-lime-500 text-slate-950 font-black rounded-2xl text-xs transition shadow-sm disabled:opacity-50">
                        {{ isSendingMessage ? '...' : 'ارسال' }}
                    </button>
                </div>
            </div>

            <!-- ======================================================== -->
            <!-- ۷. پنل کاربری اختصاصی مشتری و سفارش‌ها (Profile & Portal) -->
            <!-- ======================================================== -->
            <div v-if="currentTab === 'profile'" class="space-y-4 limo-motion-pop">
                
                <!-- کارت پروفایل و مشخصات -->
                <div class="bg-white rounded-3xl p-5 border border-slate-100 shadow-soft text-right space-y-3">
                    <div class="flex items-center gap-3">
                        <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-slate-900 to-slate-700 text-white text-lg font-black flex items-center justify-center shadow-sm">
                            {{ (userFullName || 'U').charAt(0) }}
                        </div>
                        <div class="flex-1">
                            <h3 class="text-sm font-black text-slate-900">{{ userFullName }}</h3>
                            <span class="text-[10px] text-slate-400 block">شناسه تلگرام: {{ telegramUserId || 'مهمان' }}</span>
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-2 pt-2 border-t border-slate-100 text-xs">
                        <div class="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                            <span class="text-[10px] text-slate-400 block">کیف پول</span>
                            <span class="font-black text-slate-900 mt-0.5 block">{{ formatTomans(walletBalance) }}</span>
                        </div>
                        <div class="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                            <span class="text-[10px] text-slate-400 block">کل سفارش‌ها</span>
                            <span class="font-black text-slate-900 mt-0.5 block">{{ myOrders.length }} مورد</span>
                        </div>
                    </div>
                </div>

                <!-- سابقه سفارش‌های من با رهگیری -->
                <div class="space-y-2.5">
                    <h3 class="text-xs font-black text-slate-900 px-1 flex items-center gap-1.5">
                        <span class="text-limo-700 text-sm">📦</span>
                        <span>سفارش‌های من و پیگیری وضعیت:</span>
                    </h3>

                    <div v-if="myOrders.length === 0" class="text-center py-10 bg-white rounded-3xl border border-slate-100 shadow-soft">
                        <span class="text-2xl block mb-1">📋</span>
                        <p class="text-xs text-slate-500">شما هنوز درخواستی ثبت نکرده‌اید.</p>
                        <button @click="currentTab = 'services'" class="mt-3 px-4 py-2 bg-slate-900 text-white rounded-xl text-xs font-bold shadow-sm">
                            مشاهده و ثبت خدمات
                        </button>
                    </div>

                    <div v-else class="space-y-2.5">
                        <div v-for="ord in myOrders" :key="ord.id"
                            class="bg-white rounded-3xl p-4 border border-slate-100 shadow-soft space-y-2.5 text-right">
                            <div class="flex justify-between items-start">
                                <div>
                                    <h4 class="text-xs font-black text-slate-900">{{ ord.service_title || 'سفارش لیمو' }}</h4>
                                    <span class="text-[10px] text-slate-400 font-mono block mt-0.5">کد رهگیری: {{ ord.tracking_code }}</span>
                                </div>
                                <span :class="orderStatusBadgeClass(ord.status)" class="text-[9px] font-bold px-2.5 py-0.5 rounded-full">
                                    {{ orderStatusLabel(ord.status) }}
                                </span>
                            </div>

                            <div v-if="ord.operator_notes" class="p-2.5 bg-amber-50 rounded-xl border border-amber-200 text-amber-900 text-[11px] leading-relaxed">
                                <span class="font-bold block mb-0.5">پیام اپراتور:</span>
                                {{ ord.operator_notes }}
                            </div>

                            <div class="flex justify-between items-center text-[10px] text-slate-400 pt-2 border-t border-slate-50">
                                <span>مبلغ: {{ formatTomans(ord.total_amount) }}</span>
                                <span>{{ formatDate(ord.created_at) }}</span>
                            </div>
                        </div>
                    </div>
                </div>

            </div>

            <!-- ======================================================== -->
            <!-- ۸. صفحه اختصاصی درباره ما (About Us Tab) -->
            <!-- ======================================================== -->
            <div v-if="currentTab === 'about'" class="space-y-4 limo-motion-pop">
                
                <!-- کارت معرفی اصلی -->
                <div class="bg-gradient-to-l from-slate-900 via-slate-800 to-slate-900 rounded-3xl p-5 text-white shadow-soft relative overflow-hidden">
                    <div class="absolute -top-10 -right-10 w-28 h-28 bg-limo-500/20 rounded-full blur-xl"></div>
                    <div class="relative z-10 space-y-2">
                        <div class="flex items-center gap-2">
                            <span class="text-2xl">🍋</span>
                            <h2 class="text-sm font-black text-white">{{ aboutData.title || 'درباره کافی‌نت آنلاین لیمو' }}</h2>
                        </div>
                        <p class="text-[11px] text-limo-300 font-medium">{{ aboutData.subtitle || 'پورتال جامع خدمات دیجیتال و اینترنتی کشور' }}</p>
                        <p class="text-[11px] text-slate-300 leading-relaxed pt-1">
                            {{ aboutData.story || 'کافی‌نت آنلاین لیمو با سال‌ها تجربه در ارائه خدمات فنی و اینترنتی، بستری مدرن و امن را برای انجام غیرحضوری کلیه درخواست‌های ثبت‌نامی، استعلام مدارک، خدمات دانشجویی دانشگاه‌های سراسری، آزاد، پیام نور و امور بین‌الملل فراهم کرده است. هدف ما حذف نیاز به مراجعات حضوری و اتلاف وقت متقاضیان با ارائه خدمات سریع، دقیق و با پشتیبانی پیوسته است.' }}
                        </p>
                    </div>
                </div>

                <!-- پخش‌کننده موشن‌گرافیک رسمی برند در بخش درباره ما -->
                <div v-if="motionGraphicsEnabled !== '0'" class="bg-white rounded-3xl p-4 border border-slate-100 shadow-soft space-y-2.5">
                    <div class="flex justify-between items-center px-1">
                        <h3 class="text-xs font-black text-slate-900 flex items-center gap-1.5">
                            <span>🎬</span>
                            <span>تیزر موشن‌گرافیک رسمی کافی‌نت لیمو:</span>
                        </h3>
                        <span class="text-[9px] font-bold text-limo-800 bg-limo-100 px-2 py-0.5 rounded-full">نسخه اختصاصی وب</span>
                    </div>
                    <div class="rounded-2xl overflow-hidden border border-slate-200/80 bg-slate-950 aspect-video flex items-center justify-center shadow-inner">
                        <video controls playsinline poster="/motion-logo-poster.webp" class="w-full h-full object-contain">
                            <source src="/motion-logo.mp4" type="video/mp4">
                            مرورگر شما از پخش ویدیو پشتیبانی نمی‌کند.
                        </video>
                    </div>
                </div>

                <!-- مزایای کلیدی لیمو -->
                <div class="space-y-2">
                    <h3 class="text-xs font-black text-slate-900 px-1 flex items-center gap-1.5">
                        <span class="text-limo-600">⭐</span>
                        <span>ویژگی‌ها و استانداردهای کافی‌نت لیمو:</span>
                    </h3>

                    <div class="grid grid-cols-2 gap-2 text-right">
                        <div class="bg-white p-3 rounded-2xl border border-slate-100 shadow-soft space-y-1">
                            <span class="text-base block">⚡</span>
                            <h4 class="text-xs font-black text-slate-900">سرعت و دقت بالا</h4>
                            <p class="text-[10px] text-slate-400">انجام فوری درخواست‌ها با کد رهگیری معتبر</p>
                        </div>
                        <div class="bg-white p-3 rounded-2xl border border-slate-100 shadow-soft space-y-1">
                            <span class="text-base block">🔒</span>
                            <h4 class="text-xs font-black text-slate-900">امنیت و امانت‌داری</h4>
                            <p class="text-[10px] text-slate-400">حفاظت کامل از اطلاعات و مدارک شخصی متقاضی</p>
                        </div>
                        <div class="bg-white p-3 rounded-2xl border border-slate-100 shadow-soft space-y-1">
                            <span class="text-base block">📡</span>
                            <h4 class="text-xs font-black text-slate-900">پایش هوشمند</h4>
                            <p class="text-[10px] text-slate-400">اطلاع‌رسانی لحظه‌ای بازگشایی سامانه‌ها و آزمون‌ها</p>
                        </div>
                        <div class="bg-white p-3 rounded-2xl border border-slate-100 shadow-soft space-y-1">
                            <span class="text-base block">💬</span>
                            <h4 class="text-xs font-black text-slate-900">پشتیبانی اختصاصی</h4>
                            <p class="text-[10px] text-slate-400">پاسخگویی مستقیم از طریق ربات و پیام‌رسان‌ها</p>
                        </div>
                    </div>
                </div>

                <!-- ساعات کاری و اطلاعات تماس -->
                <div class="bg-white rounded-3xl p-4 border border-slate-100 shadow-soft space-y-2.5 text-xs text-right">
                    <div class="flex items-center justify-between py-1 border-b border-slate-50">
                        <span class="text-slate-400">ساعات کاری:</span>
                        <span class="font-bold text-slate-800">{{ aboutData.working_hours || 'همه روزه ۸:۰۰ الی ۲۱:۰۰ (پشتیبانی آنلاین پیوسته)' }}</span>
                    </div>
                    <div class="flex items-center justify-between py-1 border-b border-slate-50">
                        <span class="text-slate-400">شماره پشتیبانی:</span>
                        <a :href="'tel:' + (aboutData.phone || '09364519860')" class="font-black text-emerald-600">{{ aboutData.phone || '۰۹۳۶۴۵۱۹۸۶۰' }}</a>
                    </div>
                    <div class="flex items-center justify-between py-1">
                        <span class="text-slate-400">آدرس خدمات:</span>
                        <span class="font-bold text-slate-800">{{ aboutData.address || 'تهران - پورتال آنلاین خدمات کشوری کافی‌نت لیمو' }}</span>
                    </div>
                </div>

                <div class="pt-1 text-center">
                    <button @click="currentTab = 'home'" class="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-2xl text-xs transition shadow-sm">
                        بازگشت به صفحه اصلی
                    </button>
                </div>

            </div>

        </main>

        <!-- ======================================================== -->
        <!-- ۹. نوار ناوبری شناور و مدرن پایین صفحه (Bottom Nav Bar) -->
        <!-- ======================================================== -->
        <nav class="fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur-xl border-t border-slate-200 shadow-nav max-w-md md:max-w-xl mx-auto" style="padding-bottom: max(env(safe-area-inset-bottom, 0px), 6px);">
            <div class="grid grid-cols-5 py-2 px-1 text-center">
                <button @click="currentTab = 'home'"
                    :class="currentTab === 'home' ? 'text-limo-700 font-black' : 'text-slate-400 hover:text-slate-600 font-medium'"
                    class="py-1 flex flex-col items-center gap-0.5 transition">
                    <span class="text-lg">🏠</span>
                    <span class="text-[10px]">خانه</span>
                </button>
                <button @click="currentTab = 'services'"
                    :class="currentTab === 'services' || currentTab === 'service_detail' || currentTab === 'order_form' ? 'text-limo-700 font-black' : 'text-slate-400 hover:text-slate-600 font-medium'"
                    class="py-1 flex flex-col items-center gap-0.5 transition">
                    <span class="text-lg">📋</span>
                    <span class="text-[10px]">خدمات</span>
                </button>
                <button @click="currentTab = 'seasonal'"
                    :class="currentTab === 'seasonal' ? 'text-limo-700 font-black' : 'text-slate-400 hover:text-slate-600 font-medium'"
                    class="py-1 flex flex-col items-center gap-0.5 transition relative">
                    <span v-if="campaigns.length > 0" class="absolute top-1 right-5 w-1.5 h-1.5 rounded-full bg-rose-500"></span>
                    <span class="text-lg">⏳</span>
                    <span class="text-[10px]">مقطعی</span>
                </button>
                <button @click="currentTab = 'chat'"
                    :class="currentTab === 'chat' ? 'text-limo-700 font-black' : 'text-slate-400 hover:text-slate-600 font-medium'"
                    class="py-1 flex flex-col items-center gap-0.5 transition relative">
                    <span v-if="unreadSupportCount > 0" class="absolute top-1 right-5 w-3.5 h-3.5 rounded-full bg-rose-500 text-white text-[8px] font-black flex items-center justify-center">{{ unreadSupportCount }}</span>
                    <span class="text-lg">💬</span>
                    <span class="text-[10px]">پشتیبانی</span>
                </button>
                <button @click="currentTab = 'profile'"
                    :class="currentTab === 'profile' ? 'text-limo-700 font-black' : 'text-slate-400 hover:text-slate-600 font-medium'"
                    class="py-1 flex flex-col items-center gap-0.5 transition">
                    <span class="text-lg">👤</span>
                    <span class="text-[10px]">پروفایل</span>
                </button>
            </div>
        </nav>

    </div>

    <!-- منطق جاوااسکریپت و Vue 3 مینی‌اپلیکیشن -->
    <script>

        // کاتالوگ پشتیبان آفلاین (Offline Fallback Catalog) جهت لود آنی و بدون فریز در پروکسی تلگرام
        const FALLBACK_BOOTSTRAP_DATA = {"categories": [{"id": 7, "code": "TAX", "title": "💼 امور مالیاتی و اصناف", "description": "خدمات اظهارنامه، ثبت نام مالیاتی و پرونده اصناف"}, {"id": 4, "code": "GOVERNMENT_INTERNET", "title": "🏛 سایر خدمات اینترنتی و اداری", "description": "انواع ثبت‌نام‌ها و خدمات اداری و دولتی الکترونیک"}, {"id": 3, "code": "TICKETS_TRAVEL", "title": "✈️ بلیت هواپیما، قطار و اتوبوس", "description": "صدور و استعلام بلیت کلیه خطوط ریلی، پروازی و جاده‌ای کشور"}, {"id": 2, "code": "UNIVERSITY_SERVICES", "title": "🎓 خدمات دانشگاهی و آزمون‌ها", "description": "امور ثبت‌نام آزمون‌های سراسری، تاییدیه تحصیلی و سامانه‌های آموزشی"}, {"id": 1, "code": "ALIEN_AND_CODES", "title": "🌐 امور اتباع و کدها", "description": "نوبت‌دهی تثبیت هویت، سامانه امور دانشجویان بین‌الملل و پذیرش اتباع"}], "services": [{"id": 1, "category_id": 1, "code": "EMT_VERIFICATION", "title": "استعلام تاییدیه تحصیلی و کد صحت", "desc": "دریافت استعلام رسمی مدرک دیپلم و پیش‌دانشگاهی از سامانه وزارت آموزش و پرورش (emt.medu.ir) جهت ثبت‌نام دانشگاه.", "guide_content": "مراحل انجام کار:\\n۱. ثبت مشخصات فردی و تحصیلی داوطلب\\n۲. دریافت کد پیگیری استعلام از سامانه وزارت آموزش و پرورش\\n۳. ارسال به دانشگاه یا سازمان استعلام‌گیرنده\\n\\nمدارک لازم: تصویر گواهی موقت دیپلم یا مدرک پایان تحصیلات به همراه کد ملی ۱۰ رقمی.", "official_url": "https://emt.medu.ir/", "category": "🎓 خدمات دانشجویی و آزمون‌ها", "base_fee": 50000, "required_fields": [{"key": "national_id", "label": "کد ملی ۱۰ رقمی متقاضی", "type": "text", "required": true}, {"key": "education_level", "label": "مقطع تحصیلی (دیپلم / پیش‌دانشگاهی)", "type": "text", "required": true}, {"key": "school_name", "label": "نام دبیرستان یا مدرسه محل تحصیل", "type": "text", "required": true}, {"key": "graduation_year", "label": "سال فراغت از تحصیل", "type": "text", "required": true}, {"key": "destination_org", "label": "نام دانشگاه یا سازمان استعلام‌گیرنده", "type": "text", "required": true}], "required_docs": ["تصویر مدرک تحصیلی یا گواهی موقت", "تصویر کارت ملی یا شناسنامه"]}, {"id": 2, "category_id": 1, "code": "SANJESH_REGISTRATION", "title": "ثبت‌نام آزمون‌های سازمان سنجش", "desc": "ثبت‌نام، ویرایش اطلاعات، دریافت کد سوابق تحصیلی مای‌مدیو و آزمون‌های سراسری سازمان سنجش.", "guide_content": "راهنمای ثبت‌نام:\\n۱. بررسی شرایط دفترچه آزمون مورد نظر\\n۲. تایید سوابق تحصیلی در سامانه مای مدیو\\n۳. تکمیل فرم اینترنتی و دریافت شماره پرونده و کد پیگیری نهایی.", "official_url": "https://www.sanjesh.org/", "category": "🎓 خدمات دانشجویی و آزمون‌ها", "base_fee": 65000, "required_fields": [{"key": "exam_type", "label": "نوع آزمون (سراسری / کارشناسی ارشد / دکتری)", "type": "text", "required": true}, {"key": "national_id", "label": "کد ملی داوطلب", "type": "text", "required": true}, {"key": "mobile_phone", "label": "شماره همراه به نام متقاضی", "type": "tel", "required": true}], "required_docs": ["عکس پرسنلی ۴×۳ استاندارد", "تصویر کارنامه یا مدرک مقطع قبلی"]}, {"id": 3, "category_id": 1, "code": "PNU_SERVICES", "title": "سامانه گلستان دانشگاه پیام نور", "desc": "امور انتخاب واحد، کارنامه، گواهی اشتغال به تحصیل، تسویه حساب و امور مالی در سامانه جامع گلستان پیام نور.", "guide_content": "راهنما:\\nامور آموزشی و اداری شامل صدور گواهی اشتغال، پرینت فرم‌های امتحانی، تسویه شهریه و کارنامه تحصیلی بدون نیاز به مراجعه حضوری انجام می‌پذیرد.", "official_url": "https://osreg.pnu.ac.ir/forms/authenticateuser/main.htm", "category": "🎓 خدمات دانشجویی و آزمون‌ها", "base_fee": 45000, "required_fields": [{"key": "student_id", "label": "شماره دانشجویی گلستان", "type": "text", "required": true}, {"key": "national_id", "label": "کد ملی دانشجو", "type": "text", "required": true}, {"key": "request_type", "label": "نوع درخواست (انتخاب واحد / گواهی / کارنامه)", "type": "text", "required": true}], "required_docs": ["تصویر کارت دانشجویی"]}, {"id": 4, "category_id": 1, "code": "IAU_SERVICES", "title": "سامانه آموزشیار دانشگاه آزاد اسلامی", "desc": "انتخاب واحد، پرداخت شهریه، اخذ مجوز امتحان، مشاهده نمرات و درخواست‌های آموزشی در درگاه آموزشیار.", "guide_content": "راهنما:\\nکلیه امور ثبت انتخاب واحد، تاییدیه مجوز ورود به جلسه آزمون و تسویه حساب مالی دانشجویان دانشگاه آزاد در سراسر کشور.", "official_url": "https://edu.iau.ac.ir/", "category": "🎓 خدمات دانشجویی و آزمون‌ها", "base_fee": 55000, "required_fields": [{"key": "student_id", "label": "شماره دانشجویی آموزشیار", "type": "text", "required": true}, {"key": "national_id", "label": "کد ملی دانشجو", "type": "text", "required": true}, {"key": "campus_name", "label": "واحد دانشگاهی و مقطع", "type": "text", "required": true}], "required_docs": ["تصویر کارت دانشجویی یا برگ انتخاب واحد قبلی"]}, {"id": 5, "category_id": 2, "code": "IVSF_APPOINTMENT", "title": "سامانه نوبت‌دهی تثبیت هویت اتباع", "desc": "اخذ نوبت اداری الکترونیکی جهت تثبیت هویت، تایید اسناد و امور هویتی اتباع در سامانه رسمی نوبت‌دهی (ivsf.nsia.gov.af).", "guide_content": "راهنمای دریافت نوبت:\\n۱. نوبت‌دهی رسمی با وارد کردن اطلاعات تذکره الکترونیکی یا برگه هویتی\\n۲. تعیین نزدیک‌ترین نمایندگی یا مرکز اداری مورد تقاضا\\n۳. دریافت برگه رسمی نوبت‌دهی با بارکد معتبر.", "official_url": "http://ivsf.nsia.gov.af/", "category": "🌐 امور کنسولی و بین‌الملل", "base_fee": 120000, "required_fields": [{"key": "identity_code", "label": "شماره تذکره یا شناسه هویتی متقاضی", "type": "text", "required": true}, {"key": "full_name", "label": "نام و نام خانوادگی مطابق مدارک", "type": "text", "required": true}, {"key": "phone_number", "label": "شماره تلفن همراه فعال", "type": "tel", "required": true}, {"key": "preferred_city", "label": "شهر یا نمایندگی مورد تقاضا", "type": "text", "required": true}], "required_docs": ["تصویر تذکره یا برگه هویتی", "تصویر گذرنامه یا برگه اقامت"]}, {"id": 6, "category_id": 2, "code": "ADAB_STUDENT_AFFAIRS", "title": "سامانه امور دانشجویان بین‌الملل (ادب)", "desc": "ثبت و پیگیری امور روادید تحصیلی، تمدید اقامت، امور کنسولی و پذیرش دانشجویان غیرایرانی در پورتال ادب (saorg.ir).", "guide_content": "راهنما:\\nسامانه ادب متعلق به سازمان امور دانشجویان وزارت علوم بوده و فرآیندهای مربوط به اقامت تحصیلی، تمدید روادید و خروج و مراجعت دانشجویان بین‌الملل را پردازش می‌کند.", "official_url": "https://adab.saorg.ir/PortalADAB/Home/LandingPage", "category": "🌐 امور کنسولی و بین‌الملل", "base_fee": 90000, "required_fields": [{"key": "passport_number", "label": "شماره گذرنامه معتبر", "type": "text", "required": true}, {"key": "tracking_or_fara_code", "label": "کد فراگیر / شناسه پیگیری سامانه ادب", "type": "text", "required": true}, {"key": "target_university", "label": "نام دانشگاه محل تحصیل در ایران", "type": "text", "required": true}], "required_docs": ["تصویر صفحه اول گذرنامه معتبر", "تصویر نامه پذیرش یا گواهی اشتغال به تحصیل"]}], "campaigns": [], "channels": [{"key": "PHONE", "title": "تلفن پشتیبانی کافی‌نت لیمو: 09364519860", "value": "tel:09364519860"}, {"key": "EITAA", "title": "پشتیبانی ایتا", "value": "https://eitaa.com/Cafinet_limo"}, {"key": "TELEGRAM", "title": "کانال تلگرام", "value": "https://t.me/LimoCafeBot"}, {"key": "RUBIKA", "title": "پشتیبانی روبیکا", "value": "https://rubika.ir/cafinet_limo"}, {"key": "BALE", "title": "پشتیبانی بله", "value": "https://ble.ir/cafinet_limo"}]};

        function normalizeClientFields(raw) {
            if (!raw) return [];
            let parsed = raw;
            if (typeof raw === 'string') {
                try { parsed = JSON.parse(raw); } catch(e) { return []; }
            }
            if (Array.isArray(parsed)) {
                return parsed.map((item, idx) => {
                    if (typeof item === 'string') {
                        return { key: 'field_' + (idx + 1), label: item, type: 'text', required: true };
                    }
                    return {
                        key: item.key || item.name || ('field_' + (idx + 1)),
                        label: item.label || item.title || item.name || ('فیلد ' + (idx + 1)),
                        type: item.type || 'text',
                        required: item.required !== false
                    };
                });
            }
            if (typeof parsed === 'object' && parsed !== null) {
                return Object.entries(parsed).map(([k, v], idx) => {
                    if (typeof v === 'string') {
                        return { key: k, label: v, type: 'text', required: true };
                    }
                    return {
                        key: k,
                        label: (v && v.label) || (v && v.title) || k,
                        type: (v && v.type) || 'text',
                        required: v && v.required !== undefined ? !!v.required : true
                    };
                });
            }
            return [];
        }

        const { createApp, ref, computed, onMounted, nextTick } = Vue;

        createApp({
            setup() {
                const currentTab = ref('home');
                const shopIsOpen = ref(true);
                const userFullName = ref('کاربر لیمو');
                const networkError = ref(false);
                const isLoadingData = ref(false);
                const telegramUserId = ref(null);
                const walletBalance = ref(0);
                const motionGraphicsEnabled = ref('1');

                const categories = ref([...FALLBACK_BOOTSTRAP_DATA.categories]);
                const services = ref([...FALLBACK_BOOTSTRAP_DATA.services]);
                const campaigns = ref([...FALLBACK_BOOTSTRAP_DATA.campaigns]);
                const channels = ref([...FALLBACK_BOOTSTRAP_DATA.channels]);
                const myOrders = ref([]);
                const selectedCategory = ref('ALL');
                const serviceSearchQuery = ref('');

                // محتوای درباره ما
                const aboutData = ref({
                    title: 'درباره کافی‌نت آنلاین لیمو',
                    subtitle: 'پورتال جامع خدمات دیجیتال و اینترنتی کشور',
                    story: 'کافی‌نت آنلاین لیمو با سال‌ها تجربه در ارائه خدمات فنی و اینترنتی، بستری مدرن و امن را برای انجام غیرحضوری کلیه درخواست‌های ثبت‌نامی، استعلام مدارک، خدمات دانشجویی دانشگاه‌های سراسری، آزاد، پیام نور و امور بین‌الملل فراهم کرده است.',
                    working_hours: 'همه روزه ۸:۰۰ الی ۲۱:۰۰ (پشتیبانی آنلاین پیوسته)',
                    phone: '۰۹۳۶۴۵۱۹۸۶۰',
                    address: 'تهران - پورتال آنلاین خدمات کشوری کافی‌نت لیمو'
                });

                // سفارش و فرم پویا
                const selectedService = ref(null);
                const orderFormData = ref({ fullName: '', phoneNumber: '', nationalCode: '', notes: '' });
                const dynamicFields = ref([]);
                const dynamicFieldValues = ref({});
                const isSubmitting = ref(false);
                const orderError = ref('');
                const uploadedFileBase64 = ref('');
                const uploadedFileName = ref('');

                // گفت‌وگوی زنده پشتیبانی
                const chatMessages = ref([]);
                const newChatMessage = ref('');
                const isSendingMessage = ref(false);
                const unreadSupportCount = ref(0);
                const chatContainer = ref(null);

                // فیلتر خدمات (بدون وابستگی به کدهای داخلی)
                const filteredServicesList = computed(() => {
                    return services.value.filter(s => {
                        const matchCat = (selectedCategory.value === 'ALL') || (s.category_id === selectedCategory.value);
                        const q = serviceSearchQuery.value.trim().toLowerCase();
                        const matchQ = !q || (s.title && s.title.toLowerCase().includes(q)) || (s.desc && s.desc.toLowerCase().includes(q));
                        return matchCat && matchQ;
                    });
                });

                // دریافت داده‌های بوت‌استرپ با تاب‌آوری شبکه، تایم‌اوت ۵ ثانیه‌ای و حفظ داده‌های آفلاین
                async function loadInitialData(isManualRetry = false) {
                    if (isManualRetry) isLoadingData.value = true;
                    // خواندن اطلاعات کاربر تلگرام از وب‌اپ
                    if (window.Telegram?.WebApp) {
                        try {
                            window.Telegram.WebApp.ready();
                            window.Telegram.WebApp.expand();
                            const tgUser = window.Telegram.WebApp.initDataUnsafe?.user;
                            if (tgUser) {
                                telegramUserId.value = tgUser.id;
                                userFullName.value = (tgUser.first_name + ' ' + (tgUser.last_name || '')).trim() || 'کاربر گرامی';
                                orderFormData.value.fullName = userFullName.value;
                            }
                        } catch(e) {}
                    }

                    const controller = new AbortController();
                    const timeoutId = setTimeout(() => controller.abort(), 6000); // ۶ ثانیه مهلت دریافت

                    try {
                        const qParams = new URLSearchParams();
                        if (telegramUserId.value) qParams.append('telegram_id', telegramUserId.value);
                        if (userFullName.value) qParams.append('full_name', userFullName.value);

                        const res = await fetch('/api/client/bootstrap?' + qParams.toString(), {
                            signal: controller.signal
                        });
                        clearTimeout(timeoutId);
                        const data = await res.json();
                        if (data.ok) {
                            if (data.categories && data.categories.length > 0) categories.value = data.categories;
                            if (data.services && data.services.length > 0) services.value = data.services;
                            if (data.campaigns) campaigns.value = data.campaigns;
                            if (data.channels && data.channels.length > 0) channels.value = data.channels;
                            networkError.value = false;
                            
                            if (data.settings) {
                                if (data.settings.is_open === '0') shopIsOpen.value = false;
                                else if (data.settings.is_open === '1') shopIsOpen.value = true;
                                if (data.settings.motion_graphics_enabled !== undefined) {
                                    motionGraphicsEnabled.value = String(data.settings.motion_graphics_enabled);
                                }
                                if (data.settings.about_us_content) {
                                    try {
                                        const parsedAbout = JSON.parse(data.settings.about_us_content);
                                        aboutData.value = { ...aboutData.value, ...parsedAbout };
                                    } catch(e) {
                                        aboutData.value.story = data.settings.about_us_content;
                                    }
                                }
                            }

                            if (data.user_data) {
                                walletBalance.value = data.user_data.wallet?.balance || 0;
                                myOrders.value = data.user_data.orders || [];
                                unreadSupportCount.value = data.user_data.unread_messages || 0;
                            }
                        }
                    } catch(e) {
                        clearTimeout(timeoutId);
                        console.warn('Network issue during bootstrap, fallback catalog active:', e.message);
                        networkError.value = true;
                    } finally {
                        isLoadingData.value = false;
                    }
                }

                async function fetchUserDashboard() {
                    if (!telegramUserId.value) return;
                    try {
                        const res = await fetch('/api/client/user/dashboard?telegram_id=' + telegramUserId.value + '&full_name=' + encodeURIComponent(userFullName.value));
                        const data = await res.json();
                        if (data.ok) {
                            walletBalance.value = data.wallet?.balance || 0;
                            myOrders.value = data.orders || [];
                            unreadSupportCount.value = data.unread_messages || 0;
                        }
                    } catch(e) {}
                }

                async function fetchSupportMessages() {
                    if (!telegramUserId.value) return;
                    try {
                        const res = await fetch('/api/client/support/messages?telegram_id=' + telegramUserId.value);
                        const data = await res.json();
                        if (data.ok) {
                            chatMessages.value = data.messages || [];
                            unreadSupportCount.value = 0;
                            await nextTick();
                            if (chatContainer.value) {
                                chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
                            }
                        }
                    } catch(e) {}
                }

                // ارسال پیام پشتیبانی با بازخورد آنی (Optimistic UI Update)
                async function sendChatMessage() {
                    if (!newChatMessage.value.trim() || isSendingMessage.value) return;
                    const text = newChatMessage.value.trim();
                    newChatMessage.value = '';
                    isSendingMessage.value = true;

                    // افزودن بلادرنگ به لیست پیام‌ها
                    const tempId = 'temp_' + Date.now();
                    chatMessages.value.push({
                        id: tempId,
                        sender_role: 'CUSTOMER',
                        message_text: text,
                        created_at: new Date().toISOString()
                    });
                    await nextTick();
                    if (chatContainer.value) chatContainer.value.scrollTop = chatContainer.value.scrollHeight;

                    try {
                        const res = await fetch('/api/client/support/send', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                telegram_id: telegramUserId.value,
                                full_name: userFullName.value,
                                message: text
                            })
                        });
                        const data = await res.json();
                        if (data.ok) {
                            await fetchSupportMessages();
                        }
                    } catch(e) {
                        alert('خطا در ارسال پیام به پشتیبانی');
                    } finally {
                        isSendingMessage.value = false;
                    }
                }

                // مشاهده صفحه توضیحات، شرایط و راهنمای خدمت قبل از ثبت
                function openServiceDetail(s) {
                    selectedService.value = s;
                    currentTab.value = 'service_detail';
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                }

                // ورود به فرم سفارش با پشتیبانی دوطرفه از آبجکت و آرایه فیلدها
                function openServiceForm(s) {
                    selectedService.value = s;
                    orderError.value = '';
                    uploadedFileBase64.value = '';
                    uploadedFileName.value = '';
                    
                    const normFields = normalizeClientFields(s.required_fields);
                    dynamicFields.value = normFields;
                    dynamicFieldValues.value = {};
                    normFields.forEach(f => {
                        dynamicFieldValues.value[f.key] = '';
                    });

                    currentTab.value = 'order_form';
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                }

                function applyForCampaign(c) {
                    selectedService.value = {
                        id: null,
                        title: c.title,
                        code: c.code,
                        base_fee: c.base_fee || 50000,
                        required_fields: []
                    };
                    orderFormData.value.notes = 'ثبت‌نام در رویداد مقطعی: ' + c.title;
                    currentTab.value = 'order_form';
                }

                function remindMe(c) {
                    alert('🔔 یادآوری برای رویداد "' + c.title + '" با موفقیت فعال شد.');
                }

                function selectCategoryAndBrowse(catId) {
                    selectedCategory.value = catId;
                    currentTab.value = 'services';
                }

                function handleFileUpload(e) {
                    const file = e.target.files[0];
                    if (!file) return;
                    uploadedFileName.value = file.name;
                    const reader = new FileReader();
                    reader.onload = (ev) => {
                        uploadedFileBase64.value = ev.target.result;
                    };
                    reader.readAsDataURL(file);
                }

                async function submitOrder() {
                    if (!orderFormData.value.fullName.trim() || !orderFormData.value.phoneNumber.trim()) {
                        orderError.value = 'نام و شماره تماس برای ثبت سفارش الزامی است.';
                        return;
                    }

                    isSubmitting.value = true;
                    orderError.value = '';

                    const payload = {
                        service_code: selectedService.value?.code || 'GENERAL',
                        serviceCode: selectedService.value?.code || 'GENERAL',
                        service_id: selectedService.value?.id,
                        serviceId: selectedService.value?.id,
                        full_name: orderFormData.value.fullName,
                        fullName: orderFormData.value.fullName,
                        phone_number: orderFormData.value.phoneNumber,
                        phoneNumber: orderFormData.value.phoneNumber,
                        national_code: orderFormData.value.nationalCode,
                        nationalCode: orderFormData.value.nationalCode,
                        telegram_id: telegramUserId.value,
                        form_data: {
                            ...dynamicFieldValues.value,
                            notes: orderFormData.value.notes
                        },
                        formData: {
                            ...dynamicFieldValues.value,
                            notes: orderFormData.value.notes
                        },
                        attachments: uploadedFileBase64.value ? [{ name: uploadedFileName.value, data: uploadedFileBase64.value }] : [],
                        source: 'MINIAPP'
                    };

                    try {
                        const res = await fetch('/api/order/submit', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(payload)
                        });
                        const data = await res.json();
                        if (data.ok) {
                            alert('✅ سفارش شما با موفقیت ثبت شد! - کد رهگیری: ' + (data.tracking_code || '---'));
                            await fetchUserDashboard();
                            currentTab.value = 'profile';
                        } else {
                            orderError.value = data.error || 'خطا در ثبت سفارش';
                        }
                    } catch(e) {
                        orderError.value = 'خطا در ارتباط با سرور هنگام ثبت سفارش';
                    } finally {
                        isSubmitting.value = false;
                    }
                }

                // فرمت‌بندی مبالغ تومان به صورت کاملاً فارسی
                function formatTomans(amount) {
                    if (amount === undefined || amount === null || amount === '') return '۰ تومان';
                    const num = parseInt(amount, 10);
                    if (isNaN(num)) return '۰ تومان';
                    return num.toLocaleString('fa-IR') + ' تومان';
                }

                function formatDate(dateStr) {
                    if (!dateStr) return '---';
                    try {
                        return new Date(dateStr).toLocaleDateString('fa-IR');
                    } catch(e) {
                        return dateStr;
                    }
                }

                function getCategoryIcon(code) {
                    const map = {
                        'ALIEN_AND_CODES': '🛂',
                        'UNIVERSITY_SERVICES': '🎓',
                        'TICKETS_TRAVEL': '✈️',
                        'INQUIRIES': '📑'
                    };
                    return map[code] || '📂';
                }

                function seasonalBadgeClass(st) {
                    if (st === 'OPEN') return 'bg-emerald-100 text-emerald-800';
                    if (st === 'COMING_SOON') return 'bg-amber-100 text-amber-800';
                    return 'bg-slate-100 text-slate-700';
                }

                function seasonalStatusLabel(st) {
                    if (st === 'OPEN') return 'در حال ثبت‌نام';
                    if (st === 'COMING_SOON') return 'به‌زودی';
                    return 'پایان مهلت';
                }

                function orderStatusBadgeClass(st) {
                    const map = {
                        PENDING: 'bg-amber-100 text-amber-800',
                        APPROVED: 'bg-blue-100 text-blue-800',
                        NEED_INFO: 'bg-rose-100 text-rose-800 font-bold',
                        COMPLETED: 'bg-emerald-100 text-emerald-800'
                    };
                    return map[st] || 'bg-slate-100 text-slate-700';
                }

                function orderStatusLabel(st) {
                    const map = {
                        PENDING: 'در انتظار بررسی',
                        APPROVED: 'تأیید اولیه',
                        NEED_INFO: 'نیازمند تکمیل مدارک',
                        COMPLETED: 'تکمیل و تحویل شد'
                    };
                    return map[st] || st;
                }

                // ناوبری خودکار بر اساس پارامترهای لینک تلگرام (?svc=... & ?cat=... & ?tab=...)
                function handleInitialNavigation() {
                    try {
                        const urlParams = new URLSearchParams(window.location.search);
                        const svcParam = urlParams.get('svc');
                        const catParam = urlParams.get('cat');
                        const tabParam = urlParams.get('tab');
                        const codeParam = urlParams.get('code');

                        if (svcParam) {
                            const foundSvc = services.value.find(s => s.code === svcParam || String(s.id) === svcParam);
                            if (foundSvc) {
                                openServiceDetail(foundSvc);
                                return;
                            }
                        }
                        if (catParam) {
                            const foundCat = categories.value.find(c => c.code === catParam || String(c.id) === catParam);
                            selectedCategory.value = foundCat ? foundCat.id : catParam;
                            currentTab.value = 'services';
                            return;
                        }
                        if (tabParam) {
                            currentTab.value = tabParam;
                            return;
                        }
                        if (codeParam) {
                            currentTab.value = 'profile';
                            return;
                        }
                    } catch(e) {
                        console.warn('Initial navigation error:', e);
                    }
                }

                onMounted(async () => {
                    await loadInitialData();
                    handleInitialNavigation();
                    // بررسی دوره‌ای پیام‌های چت
                    setInterval(() => {
                        if (currentTab.value === 'chat') {
                            fetchSupportMessages();
                        }
                    }, 4000);
                });

                return {
                    currentTab,
                    shopIsOpen,
                    userFullName,
                    telegramUserId,
                    walletBalance,
                    motionGraphicsEnabled,
                    categories,
                    services,
                    campaigns,
                    channels,
                    myOrders,
                    aboutData,
                    selectedCategory,
                    serviceSearchQuery,
                    filteredServicesList,
                    selectedService,
                    orderFormData,
                    dynamicFields,
                    dynamicFieldValues,
                    isSubmitting,
                    orderError,
                    uploadedFileName,
                    chatMessages,
                    newChatMessage,
                    isSendingMessage,
                    unreadSupportCount,
                    chatContainer,
                    formatTomans,
                    formatDate,
                    getCategoryIcon,
                    seasonalBadgeClass,
                    seasonalStatusLabel,
                    orderStatusBadgeClass,
                    orderStatusLabel,
                    openServiceForm,
                    applyForCampaign,
                    remindMe,
                    selectCategoryAndBrowse,
                    openServiceDetail,
                    networkError,
                    isLoadingData,
                    handleFileUpload,
                    submitOrder,
                    fetchSupportMessages,
                    sendChatMessage
                };
            }
        }).mount('#app');
    </script>
</body>
</html>"""

# Export to cloudflare/miniapp_html.js
js_export = "export const CLIENT_WEBAPP_HTML = " + json.dumps(html_content, ensure_ascii=False) + ";\n"

output_path = os.path.join("cloudflare", "miniapp_html.js")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(js_export)

print("SUCCESS: miniapp_html.js compiled cleanly. Length:", len(js_export))
