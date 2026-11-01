# -*- coding: utf-8 -*-
"""
تولید فایل جامع cloudflare/admin_html.js شامل ۹ ماژول مستقل مصوب به همراه پایش هوشمند
"""
import os

html_content = r'''<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>داشبورد مدیریت کافی نت لیمو</title>
    <link rel="icon" type="image/png" href="/logo.png">
    <script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;600;700;800;900&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: { sans: ['Vazirmatn', 'sans-serif'] },
                    colors: {
                        limo: { 50: '#f7fee7', 100: '#ecfccb', 400: '#a3e635', 500: '#84cc16', 600: '#65a30d', 700: '#4d7c0f', 800: '#3f6212' },
                        navy: { 800: '#1e293b', 900: '#0f172a' }
                    }
                }
            }
        }
    </script>
    <style>
        [v-cloak] { display: none !important; }
        body { font-family: 'Vazirmatn', sans-serif; background-color: #f8fafc; color: #1e293b; }
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #f1f5f9; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
    </style>
</head>
<body class="min-h-screen bg-slate-50 antialiased">
    <div id="admin-app" v-cloak class="min-h-screen flex flex-col">
        
        <!-- صفحه ورود امنیتی ادمین (احراز هویت دو فاکتوره: نام کاربری و کلمه عبور) -->
        <div v-if="!isAuthenticated" class="min-h-screen flex items-center justify-center p-4 bg-slate-900">
            <div class="max-w-md w-full bg-white rounded-3xl p-8 shadow-2xl space-y-6 text-center border border-slate-100">
                <img src="/logo.png" alt="کافی نت لیمو" class="h-20 mx-auto object-contain">
                <div>
                    <h1 class="text-xl font-black text-slate-800">سامانه مدیریت جامع کافی‌نت لیمو</h1>
                    <p class="text-xs text-slate-500 mt-1">جهت دسترسی به مرکز مدیریت، نام کاربری و رمز عبور خود را وارد نمایید.</p>
                </div>
                <form @submit.prevent="login" class="space-y-4 text-right">
                    <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">نام کاربری مدیریت:</label>
                        <input v-model="adminUsernameInput" type="text" placeholder="نام کاربری مدیریت (مثال: admin)" autocomplete="username" required
                            class="w-full px-4 py-3 border border-slate-300 rounded-xl text-sm focus:outline-none focus:border-limo-500 focus:ring-2 focus:ring-limo-100 transition text-left font-mono">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">رمز عبور مدیریت:</label>
                        <input v-model="adminPasswordInput" type="password" placeholder="رمز عبور مدیریت" autocomplete="current-password" required
                            class="w-full px-4 py-3 border border-slate-300 rounded-xl text-sm focus:outline-none focus:border-limo-500 focus:ring-2 focus:ring-limo-100 transition text-left font-mono">
                    </div>
                    <div v-if="authError" class="p-3 bg-red-50 text-red-600 rounded-xl text-xs font-semibold text-center">
                        {{ authError }}
                    </div>
                    <button type="submit" :disabled="isLoading"
                        class="w-full py-3 bg-limo-600 hover:bg-limo-700 text-white font-black rounded-xl text-sm shadow-lg shadow-lime-500/20 transition flex items-center justify-center gap-2">
                        <span v-if="isLoading" class="animate-spin text-base">🔄</span>
                        <span>ورود به داشبورد مدیریت 🔒</span>
                    </button>
                </form>
            </div>
        </div>

        <!-- بدنه اصلی داشبورد با ۹ ماژول -->
        <div v-else class="flex-1 flex flex-col">
            <!-- نوار بالایی هدر -->
            <header class="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
                    <div class="flex items-center gap-3">
                        <img src="/logo.png" alt="لوگو" class="h-10 w-auto object-contain">
                        <div>
                            <span class="text-sm font-black text-slate-900 block leading-tight">کافی‌نت لیمو</span>
                            <span class="text-[11px] text-slate-500 block">مرکز مدیریت و فرماندهی آنلاین</span>
                        </div>
                    </div>

                    <!-- تب‌های ۹ گانه در دسکتاپ -->
                    <nav class="hidden xl:flex items-center gap-1 bg-slate-100 p-1 rounded-xl text-xs font-bold text-slate-600">
                        <button @click="switchTab('overview')" :class="{'bg-white text-limo-700 shadow-sm': currentTab === 'overview'}" class="px-3 py-2 rounded-lg transition flex items-center gap-1">
                            📊 آمار
                        </button>
                        <button @click="switchTab('customers')" :class="{'bg-white text-limo-700 shadow-sm': currentTab === 'customers'}" class="px-3 py-2 rounded-lg transition flex items-center gap-1">
                            👥 مشتریان
                        </button>
                        <button @click="switchTab('orders')" :class="{'bg-white text-limo-700 shadow-sm': currentTab === 'orders'}" class="px-3 py-2 rounded-lg transition flex items-center gap-1">
                            📂 درخواست‌ها
                            <span v-if="pendingCount > 0" class="bg-amber-500 text-white text-[10px] px-1.5 py-0.2 rounded-full">{{ pendingCount }}</span>
                        </button>
                        <button @click="switchTab('services')" :class="{'bg-white text-limo-700 shadow-sm': currentTab === 'services'}" class="px-3 py-2 rounded-lg transition flex items-center gap-1">
                            📋 خدمات
                        </button>
                        <button @click="switchTab('wallets')" :class="{'bg-white text-limo-700 shadow-sm': currentTab === 'wallets'}" class="px-3 py-2 rounded-lg transition flex items-center gap-1">
                            💳 کیف پول
                        </button>
                        <button @click="switchTab('seasonal')" :class="{'bg-white text-limo-700 shadow-sm': currentTab === 'seasonal'}" class="px-3 py-2 rounded-lg transition flex items-center gap-1">
                            ⏰ ثبت‌نام مقطعی
                        </button>
                        <button @click="switchTab('chats')" :class="{'bg-white text-limo-700 shadow-sm': currentTab === 'chats'}" class="px-3 py-2 rounded-lg transition flex items-center gap-1">
                            💬 چت زنده
                        </button>
                        <button @click="switchTab('channels')" :class="{'bg-white text-limo-700 shadow-sm': currentTab === 'channels'}" class="px-3 py-2 rounded-lg transition flex items-center gap-1">
                            📢 راه‌های ارتباطی
                        </button>
                        <button @click="switchTab('settings')" :class="{'bg-white text-limo-700 shadow-sm': currentTab === 'settings'}" class="px-3 py-2 rounded-lg transition flex items-center gap-1">
                            ⚙️ تنظیمات
                        </button>
                        <button @click="switchTab('monitors')" :class="{'bg-white text-limo-700 shadow-sm': currentTab === 'monitors'}" class="px-3 py-2 rounded-lg transition flex items-center gap-1">
                            🌐 پایش
                        </button>
                    </nav>

                    <!-- کنترل‌های سمت چپ -->
                    <div class="flex items-center gap-2">
                        <button @click="refreshCurrentTab" :disabled="isLoading" title="بروزرسانی داده‌ها"
                            class="p-2 text-slate-500 hover:text-limo-600 hover:bg-slate-100 rounded-lg transition">
                            <span :class="{'animate-spin inline-block': isLoading}">🔄</span>
                        </button>
                        <button @click="exportCSV" title="دانلود اکسل سفارش‌ها"
                            class="hidden sm:flex items-center gap-1 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-bold transition">
                            📥 خروجی Excel
                        </button>
                        <button @click="logout" title="خروج از حساب"
                            class="px-3 py-1.5 bg-red-50 hover:bg-red-100 text-red-600 rounded-lg text-xs font-bold transition">
                            خروج
                        </button>
                    </div>
                </div>

                <!-- نوار تب‌ها برای صفحه نمایش متوسط و موبایل (اسکرول افقی) -->
                <div class="xl:hidden flex overflow-x-auto gap-1 p-2 bg-slate-100 text-xs font-bold text-slate-600">
                    <button @click="switchTab('overview')" :class="{'bg-white text-limo-700 shadow-sm': currentTab === 'overview'}" class="px-3 py-1.5 rounded-lg whitespace-nowrap">📊 آمار</button>
                    <button @click="switchTab('customers')" :class="{'bg-white text-limo-700 shadow-sm': currentTab === 'customers'}" class="px-3 py-1.5 rounded-lg whitespace-nowrap">👥 مشتریان</button>
                    <button @click="switchTab('orders')" :class="{'bg-white text-limo-700 shadow-sm': currentTab === 'orders'}" class="px-3 py-1.5 rounded-lg whitespace-nowrap flex items-center gap-1">
                        📂 درخواست‌ها
                        <span v-if="pendingCount > 0" class="bg-amber-500 text-white text-[10px] px-1.5 rounded-full">{{ pendingCount }}</span>
                    </button>
                    <button @click="switchTab('services')" :class="{'bg-white text-limo-700 shadow-sm': currentTab === 'services'}" class="px-3 py-1.5 rounded-lg whitespace-nowrap">📋 خدمات</button>
                    <button @click="switchTab('wallets')" :class="{'bg-white text-limo-700 shadow-sm': currentTab === 'wallets'}" class="px-3 py-1.5 rounded-lg whitespace-nowrap">💳 کیف پول</button>
                    <button @click="switchTab('seasonal')" :class="{'bg-white text-limo-700 shadow-sm': currentTab === 'seasonal'}" class="px-3 py-1.5 rounded-lg whitespace-nowrap">⏰ ثبت‌نام مقطعی</button>
                    <button @click="switchTab('chats')" :class="{'bg-white text-limo-700 shadow-sm': currentTab === 'chats'}" class="px-3 py-1.5 rounded-lg whitespace-nowrap">💬 چت زنده</button>
                    <button @click="switchTab('channels')" :class="{'bg-white text-limo-700 shadow-sm': currentTab === 'channels'}" class="px-3 py-1.5 rounded-lg whitespace-nowrap">📢 ارتباطی</button>
                    <button @click="switchTab('settings')" :class="{'bg-white text-limo-700 shadow-sm': currentTab === 'settings'}" class="px-3 py-1.5 rounded-lg whitespace-nowrap">⚙️ تنظیمات</button>
                    <button @click="switchTab('monitors')" :class="{'bg-white text-limo-700 shadow-sm': currentTab === 'monitors'}" class="px-3 py-1.5 rounded-lg whitespace-nowrap">🌐 پایش</button>
                </div>
            </header>

            <!-- محتوای صفحات تب‌ها -->
            <main class="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 space-y-6">

                <!-- ۱. ماژول داشبورد و آمار (Overview) -->
                <div v-if="currentTab === 'overview'" class="space-y-6">
                    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
                        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
                            <span class="text-xs font-bold text-slate-400 block mb-1">کل سفارش‌ها</span>
                            <span class="text-2xl font-black text-slate-800">{{ stats.total_orders || 0 }}</span>
                        </div>
                        <div class="bg-white p-5 rounded-2xl border border-amber-200 bg-amber-50/30 shadow-sm">
                            <span class="text-xs font-bold text-amber-600 block mb-1">در انتظار بررسی</span>
                            <span class="text-2xl font-black text-amber-700">{{ stats.pending_orders || 0 }}</span>
                        </div>
                        <div class="bg-white p-5 rounded-2xl border border-blue-200 bg-blue-50/30 shadow-sm">
                            <span class="text-xs font-bold text-blue-600 block mb-1">در دست اقدام</span>
                            <span class="text-2xl font-black text-blue-700">{{ stats.approved_orders || 0 }}</span>
                        </div>
                        <div class="bg-white p-5 rounded-2xl border border-emerald-200 bg-emerald-50/30 shadow-sm">
                            <span class="text-xs font-bold text-emerald-600 block mb-1">تحویل نهایی شده</span>
                            <span class="text-2xl font-black text-emerald-700">{{ stats.completed_orders || 0 }}</span>
                        </div>
                        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
                            <span class="text-xs font-bold text-slate-400 block mb-1">تعداد کل مشتریان</span>
                            <span class="text-2xl font-black text-slate-800">{{ stats.total_users || 0 }}</span>
                        </div>
                    </div>

                    <!-- کارت‌های دسترسی سریع به بخش‌های کلیدی -->
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div @click="switchTab('orders')" class="bg-gradient-to-br from-lime-600 to-lime-800 text-white p-6 rounded-3xl shadow-lg shadow-lime-700/20 cursor-pointer hover:opacity-95 transition">
                            <div class="text-2xl mb-2">📂</div>
                            <h3 class="font-black text-base">مدیریت سفارش‌ها و ثبت‌نام‌ها</h3>
                            <p class="text-xs text-lime-100 mt-1">مشاهده جزییات فرم‌ها، تغییر وضعیت، تخصیص اپراتور و ارسال اعلان پیامکی.</p>
                        </div>
                        <div @click="switchTab('customers')" class="bg-gradient-to-br from-slate-800 to-slate-900 text-white p-6 rounded-3xl shadow-lg shadow-slate-900/20 cursor-pointer hover:opacity-95 transition">
                            <div class="text-2xl mb-2">👥</div>
                            <h3 class="font-black text-base">پرونده مشتریان (CRM Dossier)</h3>
                            <p class="text-xs text-slate-300 mt-1">بررسی سوابق، گردش کیف پول، تیکت‌ها و تاریخچه عملیات هر مشتری.</p>
                        </div>
                        <div @click="switchTab('chats')" class="bg-gradient-to-br from-blue-600 to-blue-800 text-white p-6 rounded-3xl shadow-lg shadow-blue-800/20 cursor-pointer hover:opacity-95 transition">
                            <div class="text-2xl mb-2">💬</div>
                            <h3 class="font-black text-base">مرکز پشتیبانی برخط (Live Chat)</h3>
                            <p class="text-xs text-blue-100 mt-1">پاسخ‌گویی آنی به مکالمات متقاضیان و هدایت تیکت‌های فعال.</p>
                        </div>
                    </div>

                    <!-- خلاصه آخرین سفارش‌ها -->
                    <div class="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4">
                        <div class="flex justify-between items-center">
                            <h3 class="font-black text-sm text-slate-800">آخرین سفارش‌های ثبت‌شده</h3>
                            <button @click="switchTab('orders')" class="text-xs font-bold text-limo-700 hover:underline">مشاهده همه سفارش‌ها ←</button>
                        </div>
                        <div class="overflow-x-auto">
                            <table class="w-full text-right text-xs">
                                <thead>
                                    <tr class="text-slate-400 border-b border-slate-100">
                                        <th class="py-2.5 px-3">کد رهگیری</th>
                                        <th class="py-2.5 px-3">مشتری</th>
                                        <th class="py-2.5 px-3">خدمت</th>
                                        <th class="py-2.5 px-3">وضعیت</th>
                                        <th class="py-2.5 px-3">تاریخ ثبت</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="ord in orders.slice(0, 5)" :key="ord.id" class="border-b border-slate-50 hover:bg-slate-50 transition">
                                        <td class="py-2.5 px-3 font-mono font-bold text-slate-800">{{ ord.tracking_code }}</td>
                                        <td class="py-2.5 px-3 font-semibold">{{ ord.full_name || 'کاربر تلگرام' }}</td>
                                        <td class="py-2.5 px-3 text-slate-600">{{ ord.service_title }}</td>
                                        <td class="py-2.5 px-3">
                                            <span :class="statusBadgeClass(ord.status)" class="px-2 py-0.5 rounded-full text-[10px] font-bold">
                                                {{ statusLabel(ord.status) }}
                                            </span>
                                        </td>
                                        <td class="py-2.5 px-3 text-slate-400 font-mono">{{ formatDate(ord.created_at) }}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- ۲. ماژول مشتریان و پرونده‌ها (CRM & Dossier) -->
                <div v-if="currentTab === 'customers'" class="space-y-4">
                    <div class="flex flex-col sm:flex-row gap-3 justify-between items-center bg-white p-4 rounded-2xl border border-slate-200">
                        <div class="relative w-full sm:w-96">
                            <input v-model="customerSearchQ" @input="debouncedFetchCustomers" type="text"
                                placeholder="جست‌وجوی مشتری (نام، یوزرنیم، شناسه عددی تلگرام)..."
                                class="w-full pl-4 pr-10 py-2.5 border border-slate-200 rounded-xl text-xs focus:outline-none focus:border-limo-500">
                            <span class="absolute right-3 top-2.5 text-slate-400">🔍</span>
                        </div>
                        <div class="text-xs text-slate-500 font-semibold">
                            مجموع مشتریان یافته‌شده: <b class="text-slate-800">{{ customersList.length }}</b>
                        </div>
                    </div>

                    <div class="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
                        <div class="overflow-x-auto">
                            <table class="w-full text-right text-xs">
                                <thead class="bg-slate-50 text-slate-500 font-bold border-b border-slate-100">
                                    <tr>
                                        <th class="py-3 px-4">نام و مشخصات مشتری</th>
                                        <th class="py-3 px-4">شناسه تلگرام</th>
                                        <th class="py-3 px-4">سفارش‌ها (کل / فعال)</th>
                                        <th class="py-3 px-4">موجودی کیف پول</th>
                                        <th class="py-3 px-4">تیکت‌های باز</th>
                                        <th class="py-3 px-4">تاریخ پیوستن</th>
                                        <th class="py-3 px-4 text-center">عملیات پرونده</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-if="isLoadingCustomers" class="text-center py-8">
                                        <td colspan="7" class="py-8 text-slate-400">در حال بارگذاری اطلاعات مشتریان...</td>
                                    </tr>
                                    <tr v-else-if="customersList.length === 0" class="text-center py-8">
                                        <td colspan="7" class="py-8 text-slate-400">هیچ مشتری‌ای مطابق جستجو یافت نشد.</td>
                                    </tr>
                                    <tr v-for="c in customersList" :key="c.id" class="border-b border-slate-50 hover:bg-slate-50 transition">
                                        <td class="py-3 px-4">
                                            <div class="font-bold text-slate-900">{{ c.full_name || 'بی‌نام' }}</div>
                                            <div v-if="c.username" class="text-[10px] text-slate-400 dir-ltr text-right font-mono">@{{ c.username }}</div>
                                        </td>
                                        <td class="py-3 px-4 font-mono text-slate-700">{{ c.telegram_id }}</td>
                                        <td class="py-3 px-4">
                                            <span class="font-bold text-slate-800">{{ c.order_count || 0 }}</span>
                                            <span v-if="c.active_orders_count > 0" class="mr-1 text-[10px] bg-amber-100 text-amber-800 px-1.5 py-0.2 rounded-full font-bold">
                                                {{ c.active_orders_count }} فعال
                                            </span>
                                        </td>
                                        <td class="py-3 px-4 font-mono font-bold" :class="c.wallet_balance > 0 ? 'text-emerald-600' : 'text-slate-400'">
                                            {{ formatTomans(c.wallet_balance) }}
                                        </td>
                                        <td class="py-3 px-4">
                                            <span v-if="c.open_tickets_count > 0" class="bg-blue-100 text-blue-700 font-bold px-2 py-0.5 rounded-full text-[10px]">
                                                {{ c.open_tickets_count }} تیکت
                                            </span>
                                            <span v-else class="text-slate-300">-</span>
                                        </td>
                                        <td class="py-3 px-4 text-slate-400 font-mono">{{ formatDate(c.created_at) }}</td>
                                        <td class="py-3 px-4 text-center">
                                            <button @click="openCustomerDossier(c.id)"
                                                class="px-3 py-1.5 bg-slate-100 hover:bg-limo-100 hover:text-limo-800 text-slate-700 rounded-xl text-xs font-bold transition flex items-center gap-1 mx-auto">
                                                📂 پرونده کامل
                                            </button>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- ۳. ماژول درخواست‌ها و ثبت‌نام‌ها (Orders) -->
                <div v-if="currentTab === 'orders'" class="space-y-4">
                    <div class="flex flex-col md:flex-row gap-3 justify-between items-center bg-white p-4 rounded-2xl border border-slate-200">
                        <div class="flex flex-wrap gap-2 w-full md:w-auto">
                            <select v-model="statusFilter" class="px-3 py-2 border border-slate-200 rounded-xl text-xs bg-slate-50 font-bold">
                                <option value="ALL">همه وضعیت‌ها</option>
                                <option value="PENDING">در انتظار بررسی</option>
                                <option value="APPROVED">تایید و در دست اقدام</option>
                                <option value="NEED_INFO">نقص مدارک</option>
                                <option value="COMPLETED">تکمیل شده</option>
                                <option value="REJECTED">رد شده</option>
                            </select>
                            <input v-model="searchQuery" type="text" placeholder="جستجوی کد رهگیری، نام متقاضی یا شماره..."
                                class="px-4 py-2 border border-slate-200 rounded-xl text-xs flex-1 sm:w-64 focus:outline-none focus:border-limo-500">
                        </div>
                        <div class="text-xs text-slate-500">
                            تعداد سفارش‌ها: <b class="text-slate-800">{{ filteredOrders.length }}</b>
                        </div>
                    </div>

                    <div class="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
                        <div class="overflow-x-auto">
                            <table class="w-full text-right text-xs">
                                <thead class="bg-slate-50 text-slate-500 font-bold border-b border-slate-100">
                                    <tr>
                                        <th class="py-3 px-4">کد رهگیری</th>
                                        <th class="py-3 px-4">متقاضی</th>
                                        <th class="py-3 px-4">عنوان خدمت</th>
                                        <th class="py-3 px-4">وضعیت</th>
                                        <th class="py-3 px-4">تاریخ ثبت</th>
                                        <th class="py-3 px-4">اپراتور / یادداشت</th>
                                        <th class="py-3 px-4 text-center">عملیات</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="ord in filteredOrders" :key="ord.id" class="border-b border-slate-50 hover:bg-slate-50 transition">
                                        <td class="py-3 px-4 font-mono font-bold text-slate-900">{{ ord.tracking_code }}</td>
                                        <td class="py-3 px-4">
                                            <div class="font-bold text-slate-800">{{ ord.full_name || 'کاربر تلگرام' }}</div>
                                            <div class="text-[10px] text-slate-400 font-mono">{{ ord.telegram_id }}</div>
                                        </td>
                                        <td class="py-3 px-4 font-semibold text-slate-700">{{ ord.service_title }}</td>
                                        <td class="py-3 px-4">
                                            <span :class="statusBadgeClass(ord.status)" class="px-2.5 py-0.5 rounded-full text-[10px] font-bold">
                                                {{ statusLabel(ord.status) }}
                                            </span>
                                        </td>
                                        <td class="py-3 px-4 text-slate-400 font-mono">{{ formatDate(ord.created_at) }}</td>
                                        <td class="py-3 px-4 text-slate-500 text-[11px] max-w-xs truncate" :title="ord.operator_notes">
                                            {{ ord.operator_notes || '—' }}
                                        </td>
                                        <td class="py-3 px-4 text-center">
                                            <div class="flex items-center justify-center gap-1.5">
                                                <button @click="openOrderDetail(ord)" class="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg font-bold" title="مشاهده جزییات و وضعیت">
                                                    بررسی 🔍
                                                </button>
                                                <button @click="openAssignModal(ord)" class="px-2.5 py-1 bg-lime-50 hover:bg-lime-100 text-lime-800 rounded-lg font-bold" title="تخصیص اپراتور مسئول">
                                                    تخصیص 👤
                                                </button>
                                                <button @click="openMessageModal(ord)" class="px-2.5 py-1 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg font-bold" title="ارسال پیام تلگرامی">
                                                    پیام 💬
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- ۴. ماژول خدمات، دسته‌ها و فرم‌ها (Services & Forms) -->
                <div v-if="currentTab === 'services'" class="space-y-6">
                    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                        <div>
                            <h2 class="text-base font-black text-slate-800">کاتالوگ رسمی خدمات، تعرفه‌ها و فرم‌ها</h2>
                            <p class="text-xs text-slate-500">مدیریت آنلاین عناوین خدمات، تعرفه‌های پایه، اولویت نمایش، و فعال/غیرفعال‌سازی در سامانه.</p>
                        </div>
                        <div class="flex gap-2">
                            <button @click="openNewServiceModal" class="px-4 py-2 bg-limo-600 hover:bg-limo-700 text-white rounded-xl text-xs font-bold shadow-md shadow-limo-600/20 transition flex items-center gap-1.5">
                                ➕ افزودن خدمت جدید
                            </button>
                            <button @click="openCategoriesModal" class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold transition flex items-center gap-1.5">
                                📁 مدیریت دسته‌ها ({{ catalogCategories.length }})
                            </button>
                        </div>
                    </div>

                    <div class="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
                        <table class="w-full text-right text-xs">
                            <thead class="bg-slate-50 text-slate-500 font-bold border-b border-slate-100">
                                <tr>
                                    <th class="py-3 px-4">کد خدمت</th>
                                    <th class="py-3 px-4">عنوان خدمت</th>
                                    <th class="py-3 px-4">دسته‌بندی</th>
                                    <th class="py-3 px-4">تعرفه پایه</th>
                                    <th class="py-3 px-4">فیلدهای الزامی</th>
                                    <th class="py-3 px-4 text-center">وضعیت خدمت در ربات</th>
                                    <th class="py-3 px-4 text-center">عملیات</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="s in catalogServices" :key="s.id" class="border-b border-slate-50 hover:bg-slate-50 transition">
                                    <td class="py-3 px-4 font-mono font-bold text-slate-700">{{ s.code }}</td>
                                    <td class="py-3 px-4 font-bold text-slate-900">{{ s.title }}</td>
                                    <td class="py-3 px-4 text-slate-600">{{ s.category_title || 'عمومی' }}</td>
                                    <td class="py-3 px-4 font-mono font-bold text-slate-800">{{ formatTomans(s.base_fee) }}</td>
                                    <td class="py-3 px-4">
                                        <button @click="showServiceFields(s)" class="text-limo-700 underline font-bold">
                                            {{ Object.keys(s.required_fields || {}).length }} فیلد فرم
                                        </button>
                                    </td>
                                    <td class="py-3 px-4 text-center">
                                        <button @click="toggleServiceActive(s)"
                                            :class="s.is_active ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'"
                                            class="px-3 py-1 rounded-full text-[11px] font-bold transition">
                                            {{ s.is_active ? '✅ فعال در ربات' : '⛔️ غیرفعال' }}
                                        </button>
                                    </td>
                                    <td class="py-3 px-4 text-center">
                                        <button @click="editService(s)" class="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-bold transition">
                                            ویرایش ✏️
                                        </button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- ۵. ماژول کیف پول و تراکنش‌ها (Wallets & Ledger) -->
                <div v-if="currentTab === 'wallets'" class="space-y-6">
                    <div class="flex justify-between items-center">
                        <div>
                            <h2 class="text-base font-black text-slate-800">سامانه مالی، کیف پول‌ها و دفتر کل تراکنش‌ها</h2>
                            <p class="text-xs text-slate-500">مشاهده موجودی مشتریان، اعمال شارژ یا تعدیل دستی و بررسی گردش حساب با شناسه یکتا.</p>
                        </div>
                    </div>

                    <!-- جدول کیف پول‌های کاربران -->
                    <div class="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
                        <div class="p-4 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                            <h3 class="font-bold text-xs text-slate-700">فهرست کیف پول‌های فعال مشتریان</h3>
                        </div>
                        <div class="overflow-x-auto">
                            <table class="w-full text-right text-xs">
                                <thead class="bg-slate-50 text-slate-400 font-bold border-b border-slate-100">
                                    <tr>
                                        <th class="py-2.5 px-4">نام مشتری</th>
                                        <th class="py-2.5 px-4">شناسه تلگرام</th>
                                        <th class="py-2.5 px-4">موجودی (ریال / تومان)</th>
                                        <th class="py-2.5 px-4">تعداد تراکنش</th>
                                        <th class="py-2.5 px-4">وضعیت</th>
                                        <th class="py-2.5 px-4 text-center">عملیات مالی</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="w in adminWallets" :key="w.id" class="border-b border-slate-50 hover:bg-slate-50 transition">
                                        <td class="py-3 px-4 font-bold text-slate-900">{{ w.full_name || 'کاربر' }}</td>
                                        <td class="py-3 px-4 font-mono text-slate-600">{{ w.telegram_id }}</td>
                                        <td class="py-3 px-4 font-mono font-bold text-emerald-700">{{ formatTomans(w.balance) }}</td>
                                        <td class="py-3 px-4 font-mono">{{ w.tx_count || 0 }}</td>
                                        <td class="py-3 px-4">
                                            <span :class="w.is_frozen ? 'bg-rose-100 text-rose-800' : 'bg-emerald-100 text-emerald-800'" class="px-2 py-0.5 rounded-full text-[10px] font-bold">
                                                {{ w.is_frozen ? 'مسدود' : 'فعال' }}
                                            </span>
                                        </td>
                                        <td class="py-3 px-4 text-center">
                                            <div class="flex items-center justify-center gap-1.5">
                                                <button @click="openAdjustModal(w)" class="px-2.5 py-1 bg-lime-50 hover:bg-lime-100 text-lime-800 rounded-lg font-bold">
                                                    تعدیل / شارژ 💳
                                                </button>
                                                <button @click="toggleFreezeWallet(w)" :class="w.is_frozen ? 'bg-emerald-50 text-emerald-800' : 'bg-rose-50 text-rose-800'" class="px-2.5 py-1 rounded-lg font-bold">
                                                    {{ w.is_frozen ? 'رفع مسدودی' : 'مسدودسازی' }}
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- جدول گردش تراکنش‌های اخیر (Financial Ledger) -->
                    <div class="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
                        <div class="p-4 border-b border-slate-100 bg-slate-50/50">
                            <h3 class="font-bold text-xs text-slate-700">دفتر کل تراکنش‌های ثبت‌شده اخیر</h3>
                        </div>
                        <div class="overflow-x-auto">
                            <table class="w-full text-right text-xs">
                                <thead class="bg-slate-50 text-slate-400 font-bold border-b border-slate-100">
                                    <tr>
                                        <th class="py-2.5 px-4">شناسه پیگیری (Ref)</th>
                                        <th class="py-2.5 px-4">مشتری</th>
                                        <th class="py-2.5 px-4">مبلغ (تومان)</th>
                                        <th class="py-2.5 px-4">نوع تراکنش</th>
                                        <th class="py-2.5 px-4">وضعیت</th>
                                        <th class="py-2.5 px-4">شرح تراکنش</th>
                                        <th class="py-2.5 px-4">تاریخ ثبت</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="tx in adminTransactions" :key="tx.id" class="border-b border-slate-50 hover:bg-slate-50 transition">
                                        <td class="py-2.5 px-4 font-mono font-bold text-slate-800">{{ tx.tracking_ref }}</td>
                                        <td class="py-2.5 px-4">{{ tx.full_name || 'کاربر' }}</td>
                                        <td class="py-2.5 px-4 font-mono font-bold" :class="tx.amount >= 0 ? 'text-emerald-600' : 'text-rose-600'">
                                            {{ tx.amount >= 0 ? '+' : '' }}{{ formatTomans(tx.amount) }}
                                        </td>
                                        <td class="py-2.5 px-4 font-semibold text-slate-600">{{ tx.transaction_type }}</td>
                                        <td class="py-2.5 px-4">
                                            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700">
                                                {{ tx.status }}
                                            </span>
                                        </td>
                                        <td class="py-2.5 px-4 text-slate-500">{{ tx.notes || '—' }}</td>
                                        <td class="py-2.5 px-4 font-mono text-slate-400">{{ formatDate(tx.created_at) }}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- ۶. ماژول ثبت‌نام‌های مقطعی (Seasonal Campaigns) -->
                <div v-if="currentTab === 'seasonal'" class="space-y-6">
                    <div class="flex justify-between items-center">
                        <div>
                            <h2 class="text-base font-black text-slate-800">مدیریت ثبت‌نام‌های مقطعی و دوره‌ای</h2>
                            <p class="text-xs text-slate-500">کنترل زمان‌بندی، مهلت‌های ثبت‌نام آزمون‌ها و خدمات فصلی با تقویم تهران.</p>
                        </div>
                        <button @click="openNewCampaignModal" class="px-4 py-2 bg-limo-600 hover:bg-limo-700 text-white rounded-xl text-xs font-bold shadow-md shadow-limo-600/20 transition flex items-center gap-1.5">
                            ➕ ثبت‌نام جدید
                        </button>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <div v-for="c in campaigns" :key="c.id" class="bg-white rounded-3xl p-5 border border-slate-200 shadow-sm space-y-3">
                            <div class="flex justify-between items-start">
                                <div>
                                    <h3 class="font-bold text-sm text-slate-900">{{ c.title }}</h3>
                                    <span class="text-[10px] font-mono text-slate-400">{{ c.code }}</span>
                                </div>
                                <span :class="seasonalBadgeClass(c.dynamic_status)" class="px-2 py-0.5 rounded-full text-[10px] font-bold">
                                    {{ seasonalStatusLabel(c.dynamic_status) }}
                                </span>
                            </div>
                            <p class="text-xs text-slate-500 line-clamp-2">{{ c.description }}</p>
                            <div class="text-[11px] bg-slate-50 p-2.5 rounded-xl border border-slate-100 space-y-1">
                                <div class="flex justify-between"><span class="text-slate-400">آغاز:</span> <b class="font-mono">{{ formatDate(c.start_at) }}</b></div>
                                <div class="flex justify-between"><span class="text-slate-400">پایان:</span> <b class="font-mono text-rose-600">{{ formatDate(c.end_at) }}</b></div>
                            </div>
                            <div class="flex justify-between items-center pt-2 border-t border-slate-100">
                                <button @click="toggleSeasonalActive(c)" :class="c.is_active ? 'text-amber-600' : 'text-emerald-600'" class="text-xs font-bold hover:underline">
                                    {{ c.is_active ? 'توقف ثبت‌نام' : 'فعال‌سازی مجدد' }}
                                </button>
                                <div class="flex items-center gap-2">
                                    <button @click="openBroadcastModal(c)" class="text-xs font-bold text-amber-700 hover:text-amber-900">
                                        اطلاعیه 📢
                                    </button>
                                    <button @click="editCampaign(c)" class="text-xs font-bold text-slate-600 hover:text-slate-900">
                                        ویرایش ✏️
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- ۷. ماژول چت و پشتیبانی زنده (Support Live Chat) -->
                <div v-if="currentTab === 'chats'" class="space-y-4">
                    <div class="bg-white rounded-3xl border border-slate-200 shadow-sm grid grid-cols-1 lg:grid-cols-3 min-h-[600px] overflow-hidden">
                        <!-- ستون راست: لیست تیکت‌ها -->
                        <div class="border-l border-slate-200 flex flex-col">
                            <div class="p-3 border-b border-slate-200 bg-slate-50/50">
                                <select v-model="supportFilter" class="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs bg-white font-bold">
                                    <option value="ALL">همه گفتگوها</option>
                                    <option value="NEW">جدید (بدون پاسخ)</option>
                                    <option value="PENDING_SUPPORT">در انتظار پاسخ پشتیبان</option>
                                    <option value="PENDING_CUSTOMER">در انتظار پاسخ کاربر</option>
                                    <option value="CLOSED">بسته شده</option>
                                </select>
                            </div>
                            <div class="flex-1 overflow-y-auto divide-y divide-slate-100 max-h-[550px]">
                                <div v-for="th in filteredSupportThreads" :key="th.id"
                                    @click="selectThread(th)"
                                    :class="{'bg-lime-50/60': selectedThread && selectedThread.id === th.id}"
                                    class="p-4 hover:bg-slate-50 cursor-pointer transition space-y-1">
                                    <div class="flex justify-between items-center">
                                        <b class="text-xs text-slate-900">{{ th.full_name || 'کاربر تلگرام' }}</b>
                                        <span :class="supportStatusBadgeClass(th.status)" class="px-2 py-0.5 rounded-full text-[9px] font-bold">
                                            {{ supportStatusLabel(th.status) }}
                                        </span>
                                    </div>
                                    <p class="text-[11px] text-slate-500 truncate">{{ th.last_message || 'مکالمه آغاز شده' }}</p>
                                    <div class="flex justify-between text-[10px] text-slate-400 font-mono">
                                        <span>پیام‌ها: {{ th.message_count }}</span>
                                        <span>{{ formatDate(th.updated_at) }}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- ستون چپ: صفحه چت و پاسخگویی -->
                        <div class="lg:col-span-2 flex flex-col bg-slate-50/30">
                            <div v-if="selectedThread" class="flex-1 flex flex-col h-full">
                                <div class="p-4 bg-white border-b border-slate-200 flex justify-between items-center">
                                    <div>
                                        <h3 class="font-black text-xs text-slate-900">{{ selectedThread.full_name }}</h3>
                                        <span class="text-[10px] text-slate-400 font-mono">{{ selectedThread.telegram_id }}</span>
                                    </div>
                                    <div class="flex gap-2">
                                        <button v-if="selectedThread.status !== 'CLOSED'" @click="changeThreadStatus('CLOSED')" class="px-3 py-1 bg-slate-100 hover:bg-rose-50 text-rose-700 rounded-lg text-xs font-bold transition">
                                            بستن تیکت ✕
                                        </button>
                                        <button v-else @click="changeThreadStatus('PENDING_CUSTOMER')" class="px-3 py-1 bg-lime-100 hover:bg-lime-200 text-lime-800 rounded-lg text-xs font-bold transition">
                                            بازگشایی مجدد ↺
                                        </button>
                                    </div>
                                </div>

                                <!-- پیام‌ها -->
                                <div class="flex-1 p-4 overflow-y-auto space-y-3 max-h-[440px]">
                                    <div v-for="m in currentThreadMessages" :key="m.id"
                                        :class="m.sender_role === 'OPERATOR' ? 'mr-auto text-left' : 'ml-auto text-right'"
                                        class="max-w-[75%]">
                                        <div :class="m.sender_role === 'OPERATOR' ? 'bg-slate-800 text-white rounded-2xl rounded-bl-none' : 'bg-white border border-slate-200 text-slate-800 rounded-2xl rounded-br-none'"
                                            class="p-3 text-xs shadow-sm space-y-1">
                                            <div class="text-[10px] opacity-70 font-bold mb-1">
                                                {{ m.sender_role === 'OPERATOR' ? 'اپراتور کافی‌نت لیمو' : selectedThread.full_name }}
                                            </div>
                                            <p class="whitespace-pre-line leading-relaxed">{{ m.message_text }}</p>
                                            <div class="text-[9px] opacity-60 font-mono text-left pt-1">{{ formatDate(m.created_at) }}</div>
                                        </div>
                                    </div>
                                </div>

                                <!-- کادر پاسخ اپراتور -->
                                <div class="p-3 bg-white border-t border-slate-200 flex gap-2">
                                    <textarea v-model="supportReplyText" rows="2" placeholder="پاسخ خود را برای متقاضی بنویسید (بلافاصله به تلگرام کاربر ارسال می‌شود)..."
                                        class="flex-1 p-2.5 border border-slate-200 rounded-xl text-xs focus:outline-none focus:border-limo-500"></textarea>
                                    <button @click="sendSupportReply" :disabled="!supportReplyText || isSendingSupportReply"
                                        class="px-5 py-2 bg-limo-600 hover:bg-limo-700 text-white rounded-xl text-xs font-bold transition flex items-center justify-center">
                                        <span v-if="isSendingSupportReply">...</span>
                                        <span v-else>ارسال 🚀</span>
                                    </button>
                                </div>
                            </div>
                            <div v-else class="flex-1 flex items-center justify-center text-slate-400 text-xs p-8">
                                لطفاً یک گفتگو را از ستون راست انتخاب فرمایید.
                            </div>
                        </div>
                    </div>
                </div>

                <!-- ۸. ماژول راه‌های ارتباطی (Communication Channels) -->
                <div v-if="currentTab === 'channels'" class="space-y-6">
                    <div class="flex justify-between items-center">
                        <div>
                            <h2 class="text-base font-black text-slate-800">راه‌های ارتباطی و شبکه‌های اجتماعی کافی‌نت</h2>
                            <p class="text-xs text-slate-500">هرگونه تغییر در این بخش، بلافاصله در پیام "راه‌های ارتباطی" ربات تلگرام منعکس می‌گردد.</p>
                        </div>
                    </div>

                    <div class="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
                        <table class="w-full text-right text-xs">
                            <thead class="bg-slate-50 text-slate-500 font-bold border-b border-slate-100">
                                <tr>
                                    <th class="py-3 px-4">کلید سامانه</th>
                                    <th class="py-3 px-4">عنوان نمایشی</th>
                                    <th class="py-3 px-4">مقدار / آدرس / شماره تماس</th>
                                    <th class="py-3 px-4">وضعیت نمایش در ربات</th>
                                    <th class="py-3 px-4 text-center">ویرایش</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="ch in communicationChannels" :key="ch.id" class="border-b border-slate-50 hover:bg-slate-50 transition">
                                    <td class="py-3 px-4 font-mono font-bold text-slate-700">{{ ch.key }}</td>
                                    <td class="py-3 px-4 font-bold text-slate-900">{{ ch.title }}</td>
                                    <td class="py-3 px-4 font-mono dir-ltr text-right text-slate-700">{{ ch.value || 'تنظیم‌نشده' }}</td>
                                    <td class="py-3 px-4">
                                        <span :class="ch.is_active ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'" class="px-2.5 py-0.5 rounded-full text-[10px] font-bold">
                                            {{ ch.is_active ? 'فعال در بات' : 'مخفی' }}
                                        </span>
                                    </td>
                                    <td class="py-3 px-4 text-center">
                                        <button @click="openChannelEdit(ch)" class="px-3 py-1 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-lg font-bold">
                                            ویرایش ✏️
                                        </button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- ۹. ماژول تنظیمات، سطوح دسترسی و لاگ‌های سیستم (Settings & Audit Logs) -->
                <div v-if="currentTab === 'settings'" class="space-y-6">
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <!-- بخش تنظیمات حساب بانکی و پرداخت -->
                        <div class="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4">
                            <div class="flex justify-between items-center">
                                <h3 class="font-black text-sm text-slate-800">💳 اطلاعات حساب بانکی و کارت واریز</h3>
                                <span class="text-[11px] text-emerald-600 font-bold">نمایش پویا در مینی‌اپ</span>
                            </div>
                            <p class="text-xs text-slate-500 leading-relaxed">
                                اطلاعات کارت بانکی زیر به صورت خودکار در تب پرداخت مینی‌اپلیکیشن به متقاضیان نمایش داده می‌شود:
                            </p>
                            <div class="space-y-3 text-xs">
                                <div>
                                    <label class="block font-bold text-slate-700 mb-1">شماره کارت اختصاصی (۱۶ رقمی):</label>
                                    <input v-model="settingCardNumber" type="text" placeholder="مثال: 6037991812345678"
                                        class="w-full px-3 py-2 border border-slate-200 rounded-xl font-mono text-center font-bold">
                                </div>
                                <div>
                                    <label class="block font-bold text-slate-700 mb-1">نام صاحب حساب:</label>
                                    <input v-model="settingCardOwner" type="text" placeholder="مثال: مدیریت کافی نت لیمو"
                                        class="w-full px-3 py-2 border border-slate-200 rounded-xl font-bold">
                                </div>
                                <div>
                                    <label class="block font-bold text-slate-700 mb-1">شماره همراه پشتیبانی مستقیم:</label>
                                    <input v-model="settingSupportPhone" type="text" placeholder="مثال: 09123456789"
                                        class="w-full px-3 py-2 border border-slate-200 rounded-xl font-mono">
                                </div>
                                <button @click="saveBankSettings" :disabled="isSavingBank"
                                    class="w-full py-2.5 bg-limo-600 hover:bg-limo-700 text-white rounded-xl font-bold shadow-sm transition">
                                    {{ isSavingBank ? 'در حال ذخیره...' : 'ذخیره مشخصات حساب بانکی' }}
                                </button>
                            </div>
                        </div>

                        <!-- بخش تنظیم هزینه تامین شاهد مسکن -->
                        <div class="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4">
                            <h3 class="font-black text-sm text-slate-800">تنظیمات خدمت کد رهگیری مسکن (شاهدان)</h3>
                            <p class="text-xs text-slate-500 leading-relaxed">
                                طبق ضوابط مصوب، متقاضی می‌تواند درخواست تأمین دو شاهد رسمی توسط کافی‌نت لیمو را انتخاب نماید. تعرفه مصوب این خدمت در زیر تنظیم و مدیریت می‌شود:
                            </p>
                            <div class="space-y-2">
                                <label class="block text-xs font-bold text-slate-700">هزینه تأمین شاهد رسمی (به ریال):</label>
                                <div class="flex gap-2">
                                    <input v-model.number="witnessProvisionFee" type="number"
                                        class="flex-1 px-4 py-2.5 border border-slate-200 rounded-xl text-xs font-mono font-bold focus:outline-none focus:border-limo-500">
                                    <button @click="saveWitnessFee" :disabled="isSavingSetting"
                                        class="px-5 py-2.5 bg-limo-600 hover:bg-limo-700 text-white rounded-xl text-xs font-bold transition">
                                        ذخیره تعرفه
                                    </button>
                                </div>
                                <div class="text-[11px] text-slate-400">
                                    معادل: <b class="font-mono text-slate-700">{{ formatTomans(witnessProvisionFee) }}</b>
                                </div>
                            </div>
                        </div>

                        <!-- راهنمای نقش‌ها و تفکیک دسترسی (RBAC) -->
                        <div class="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-3">
                            <h3 class="font-black text-sm text-slate-800">سطوح دسترسی و تفکیک نقش‌ها (RBAC)</h3>
                            <div class="space-y-2 text-xs">
                                <div class="p-3 bg-slate-50 rounded-xl border border-slate-100">
                                    <b class="text-slate-800">👑 مدیر کل سیستم (Super Admin):</b>
                                    <p class="text-slate-500 text-[11px] mt-0.5">دسترسی جامع به امور مالی، تنظیمات سامانه، کاتالوگ خدمات، کاربران و مانیتورینگ.</p>
                                </div>
                                <div class="p-3 bg-slate-50 rounded-xl border border-slate-100">
                                    <b class="text-slate-800">👔 کارشناس ارشد (Senior Operator):</b>
                                    <p class="text-slate-500 text-[11px] mt-0.5">بررسی پرونده‌ها، تخصیص پرونده به اپراتور، تغییر وضعیت سفارشات و ارسال پیام به مشتری.</p>
                                </div>
                                <div class="p-3 bg-slate-50 rounded-xl border border-slate-100">
                                    <b class="text-slate-800">🎧 کارشناس پشتیبانی (Support Agent):</b>
                                    <p class="text-slate-500 text-[11px] mt-0.5">پاسخگویی به گفت‌وگوهای زنده متقاضیان و رفع اشکال اولیه.</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- جدول تاریخچه لاگ‌های حسابرسی سیستم (System Audit Logs) -->
                    <div class="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
                        <div class="p-4 border-b border-slate-100 bg-slate-50/50">
                            <h3 class="font-bold text-xs text-slate-700">تاریخچه تغییر وضعیت و عملیات اپراتورها (Order Audit Logs)</h3>
                        </div>
                        <div class="overflow-x-auto">
                            <table class="w-full text-right text-xs">
                                <thead class="bg-slate-50 text-slate-400 font-bold border-b border-slate-100">
                                    <tr>
                                        <th class="py-2.5 px-4">کد سفارش</th>
                                        <th class="py-2.5 px-4">شناسه اقدام‌کننده (Actor)</th>
                                        <th class="py-2.5 px-4">تغییر وضعیت</th>
                                        <th class="py-2.5 px-4">شرح / یادداشت اپراتور</th>
                                        <th class="py-2.5 px-4">زمان ثبت رویداد</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="log in systemAuditLogs" :key="log.id" class="border-b border-slate-50 hover:bg-slate-50 transition">
                                        <td class="py-2.5 px-4 font-mono font-bold text-slate-800">{{ log.tracking_code || log.order_id }}</td>
                                        <td class="py-2.5 px-4 font-mono text-slate-500">{{ log.actor_id }}</td>
                                        <td class="py-2.5 px-4">
                                            <span class="font-mono text-slate-400">{{ log.from_status }}</span>
                                            <span class="mx-1 text-slate-300">→</span>
                                            <span :class="statusBadgeClass(log.to_status)" class="px-2 py-0.5 rounded-full text-[10px] font-bold">
                                                {{ statusLabel(log.to_status) }}
                                            </span>
                                        </td>
                                        <td class="py-2.5 px-4 text-slate-700">{{ log.note || '—' }}</td>
                                        <td class="py-2.5 px-4 font-mono text-slate-400">{{ formatDate(log.created_at) }}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- ۱۰. ماژول پایش هوشمند سامانه‌ها (Website Monitors) -->
                <div v-if="currentTab === 'monitors'" class="space-y-4">
                    <div class="flex justify-between items-center bg-white p-4 rounded-2xl border border-slate-200">
                        <div>
                            <h2 class="text-sm font-black text-slate-800">پایش هوشمند سامانه‌های مرجع</h2>
                            <p class="text-xs text-slate-500">تفکیک دوگانه: پایش سرور (Uptime) و پایش باز بودن خدمت (Service Status)</p>
                        </div>
                        <button @click="checkAllMonitorsNow" :disabled="isCheckingMonitors"
                            class="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold transition flex items-center gap-1.5 shadow-sm">
                            <span :class="{'animate-spin': isCheckingMonitors}">🔄</span>
                            <span>بررسی فوری سامانه‌ها</span>
                        </button>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <div v-for="m in monitors" :key="m.id" class="bg-white rounded-3xl p-5 border border-slate-200 shadow-sm space-y-3">
                            <div class="flex justify-between items-start">
                                <h3 class="font-bold text-xs text-slate-800 leading-snug">{{ m.title }}</h3>
                                <span :class="m.is_available ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'" class="px-2 py-0.5 rounded-full text-[10px] font-bold whitespace-nowrap">
                                    {{ m.is_available ? 'سرور آنلاین' : 'سرور قطع' }}
                                </span>
                            </div>
                            <div class="text-[11px] text-slate-400 font-mono truncate" :title="m.target_url">{{ m.target_url }}</div>
                            <div class="text-xs bg-slate-50 p-3 rounded-2xl border border-slate-100 space-y-1.5">
                                <div class="flex justify-between">
                                    <span class="text-slate-400">کد HTTP آخرین پاسخ:</span>
                                    <b class="font-mono text-slate-700">{{ m.last_status_code || '-' }}</b>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-slate-400">آخرین پایش:</span>
                                    <b class="font-mono text-slate-700">{{ formatDate(m.last_checked_at) }}</b>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

            </main>
        </div>

        <!-- مودال ۱: پرونده جامع مشتری (Customer Dossier Modal) -->
        <div v-if="selectedDossier" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
            <div class="bg-white rounded-3xl max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl border border-slate-100 text-right overflow-hidden">
                <!-- سربرگ مودال پرونده -->
                <div class="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                    <div>
                        <div class="flex items-center gap-2">
                            <h3 class="font-black text-base text-slate-900">پرونده مشتری: {{ selectedDossier.user.full_name }}</h3>
                            <span class="text-[10px] bg-slate-200 text-slate-700 px-2 py-0.5 rounded-full font-bold">{{ selectedDossier.user.role }}</span>
                        </div>
                        <div class="text-xs text-slate-500 mt-1">شناسه تلگرام: <code class="font-mono text-slate-800">{{ selectedDossier.user.telegram_id }}</code> | عضویت: {{ formatDate(selectedDossier.user.created_at) }}</div>
                    </div>
                    <button @click="selectedDossier = null" class="p-2 text-slate-400 hover:text-slate-600 rounded-lg">✕</button>
                </div>

                <!-- وضعیت مالی مشتری در بالای پرونده -->
                <div class="px-6 py-3 bg-emerald-50/50 border-b border-emerald-100/50 flex justify-between items-center text-xs">
                    <div>
                        <span class="text-slate-500">موجودی کیف پول:</span>
                        <b class="font-mono text-sm text-emerald-800 mr-2">{{ formatTomans(selectedDossier.wallet.balance) }}</b>
                    </div>
                    <span :class="selectedDossier.wallet.is_frozen ? 'bg-rose-100 text-rose-800' : 'bg-emerald-100 text-emerald-800'" class="px-2 py-0.5 rounded-full text-[10px] font-bold">
                        {{ selectedDossier.wallet.is_frozen ? 'کیف پول مسدود است' : 'کیف پول فعال است' }}
                    </span>
                </div>

                <!-- تب‌های داخلی پرونده مشتری -->
                <div class="flex border-b border-slate-100 px-6 gap-4 text-xs font-bold text-slate-500 bg-white">
                    <button @click="dossierTab = 'orders'" :class="{'text-limo-700 border-b-2 border-limo-600 py-3': dossierTab === 'orders'}" class="py-3 transition">
                        سفارش‌ها ({{ selectedDossier.orders.length }})
                    </button>
                    <button @click="dossierTab = 'transactions'" :class="{'text-limo-700 border-b-2 border-limo-600 py-3': dossierTab === 'transactions'}" class="py-3 transition">
                        تراکنش‌های مالی ({{ selectedDossier.transactions.length }})
                    </button>
                    <button @click="dossierTab = 'threads'" :class="{'text-limo-700 border-b-2 border-limo-600 py-3': dossierTab === 'threads'}" class="py-3 transition">
                        گفتگوهای پشتیبانی ({{ selectedDossier.support_threads.length }})
                    </button>
                    <button @click="dossierTab = 'logs'" :class="{'text-limo-700 border-b-2 border-limo-600 py-3': dossierTab === 'logs'}" class="py-3 transition">
                        لاگ‌های حسابرسی پرونده ({{ selectedDossier.audit_logs.length }})
                    </button>
                </div>

                <!-- محتوای تب‌های پرونده -->
                <div class="p-6 overflow-y-auto flex-1 space-y-4">
                    <!-- تب سفارش‌های پرونده -->
                    <div v-if="dossierTab === 'orders'" class="space-y-3">
                        <div v-if="selectedDossier.orders.length === 0" class="text-center py-8 text-slate-400 text-xs">سفارشی برای این مشتری ثبت نشده است.</div>
                        <div v-for="ord in selectedDossier.orders" :key="ord.id" class="p-4 bg-slate-50 rounded-2xl border border-slate-200 text-xs space-y-2">
                            <div class="flex justify-between items-center">
                                <b class="font-mono text-slate-900">{{ ord.tracking_code }} - {{ ord.service_title }}</b>
                                <span :class="statusBadgeClass(ord.status)" class="px-2 py-0.5 rounded-full text-[10px] font-bold">{{ statusLabel(ord.status) }}</span>
                            </div>
                            <div class="text-[11px] text-slate-500">یادداشت اپراتور: {{ ord.operator_notes || 'ندارد' }}</div>
                            <div class="text-[10px] text-slate-400 font-mono">ثبت: {{ formatDate(ord.created_at) }}</div>
                        </div>
                    </div>

                    <!-- تب تراکنش‌های پرونده -->
                    <div v-if="dossierTab === 'transactions'" class="space-y-3">
                        <div v-if="selectedDossier.transactions.length === 0" class="text-center py-8 text-slate-400 text-xs">تراکنشی ثبت نشده است.</div>
                        <div v-for="tx in selectedDossier.transactions" :key="tx.id" class="p-3 bg-slate-50 rounded-xl border border-slate-100 text-xs flex justify-between items-center">
                            <div>
                                <b class="font-mono text-slate-800">{{ tx.tracking_ref }}</b>
                                <div class="text-[11px] text-slate-500">{{ tx.notes }}</div>
                            </div>
                            <div class="text-left font-mono">
                                <span :class="tx.amount >= 0 ? 'text-emerald-700' : 'text-rose-700'" class="font-bold block">
                                    {{ tx.amount >= 0 ? '+' : '' }}{{ formatTomans(tx.amount) }}
                                </span>
                                <span class="text-[10px] text-slate-400">{{ formatDate(tx.created_at) }}</span>
                            </div>
                        </div>
                    </div>

                    <!-- تب چت‌های پرونده -->
                    <div v-if="dossierTab === 'threads'" class="space-y-3">
                        <div v-if="selectedDossier.support_threads.length === 0" class="text-center py-8 text-slate-400 text-xs">تیکتی ثبت نشده است.</div>
                        <div v-for="th in selectedDossier.support_threads" :key="th.id" class="p-3 bg-slate-50 rounded-xl border border-slate-100 text-xs flex justify-between items-center">
                            <div>
                                <b class="text-slate-800">تیکت #{{ th.id }}</b>
                                <div class="text-[10px] text-slate-400 font-mono">پیام‌ها: {{ th.message_count }}</div>
                            </div>
                            <span :class="supportStatusBadgeClass(th.status)" class="px-2 py-0.5 rounded-full text-[10px] font-bold">{{ supportStatusLabel(th.status) }}</span>
                        </div>
                    </div>

                    <!-- تب لاگ‌های حسابرسی پرونده -->
                    <div v-if="dossierTab === 'logs'" class="space-y-3">
                        <div v-if="selectedDossier.audit_logs.length === 0" class="text-center py-8 text-slate-400 text-xs">لاگ حسابرسی‌ای ثبت نشده است.</div>
                        <div v-for="l in selectedDossier.audit_logs" :key="l.id" class="p-3 bg-slate-50 rounded-xl border border-slate-100 text-xs space-y-1">
                            <div class="flex justify-between font-mono text-slate-600">
                                <b>سفارش: {{ l.tracking_code || l.order_id }}</b>
                                <span class="text-[10px] text-slate-400">{{ formatDate(l.created_at) }}</span>
                            </div>
                            <div class="text-[11px] text-slate-700">{{ l.note }}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- مودال ۲: جزییات سفارش و تغییر وضعیت -->
        <div v-if="selectedOrder" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
            <div class="bg-white rounded-3xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 space-y-5 shadow-2xl border border-slate-100 text-right">
                <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                    <div>
                        <h3 class="font-black text-base text-slate-900">پرونده سفارش {{ selectedOrder.tracking_code }}</h3>
                        <span class="text-xs text-slate-500">{{ selectedOrder.service_title }}</span>
                    </div>
                    <button @click="selectedOrder = null" class="p-2 text-slate-400 hover:text-slate-600 rounded-lg">✕</button>
                </div>

                <div class="grid grid-cols-2 gap-3 text-xs bg-slate-50 p-4 rounded-2xl border border-slate-100">
                    <div><span class="text-slate-400">نام متقاضی:</span> <b class="text-slate-800">{{ selectedOrder.full_name || 'کاربر تلگرام' }}</b></div>
                    <div><span class="text-slate-400">شناسه تلگرام:</span> <b class="font-mono text-slate-800">{{ selectedOrder.telegram_id }}</b></div>
                    <div><span class="text-slate-400">تاریخ ثبت:</span> <b class="font-mono text-slate-800">{{ formatDate(selectedOrder.created_at) }}</b></div>
                    <div><span class="text-slate-400">وضعیت فعلی:</span> 
                        <span :class="statusBadgeClass(selectedOrder.status)" class="px-2 py-0.5 rounded-full text-[10px] font-bold">
                            {{ statusLabel(selectedOrder.status) }}
                        </span>
                    </div>
                </div>

                <!-- پیش‌نمایش فیش واریز در صورت ارسال توسط متقاضی -->
                <div v-if="parseOrderData(selectedOrder.form_data).receipt" class="p-3 bg-lime-50/70 border border-lime-200 rounded-2xl space-y-2 text-xs">
                    <div class="flex justify-between items-center">
                        <span class="font-bold text-lime-900">💳 فیش واریزی ارسال‌شده:</span>
                        <span v-if="parseOrderData(selectedOrder.form_data).receipt.ref_number" class="text-[11px] font-mono text-slate-600 bg-white px-2 py-0.5 rounded border border-slate-200">
                            شناسه: {{ parseOrderData(selectedOrder.form_data).receipt.ref_number }}
                        </span>
                        <span v-else-if="parseOrderData(selectedOrder.form_data).receipt.file_id" class="text-[11px] font-mono text-purple-700 bg-purple-50 px-2 py-0.5 rounded border border-purple-200">
                            ارسال مستقیم از تلگرام
                        </span>
                    </div>
                    <div v-if="parseOrderData(selectedOrder.form_data).receipt.image" class="text-center py-1">
                        <a :href="parseOrderData(selectedOrder.form_data).receipt.image" target="_blank" title="مشاهده تصویر بزرگ‌تر">
                            <img :src="parseOrderData(selectedOrder.form_data).receipt.image" alt="فیش واریز" class="max-h-56 mx-auto rounded-xl border border-slate-200 shadow-sm object-contain cursor-pointer">
                        </a>
                        <div class="text-[10px] text-slate-400 mt-1">جهت مشاهده با وضوح اصلی روی تصویر کلیک فرمایید</div>
                    </div>
                    <div v-else-if="parseOrderData(selectedOrder.form_data).receipt.file_id" class="p-3 bg-white rounded-xl border border-slate-200 text-center space-y-1">
                        <div class="font-bold text-slate-800">📷 فیش به بات تلگرام مدیر فوروارد شده است.</div>
                        <div class="text-[10px] text-slate-400 font-mono">شناسه تلگرام فایل: {{ parseOrderData(selectedOrder.form_data).receipt.file_id }}</div>
                        <div v-if="parseOrderData(selectedOrder.form_data).receipt.caption" class="text-xs text-slate-600 mt-1">توضیح متقاضی: {{ parseOrderData(selectedOrder.form_data).receipt.caption }}</div>
                    </div>
                    <div class="flex gap-2 pt-1">
                        <button @click="quickApprovePayment" class="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-2 rounded-xl text-xs shadow-sm transition">
                            ✅ تأیید پرداخت
                        </button>
                        <button @click="quickRejectPayment" class="flex-1 bg-rose-600 hover:bg-rose-700 text-white font-bold py-2 rounded-xl text-xs shadow-sm transition">
                            ❌ رد فیش پرداخت
                        </button>
                    </div>
                </div>

                <!-- اطلاعات فیلدهای فرم مرحله‌ای واردشده -->
                <div class="space-y-2">
                    <h4 class="font-bold text-xs text-slate-700">داده‌های ثبت‌شده توسط متقاضی:</h4>
                    <div class="bg-white border border-slate-100 rounded-2xl p-4 space-y-2 text-xs">
                        <div v-for="(val, key) in parseOrderData(selectedOrder.form_data || selectedOrder.data)" :key="key" v-show="key !== 'receipt'" class="flex justify-between border-b border-slate-50 py-1.5 last:border-0">
                            <span class="text-slate-500 font-semibold">{{ formatFieldKey(key) }}:</span>
                            <span class="font-mono font-bold text-slate-900">{{ val }}</span>
                        </div>
                    </div>
                </div>

                <!-- یادداشت‌های داخلی و خروجی پرونده در صورت تکمیل -->
                <div v-if="parseOrderData(selectedOrder.form_data).result_document" class="p-3 bg-emerald-50 border border-emerald-200 rounded-2xl space-y-1 text-xs">
                    <div class="font-bold text-emerald-900">📜 خروجی نهایی تحویل‌شده به متقاضی:</div>
                    <div class="font-mono text-slate-800 bg-white p-2 rounded-xl border border-emerald-100">{{ parseOrderData(selectedOrder.form_data).result_document.text }}</div>
                </div>

                <div v-if="parseOrderData(selectedOrder.form_data).internal_notes" class="p-3 bg-slate-50 border border-slate-200 rounded-2xl space-y-1 text-xs">
                    <div class="font-bold text-slate-700">🔒 یادداشت داخلی و محرمانه متصدی:</div>
                    <div class="text-slate-600">{{ parseOrderData(selectedOrder.form_data).internal_notes }}</div>
                </div>

                <!-- دکمه‌های اقدام سریع متصدی پرونده -->
                <div class="p-3 bg-slate-50 border border-slate-200 rounded-2xl space-y-2 text-xs">
                    <div class="font-bold text-slate-700">⚡️ عملیات سریع متصدی:</div>
                    <div class="grid grid-cols-3 gap-2">
                        <button @click="quickStartProgress" class="py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl text-[11px] shadow-xs transition">
                            ⚙️ شروع اقدام
                        </button>
                        <button @click="quickRequestInfo" class="py-2 bg-amber-600 hover:bg-amber-700 text-white font-bold rounded-xl text-[11px] shadow-xs transition">
                            ⚠️ اعلام نقص مدارک
                        </button>
                        <button @click="quickCompleteOrder" class="py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-[11px] shadow-xs transition">
                            🎉 صدور و تحویل نهایی
                        </button>
                    </div>
                </div>

                <!-- فرم تغییر وضعیت و ارسال پیام خودکار به تلگرام متقاضی -->
                <div class="space-y-3 pt-2 border-t border-slate-100">
                    <h4 class="font-bold text-xs text-slate-700">تغییر وضعیت، یادداشت‌ها و ارسال به متقاضی:</h4>
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div>
                            <label class="block text-[11px] font-semibold text-slate-600 mb-1">وضعیت جدید پرونده:</label>
                            <select v-model="newOrderStatus" class="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs bg-white font-bold">
                                <option value="PENDING">در انتظار پرداخت و ارسال فیش</option>
                                <option value="RECEIPT_SUBMITTED">فیش ارسال‌شده (منتظر تأیید مدیر)</option>
                                <option value="APPROVED">تأیید پرداخت و در صف اقدام</option>
                                <option value="IN_PROGRESS">در حال اقدام توسط کارشناس</option>
                                <option value="NEED_INFO">نقص مدارک و اطلاعات</option>
                                <option value="PAYMENT_REJECTED">رد فیش پرداخت</option>
                                <option value="COMPLETED">تکمیل شده و مختومه</option>
                                <option value="CANCELLED">لغو گردیده</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-[11px] font-semibold text-slate-600 mb-1">یادداشت عمومی (پیام برای مشتری):</label>
                            <input v-model="newOperatorNotes" type="text" placeholder="پیام قابل مشاهده در استپر و تلگرام مشتری..."
                                class="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs">
                        </div>
                    </div>

                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div>
                            <label class="block text-[11px] font-semibold text-slate-600 mb-1">یادداشت داخلی و محرمانه کارشناس (صرفاً در پنل):</label>
                            <input v-model="newInternalNotes" type="text" placeholder="یادداشت محرمانه متصدی یا مدیر..."
                                class="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs">
                        </div>
                        <div v-if="newOrderStatus === 'COMPLETED'">
                            <label class="block text-[11px] font-semibold text-emerald-800 mb-1">متن یا کد رهگیری مدرک صادرشده:</label>
                            <input v-model="resultDocText" type="text" placeholder="مثال: کد رهگیری خودنویس: 9988776655"
                                class="w-full px-3 py-2 border border-emerald-300 bg-emerald-50/50 rounded-xl text-xs font-mono">
                        </div>
                    </div>

                    <div class="flex justify-end gap-2 pt-2">
                        <button @click="updateOrderStatus" :disabled="isUpdatingStatus"
                            class="px-5 py-2.5 bg-limo-600 hover:bg-limo-700 text-white rounded-xl text-xs font-bold shadow-md shadow-limo-600/20 transition">
                            <span v-if="isUpdatingStatus">در حال ثبت...</span>
                            <span v-else>ذخیره وضعیت و ارسال به مشتری</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- مودال ۳: تخصیص اپراتور مسئول به سفارش -->
        <div v-if="assignOrderModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
            <div class="bg-white rounded-3xl max-w-md w-full p-6 space-y-4 shadow-2xl border border-slate-100 text-right">
                <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                    <h3 class="font-black text-sm text-slate-900">تخصیص اپراتور مسئول پرونده</h3>
                    <button @click="assignOrderModal = null" class="text-slate-400 hover:text-slate-600">✕</button>
                </div>
                <div class="text-xs text-slate-500">
                    پرونده: <b class="font-mono text-slate-800">{{ assignOrderModal.tracking_code }}</b> ({{ assignOrderModal.service_title }})
                </div>
                <div class="space-y-3">
                    <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">نام اپراتور مسئول:</label>
                        <input v-model="assignOperatorName" type="text" placeholder="مثال: کارشناس راد / مهندس احمدی"
                            class="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs focus:outline-none focus:border-limo-500">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">یادداشت ارجاع پرونده:</label>
                        <input v-model="assignOperatorNote" type="text" placeholder="مثال: پرونده با اولویت بالا جهت ثبت سامانه"
                            class="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs focus:outline-none focus:border-limo-500">
                    </div>
                </div>
                <div class="flex justify-end gap-2 pt-2">
                    <button @click="assignOrderModal = null" class="px-4 py-2 bg-slate-100 text-slate-600 rounded-xl text-xs font-bold">انصراف</button>
                    <button @click="submitAssignOperator" :disabled="!assignOperatorName || isAssigningOperator"
                        class="px-5 py-2 bg-limo-600 hover:bg-limo-700 text-white rounded-xl text-xs font-bold transition">
                        <span v-if="isAssigningOperator">در حال ارجاع...</span>
                        <span v-else>ثبت ارجاع اپراتور</span>
                    </button>
                </div>
            </div>
        </div>

        <!-- مودال ۵: افزودن / ویرایش خدمت (Service Modal) -->
        <div v-if="editServiceModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
            <div class="bg-white rounded-3xl max-w-lg w-full max-h-[90vh] overflow-y-auto p-6 space-y-4 shadow-2xl border border-slate-100 text-right">
                <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                    <h3 class="font-black text-sm text-slate-900">{{ currentServiceForm.id ? 'ویرایش مشخصات خدمت' : 'افزودن خدمت جدید' }}</h3>
                    <button @click="editServiceModal = false" class="text-slate-400 hover:text-slate-600">✕</button>
                </div>
                <div class="space-y-3 text-xs">
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">کد یکتای خدمت (انگلیسی):</label>
                            <input v-model="currentServiceForm.code" type="text" placeholder="مثال: TAX_DECLARATION"
                                class="w-full px-3 py-2 border border-slate-200 rounded-xl font-mono text-xs">
                        </div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">عنوان فارسی خدمت:</label>
                            <input v-model="currentServiceForm.title" type="text" placeholder="مثال: ثبت اظهارنامه مالیاتی"
                                class="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs font-bold">
                        </div>
                    </div>
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">دسته‌بندی:</label>
                            <select v-model="currentServiceForm.category_id" class="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs bg-white font-bold">
                                <option v-for="c in catalogCategories" :key="c.id" :value="c.id">{{ c.title }}</option>
                            </select>
                        </div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">تعرفه پایه (ریال):</label>
                            <input v-model.number="currentServiceForm.base_fee" type="number"
                                class="w-full px-3 py-2 border border-slate-200 rounded-xl font-mono text-xs">
                            <div class="text-[10px] text-slate-400 mt-0.5">معادل: {{ formatTomans(currentServiceForm.base_fee) }}</div>
                        </div>
                    </div>
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">توضیحات کوتاه خدمت:</label>
                        <textarea v-model="currentServiceForm.description" rows="2" placeholder="توضیحات و شرایط انجام..."
                            class="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs"></textarea>
                    </div>
                    <div class="flex items-center gap-2 pt-1">
                        <input type="checkbox" id="svcActiveCheck" v-model="currentServiceForm.is_active" class="rounded">
                        <label for="svcActiveCheck" class="font-bold text-slate-800">فعال و قابل سفارش در مینی‌اپ و بات تلگرام</label>
                    </div>
                </div>
                <div class="flex justify-end gap-2 pt-2 border-t border-slate-100">
                    <button @click="editServiceModal = false" class="px-4 py-2 bg-slate-100 text-slate-600 rounded-xl text-xs font-bold">انصراف</button>
                    <button @click="saveServiceForm" :disabled="isSavingService"
                        class="px-5 py-2 bg-limo-600 hover:bg-limo-700 text-white rounded-xl text-xs font-bold transition">
                        {{ isSavingService ? 'در حال ذخیره...' : 'ذخیره تغییرات خدمت' }}
                    </button>
                </div>
            </div>
        </div>

        <!-- مودال ۶: مدیریت دسته‌بندی‌ها (Categories Modal) -->
        <div v-if="categoriesModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
            <div class="bg-white rounded-3xl max-w-md w-full max-h-[85vh] overflow-y-auto p-6 space-y-4 shadow-2xl border border-slate-100 text-right">
                <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                    <h3 class="font-black text-sm text-slate-900">مدیریت دسته‌بندی‌های خدمات</h3>
                    <button @click="categoriesModal = false" class="text-slate-400 hover:text-slate-600">✕</button>
                </div>
                <div class="space-y-3">
                    <!-- فرم افزودن دسته جدید -->
                    <div class="p-3 bg-slate-50 rounded-2xl border border-slate-200 space-y-2 text-xs">
                        <div class="font-bold text-slate-800">➕ ایجاد دسته‌بندی جدید:</div>
                        <div class="grid grid-cols-2 gap-2">
                            <input v-model="newCategoryForm.code" type="text" placeholder="کد: TAX" class="px-3 py-1.5 border border-slate-200 rounded-lg text-xs font-mono">
                            <input v-model="newCategoryForm.title" type="text" placeholder="عنوان: مالیاتی" class="px-3 py-1.5 border border-slate-200 rounded-lg text-xs font-bold">
                        </div>
                        <button @click="saveNewCategory" :disabled="isSavingCategory" class="w-full py-1.5 bg-slate-800 hover:bg-slate-900 text-white rounded-lg text-xs font-bold">
                            {{ isSavingCategory ? 'در حال ثبت...' : 'ثبت دسته‌بندی' }}
                        </button>
                    </div>
                    <!-- لیست دسته‌ها -->
                    <div class="space-y-2 text-xs">
                        <div v-for="c in catalogCategories" :key="c.id" class="p-2.5 bg-white border border-slate-200 rounded-xl flex justify-between items-center">
                            <div>
                                <b class="text-slate-900">{{ c.title }}</b>
                                <span class="font-mono text-slate-400 text-[10px] mr-1">({{ c.code }})</span>
                            </div>
                            <span class="text-[10px] text-slate-400 font-mono">اولویت: {{ c.order_priority || 0 }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- مودال ۷: ایجاد و ویرایش ثبت‌نام مقطعی (Seasonal Campaign Modal) -->
        <div v-if="campaignModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
            <div class="bg-white rounded-3xl max-w-lg w-full max-h-[90vh] overflow-y-auto p-6 space-y-4 shadow-2xl border border-slate-100 text-right">
                <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                    <h3 class="font-black text-sm text-slate-900">{{ editingCampaign.id ? 'ویرایش ثبت‌نام مقطعی' : 'ثبت رویداد مقطعی جدید' }}</h3>
                    <button @click="campaignModalOpen = false" class="text-slate-400 hover:text-slate-600">✕</button>
                </div>
                <div class="space-y-3 text-xs">
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">کد یکتای رویداد:</label>
                            <input v-model="editingCampaign.code" type="text" placeholder="مثال: SANJESH_KONKOOR_1405"
                                class="w-full px-3 py-2 border border-slate-200 rounded-xl font-mono text-xs">
                        </div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">عنوان رویداد / آزمون:</label>
                            <input v-model="editingCampaign.title" type="text" placeholder="مثال: کنکور سراسری نوبت دوم ۱۴۰۵"
                                class="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs font-bold">
                        </div>
                    </div>
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">توضیحات و شرایط ثبت‌نام:</label>
                        <textarea v-model="editingCampaign.description" rows="2" placeholder="توضیحات مدارک و شرایط..."
                            class="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs"></textarea>
                    </div>
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">تاریخ و ساعت آغاز:</label>
                            <input v-model="editingCampaign.start_at" type="text" placeholder="YYYY-MM-DDTHH:mm:ss"
                                class="w-full px-3 py-2 border border-slate-200 rounded-xl font-mono text-xs text-left">
                            <div class="text-[10px] text-slate-400 mt-0.5">مثال: 2026-11-01T08:00:00</div>
                        </div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">تاریخ و ساعت پایان:</label>
                            <input v-model="editingCampaign.end_at" type="text" placeholder="YYYY-MM-DDTHH:mm:ss"
                                class="w-full px-3 py-2 border border-slate-200 rounded-xl font-mono text-xs text-left">
                            <div class="text-[10px] text-slate-400 mt-0.5">مثال: 2026-11-15T23:59:59</div>
                        </div>
                    </div>
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">تعرفه ثبت‌نام (ریال):</label>
                            <input v-model.number="editingCampaign.base_fee" type="number"
                                class="w-full px-3 py-2 border border-slate-200 rounded-xl font-mono text-xs">
                            <div class="text-[10px] text-slate-400 mt-0.5">معادل: {{ formatTomans(editingCampaign.base_fee) }}</div>
                        </div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">وضعیت اولیه:</label>
                            <select v-model="editingCampaign.status" class="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs bg-white font-bold">
                                <option value="SCHEDULED">برنامه‌ریزی‌شده (به‌زودی)</option>
                                <option value="ACTIVE">فعال (در حال ثبت‌نام)</option>
                                <option value="SUSPENDED">متوقف‌شده (تعلیق)</option>
                                <option value="ENDED">پایان‌یافته</option>
                                <option value="DRAFT">پیش‌نویس</option>
                            </select>
                        </div>
                    </div>
                    <div class="flex items-center gap-2 pt-1">
                        <input type="checkbox" id="campActiveCheck" v-model="editingCampaign.is_active" class="rounded">
                        <label for="campActiveCheck" class="font-bold text-slate-800">فعال بودن رویداد در تقویم و مینی‌اپ</label>
                    </div>
                </div>
                <div class="flex justify-end gap-2 pt-2 border-t border-slate-100">
                    <button @click="campaignModalOpen = false" class="px-4 py-2 bg-slate-100 text-slate-600 rounded-xl text-xs font-bold">انصراف</button>
                    <button @click="saveCampaign" :disabled="isSavingCampaign"
                        class="px-5 py-2 bg-limo-600 hover:bg-limo-700 text-white rounded-xl text-xs font-bold transition">
                        {{ isSavingCampaign ? 'در حال ذخیره...' : 'ذخیره رویداد' }}
                    </button>
                </div>
            </div>
        </div>

        <!-- مودال ۸: ارسال اطلاعیه و یادآوری عمومی به کاربران تلگرام (Broadcast Modal) -->
        <div v-if="broadcastModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
            <div class="bg-white rounded-3xl max-w-md w-full p-6 space-y-4 shadow-2xl border border-slate-100 text-right">
                <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                    <h3 class="font-black text-sm text-slate-900">📢 ارسال اطلاعیه به کاربران تلگرام</h3>
                    <button @click="broadcastModalOpen = false" class="text-slate-400 hover:text-slate-600">✕</button>
                </div>
                <div class="space-y-3 text-xs">
                    <div class="p-3 bg-amber-50 rounded-xl border border-amber-200 text-amber-900">
                        <div class="font-bold">📌 رویداد انتخابی: {{ broadcastForm.campaign_title }}</div>
                        <div class="text-[11px] text-amber-700 mt-1">این پیام به صورت نوتیفیکیشن اختصاصی تلگرام برای متقاضیان ارسال خواهد شد.</div>
                    </div>
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">مخاطبان هدف:</label>
                        <select v-model="broadcastForm.target" class="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs bg-white font-bold">
                            <option value="all">همه کاربران فعال ربات تلگرام</option>
                            <option value="reminders">فقط متقاضیانی که درخواست یادآوری این رویداد را ثبت کرده‌اند</option>
                        </select>
                    </div>
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">پیام اختصاصی یا نکته مهم (اختیاری):</label>
                        <textarea v-model="broadcastForm.custom_message" rows="3" placeholder="مثال: مهلت ثبت‌نام تمدید شد و تا فردا شب فرصت باقیست..."
                            class="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs"></textarea>
                    </div>
                </div>
                <div class="flex justify-end gap-2 pt-2 border-t border-slate-100">
                    <button @click="broadcastModalOpen = false" class="px-4 py-2 bg-slate-100 text-slate-600 rounded-xl text-xs font-bold">انصراف</button>
                    <button @click="sendCampaignBroadcast" :disabled="isSendingBroadcast"
                        class="px-5 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-xl text-xs font-bold transition flex items-center gap-1.5">
                        <span v-if="isSendingBroadcast">در حال ارسال پیام...</span>
                        <span v-else>ارسال اطلاعیه 🚀</span>
                    </button>
                </div>
            </div>
        </div>

        <!-- مودال ۴: ارسال پیام تلگرام اختصاصی به متقاضی -->
        <div v-if="messageModalOrder" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
            <div class="bg-white rounded-3xl max-w-md w-full p-6 space-y-4 shadow-2xl border border-slate-100 text-right">
                <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                    <h3 class="font-bold text-sm text-slate-900">ارسال پیام تلگرام به متقاضی</h3>
                    <button @click="messageModalOrder = null" class="text-slate-400 hover:text-slate-600">✕</button>
                </div>
                <div class="text-xs text-slate-500">
                    گیرنده: <b>{{ messageModalOrder.full_name }}</b> (پرونده {{ messageModalOrder.tracking_code }})
                </div>
                <textarea v-model="customMessageText" rows="4" placeholder="متن پیام پشتیبانی را بنویسید..."
                    class="w-full p-3 border border-slate-200 rounded-xl text-xs focus:outline-none focus:border-limo-500"></textarea>
                <div class="flex justify-end gap-2">
                    <button @click="messageModalOrder = null" class="px-4 py-2 bg-slate-100 text-slate-600 rounded-xl text-xs font-bold">انصراف</button>
                    <button @click="sendCustomMessage" :disabled="!customMessageText || isSendingCustomMessage"
                        class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold transition">
                        <span v-if="isSendingCustomMessage">در حال ارسال...</span>
                        <span v-else>ارسال پیام 🚀</span>
                    </button>
                </div>
            </div>
        </div>

        <!-- مودال ۵: ویرایش کانال ارتباطی -->
        <div v-if="editingChannel" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
            <div class="bg-white rounded-3xl max-w-md w-full p-6 space-y-4 shadow-2xl border border-slate-100 text-right">
                <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                    <h3 class="font-bold text-sm text-slate-900">ویرایش کانال ارتباطی: {{ editingChannel.key }}</h3>
                    <button @click="editingChannel = null" class="text-slate-400 hover:text-slate-600">✕</button>
                </div>
                <div class="space-y-3">
                    <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">عنوان نمایشی:</label>
                        <input v-model="editingChannel.title" type="text"
                            class="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs focus:outline-none focus:border-limo-500">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">مقدار / آدرس / شماره تماس:</label>
                        <input v-model="editingChannel.value" type="text" dir="ltr"
                            class="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs font-mono focus:outline-none focus:border-limo-500">
                    </div>
                    <div class="flex items-center gap-2 pt-1">
                        <input type="checkbox" id="ch_active" v-model="editingChannel.is_active" class="rounded text-limo-600">
                        <label for="ch_active" class="text-xs text-slate-700 font-bold">نمایش فعال در ربات تلگرام</label>
                    </div>
                </div>
                <div class="flex justify-end gap-2 pt-2">
                    <button @click="editingChannel = null" class="px-4 py-2 bg-slate-100 text-slate-600 rounded-xl text-xs font-bold">انصراف</button>
                    <button @click="saveChannel" :disabled="isSavingChannel"
                        class="px-5 py-2 bg-limo-600 hover:bg-limo-700 text-white rounded-xl text-xs font-bold transition">
                        <span v-if="isSavingChannel">در حال ذخیره...</span>
                        <span v-else>ذخیره تغییرات</span>
                    </button>
                </div>
            </div>
        </div>

        <!-- مودال ۶: شارژ یا تعدیل دستی کیف پول -->
        <div v-if="adjustModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
            <div class="bg-white rounded-3xl max-w-md w-full p-6 space-y-4 shadow-2xl border border-slate-100 text-right">
                <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                    <h3 class="font-black text-sm text-slate-900">شارژ / تعدیل دستی موجودی کیف پول</h3>
                    <button @click="adjustModalOpen = false" class="text-slate-400 hover:text-slate-600">✕</button>
                </div>
                <div class="text-xs text-slate-600">
                    مشتری: <b>{{ adjustTargetWallet.full_name }}</b> (موجودی فعلی: {{ formatTomans(adjustTargetWallet.balance) }})
                </div>
                <div class="space-y-3">
                    <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">نوع عملیات مالی:</label>
                        <select v-model="adjustType" class="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs bg-white font-bold">
                            <option value="TOPUP">افزایش اعتبار (شارژ دستی)</option>
                            <option value="ADJUSTMENT">کسر از موجودی (تعدیل مالی)</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">مبلغ به ریال:</label>
                        <input v-model.number="adjustAmount" type="number" placeholder="مثال: 5000000"
                            class="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs font-mono font-bold focus:outline-none focus:border-limo-500">
                        <span class="text-[10px] text-slate-400 mt-1 block">معادل: {{ formatTomans(adjustAmount) }}</span>
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">شرح دقیق و علت تراکنش (الزامی):</label>
                        <input v-model="adjustNotes" type="text" placeholder="مثال: شارژ بابت رسیدگی به سفارش..."
                            class="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs focus:outline-none focus:border-limo-500">
                    </div>
                </div>
                <div class="flex justify-end gap-2 pt-2">
                    <button @click="adjustModalOpen = false" class="px-4 py-2 bg-slate-100 text-slate-600 rounded-xl text-xs font-bold">انصراف</button>
                    <button @click="submitAdjustWallet" :disabled="!adjustAmount || isSubmittingAdjust"
                        class="px-5 py-2 bg-limo-600 hover:bg-limo-700 text-white rounded-xl text-xs font-bold transition">
                        <span v-if="isSubmittingAdjust">در حال ثبت...</span>
                        <span v-else>ثبت تراکنش و اعلان به کاربر</span>
                    </button>
                </div>
            </div>
        </div>

    </div>

    <!-- اسکریپت Vue 3 -->
    <script>
        function safeGetStorage(k) {
            try { return localStorage.getItem(k) || ''; } catch(e) { return ''; }
        }
        function safeSetStorage(k, v) {
            try { localStorage.setItem(k, v); } catch(e) {}
        }
        function safeRemoveStorage(k) {
            try { localStorage.removeItem(k); } catch(e) {}
        }

        const { createApp, ref, computed, onMounted } = Vue;

        createApp({
            setup() {
                const isAuthenticated = ref(false);
                const adminUsernameInput = ref(safeGetStorage('limo_admin_user') || '');
                const adminPasswordInput = ref('');
                const authError = ref('');
                const isLoading = ref(false);
                const currentTab = ref('overview');

                // داده‌های پایه‌ای
                const stats = ref({});
                const orders = ref([]);
                const monitors = ref([]);
                const searchQuery = ref('');
                const statusFilter = ref('ALL');

                // ماژول مشتریان (CRM)
                const customersList = ref([]);
                const customerSearchQ = ref('');
                const isLoadingCustomers = ref(false);
                const selectedDossier = ref(null);
                const dossierTab = ref('orders');

                // ماژول خدمات
                const catalogCategories = ref([]);
                const catalogServices = ref([]);
                const editServiceModal = ref(false);
                const categoriesModal = ref(false);
                const isSavingService = ref(false);
                const isSavingCategory = ref(false);
                const isSavingBank = ref(false);
                const settingCardNumber = ref('');
                const settingCardOwner = ref('');
                const settingSupportPhone = ref('');
                const currentServiceForm = ref({ id: null, code: '', title: '', category_id: null, base_fee: 0, description: '', is_active: 1 });
                const newCategoryForm = ref({ code: '', title: '' });

                // ماژول کیف پول
                const adminWallets = ref([]);
                const adminTransactions = ref([]);
                const adjustModalOpen = ref(false);
                const isSubmittingAdjust = ref(false);
                const adjustTargetWallet = ref(null);
                const adjustType = ref('TOPUP');
                const adjustAmount = ref(0);
                const adjustNotes = ref('');

                // ماژول ثبت‌نام‌های مقطعی
                const campaigns = ref([]);
                const campaignModalOpen = ref(false);
                const broadcastModalOpen = ref(false);
                const isSavingCampaign = ref(false);
                const isSendingBroadcast = ref(false);
                const editingCampaign = ref({});
                const broadcastForm = ref({ campaign_id: null, campaign_title: '', target: 'all', custom_message: '' });

                // ماژول چت و پشتیبانی
                const supportThreads = ref([]);
                const selectedThread = ref(null);
                const currentThreadMessages = ref([]);
                const supportFilter = ref('ALL');
                const supportReplyText = ref('');
                const isSendingSupportReply = ref(false);

                // ماژول راه‌های ارتباطی
                const communicationChannels = ref([]);
                const editingChannel = ref(null);
                const isSavingChannel = ref(false);

                // ماژول تنظیمات و لاگ‌ها
                const witnessProvisionFee = ref(3500000);
                const isSavingSetting = ref(false);
                const systemAuditLogs = ref([]);

                // مودال‌ها
                const selectedOrder = ref(null);
                const newOrderStatus = ref('PENDING');
                const newOperatorNotes = ref('');
                const isUpdatingStatus = ref(false);
                const assignOrderModal = ref(null);
                const assignOperatorName = ref('');
                const assignOperatorNote = ref('');
                const isAssigningOperator = ref(false);
                const messageModalOrder = ref(null);
                const customMessageText = ref('');
                const isSendingCustomMessage = ref(false);
                const isCheckingMonitors = ref(false);

                const pendingCount = computed(() => {
                    return orders.value.filter(o => o.status === 'PENDING').length;
                });

                const filteredOrders = computed(() => {
                    return orders.value.filter(o => {
                        const matchStatus = statusFilter.value === 'ALL' || o.status === statusFilter.value;
                        const q = searchQuery.value.trim().toLowerCase();
                        const matchSearch = !q || 
                            (o.tracking_code && o.tracking_code.toLowerCase().includes(q)) ||
                            (o.full_name && o.full_name.toLowerCase().includes(q));
                        return matchStatus && matchSearch;
                    });
                });

                const filteredSupportThreads = computed(() => {
                    if (supportFilter.value === 'ALL') return supportThreads.value;
                    if (supportFilter.value === 'PENDING_SUPPORT' || supportFilter.value === 'PENDING_OPERATOR') {
                        return supportThreads.value.filter(t => t.status === 'PENDING_SUPPORT' || t.status === 'PENDING_OPERATOR');
                    }
                    return supportThreads.value.filter(t => t.status === supportFilter.value);
                });

                async function fetchWithAuth(endpoint, options = {}, directAuth = null) {
                    const u = directAuth?.user || safeGetStorage('limo_admin_user') || (adminUsernameInput.value || '').trim();
                    const p = directAuth?.pass || safeGetStorage('limo_admin_pass') || (adminPasswordInput.value || '').trim();
                    const headers = { ...(options.headers || {}) };
                    if (u && p) {
                        try {
                            headers['Authorization'] = 'Basic ' + btoa(unescape(encodeURIComponent(u + ':' + p)));
                        } catch(e) {
                            headers['Authorization'] = 'Basic ' + btoa(u + ':' + p);
                        }
                        headers['x-admin-username'] = u;
                        headers['x-admin-key'] = p;
                    }
                    return fetch(endpoint, { ...options, headers });
                }

                async function refreshData() {
                    isLoading.value = true;
                    try {
                        const res = await fetchWithAuth('/api/admin/data');
                        if (res.status === 401 || res.status === 403) {
                            isAuthenticated.value = false;
                            authError.value = 'اعتبار کلید امنیتی منقضی شده است.';
                            return;
                        }
                        const data = await res.json();
                        if (data.ok) {
                            stats.value = data.stats || {};
                            orders.value = data.orders || [];
                            monitors.value = data.monitors || [];
                            isAuthenticated.value = true;
                        }
                    } catch (e) {
                        console.error(e);
                    } finally {
                        isLoading.value = false;
                    }
                }

                let chatLiveInterval = null;
                async function switchTab(tab) {
                    currentTab.value = tab;
                    if (chatLiveInterval) {
                        clearInterval(chatLiveInterval);
                        chatLiveInterval = null;
                    }
                    if (tab === 'customers') fetchCustomers();
                    else if (tab === 'services') fetchServices();
                    else if (tab === 'wallets') refreshWalletsData();
                    else if (tab === 'seasonal') fetchCampaigns();
                    else if (tab === 'chats') {
                        fetchSupportThreads();
                        chatLiveInterval = setInterval(async () => {
                            if (currentTab.value === 'chats' && isAuthenticated.value) {
                                try {
                                    const res = await fetchWithAuth('/api/admin/support/threads');
                                    const data = await res.json();
                                    if (data.ok) supportThreads.value = data.threads || [];
                                    if (selectedThread.value) {
                                        const mRes = await fetchWithAuth('/api/admin/support/messages?thread_id=' + selectedThread.value.id);
                                        const mData = await mRes.json();
                                        if (mData.ok) currentThreadMessages.value = mData.messages || [];
                                    }
                                } catch(e) {}
                            }
                        }, 5000);
                    }
                    else if (tab === 'channels') fetchChannels();
                    else if (tab === 'settings') fetchSettingsAndLogs();
                    else if (tab === 'overview' || tab === 'orders' || tab === 'monitors') refreshData();
                }

                function refreshCurrentTab() {
                    switchTab(currentTab.value);
                }

                async function login() {
                    authError.value = '';
                    const rawUser = (adminUsernameInput.value || '').trim();
                    let rawPass = (adminPasswordInput.value || '').trim();
                    if (!rawUser) {
                        authError.value = 'لطفاً نام کاربری مدیریت را وارد فرمایید.';
                        return;
                    }
                    if (!rawPass) {
                        authError.value = 'لطفاً رمز عبور مدیریت را وارد فرمایید.';
                        return;
                    }
                    rawPass = rawPass.replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d))
                                     .replace(/[٠-٩]/g, d => '٠١٢٣٤٥٦٧٨٩'.indexOf(d)).trim();
                    isLoading.value = true;
                    try {
                        const res = await fetchWithAuth('/api/admin/data', {}, { user: rawUser, pass: rawPass });
                        if (res.ok) {
                            const data = await res.json();
                            safeSetStorage('limo_admin_user', rawUser);
                            safeSetStorage('limo_admin_pass', rawPass);
                            stats.value = data.stats || {};
                            orders.value = data.orders || [];
                            monitors.value = data.monitors || [];
                            isAuthenticated.value = true;
                        } else {
                            const errData = await res.json().catch(() => ({}));
                            authError.value = errData.error || 'نام کاربری یا رمز عبور مدیریت نادرست است.';
                            safeRemoveStorage('limo_admin_pass');
                        }
                    } catch (err) {
                        authError.value = 'خطا در ارتباط با سرور.';
                    } finally {
                        isLoading.value = false;
                    }
                }

                function logout() {
                    safeRemoveStorage('limo_admin_user');
                    safeRemoveStorage('limo_admin_pass');
                    isAuthenticated.value = false;
                    adminPasswordInput.value = '';
                }

                function debouncedFetchCustomers() {
                    clearTimeout(debounceTimeout);
                    debounceTimeout = setTimeout(fetchCustomers, 300);
                }

                async function fetchCustomers() {
                    isLoadingCustomers.value = true;
                    try {
                        const q = encodeURIComponent(customerSearchQ.value.trim());
                        const res = await fetchWithAuth('/api/admin/customers?q=' + q);
                        const data = await res.json();
                        if (data.ok) customersList.value = data.customers || [];
                    } catch (e) {
                        console.error(e);
                    } finally {
                        isLoadingCustomers.value = false;
                    }
                }

                async function openCustomerDossier(userId) {
                    try {
                        const res = await fetchWithAuth('/api/admin/customer/dossier?user_id=' + userId);
                        const data = await res.json();
                        if (data.ok) {
                            selectedDossier.value = data.dossier;
                            dossierTab.value = 'orders';
                        } else {
                            alert('خطا در دریافت پرونده: ' + (data.error || ''));
                        }
                    } catch (e) {
                        alert('خطا در برقراری ارتباط');
                    }
                }

                // متدهای خدمات و کاتالوگ
                async function fetchServices() {
                    try {
                        const res = await fetchWithAuth('/api/admin/services');
                        const data = await res.json();
                        if (data.ok) {
                            catalogCategories.value = data.categories || [];
                            catalogServices.value = data.services || [];
                        }
                    } catch(e) {
                        console.error(e);
                    }
                }

                async function toggleServiceActive(svc) {
                    const newActive = !svc.is_active;
                    try {
                        const res = await fetchWithAuth('/api/admin/service/toggle', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ service_id: svc.id, is_active: newActive })
                        });
                        const data = await res.json();
                        if (data.ok) svc.is_active = newActive ? 1 : 0;
                    } catch (e) {
                        alert('خطا در تغییر وضعیت خدمت');
                    }
                }

                function showServiceFields(svc) {
                    let fields = svc.required_fields || {};
                    if (typeof fields === 'string') {
                        try { fields = JSON.parse(fields); } catch(e) { fields = {}; }
                    }
                    const keys = Object.keys(fields);
                    if (keys.length === 0) {
                        alert('این خدمت فیلد اختصاصی اضافه‌ای ندارد.');
                    } else {
                        alert('فیلدهای فرم این خدمت:\n' + keys.map(k => '• ' + (fields[k]?.label || k)).join('\n'));
                    }
                }

                function openNewServiceModal() {
                    currentServiceForm.value = {
                        id: null,
                        code: '',
                        title: '',
                        category_id: catalogCategories.value[0]?.id || null,
                        base_fee: 0,
                        description: '',
                        is_active: 1
                    };
                    editServiceModal.value = true;
                }

                function editService(s) {
                    currentServiceForm.value = {
                        id: s.id,
                        code: s.code,
                        title: s.title,
                        category_id: s.category_id,
                        base_fee: s.base_fee,
                        description: s.description || s.desc || '',
                        is_active: s.is_active ? 1 : 0
                    };
                    editServiceModal.value = true;
                }

                function openCategoriesModal() {
                    categoriesModal.value = true;
                }

                async function saveServiceForm() {
                    if (!currentServiceForm.value.code || !currentServiceForm.value.title) {
                        alert('لطفاً کد و عنوان خدمت را وارد فرمایید.');
                        return;
                    }
                    isSavingService.value = true;
                    try {
                        const res = await fetchWithAuth('/api/admin/service/save', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(currentServiceForm.value)
                        });
                        const data = await res.json();
                        if (data.ok) {
                            editServiceModal.value = false;
                            await fetchServices();
                        } else {
                            alert(data.error || 'خطا در ذخیره خدمت.');
                        }
                    } catch(e) {
                        alert('خطا در ارتباط با سرور.');
                    } finally {
                        isSavingService.value = false;
                    }
                }

                async function saveNewCategory() {
                    if (!newCategoryForm.value.code || !newCategoryForm.value.title) {
                        alert('لطفاً کد و عنوان دسته‌بندی را وارد فرمایید.');
                        return;
                    }
                    isSavingCategory.value = true;
                    try {
                        const res = await fetchWithAuth('/api/admin/category/save', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(newCategoryForm.value)
                        });
                        const data = await res.json();
                        if (data.ok) {
                            newCategoryForm.value = { code: '', title: '' };
                            await fetchServices();
                        } else {
                            alert(data.error || 'خطا در ثبت دسته‌بندی.');
                        }
                    } catch(e) {
                        alert('خطا در ارتباط با سرور.');
                    } finally {
                        isSavingCategory.value = false;
                    }
                }

                async function saveBankSettings() {
                    isSavingBank.value = true;
                    try {
                        await Promise.all([
                            fetchWithAuth('/api/admin/setting/update', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ key: 'card_number', value: settingCardNumber.value })
                            }),
                            fetchWithAuth('/api/admin/setting/update', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ key: 'card_owner', value: settingCardOwner.value })
                            }),
                            fetchWithAuth('/api/admin/setting/update', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ key: 'support_phone', value: settingSupportPhone.value })
                            })
                        ]);
                        alert('مشخصات حساب بانکی با موفقیت ذخیره شد.');
                    } catch(e) {
                        alert('خطا در ذخیره تنظیمات بانکی.');
                    } finally {
                        isSavingBank.value = false;
                    }
                }

                // متدهای سفارش‌ها
                function openOrderDetail(order) {
                    selectedOrder.value = order;
                    newOrderStatus.value = order.status;
                    newOperatorNotes.value = order.operator_notes || '';
                }

                const newInternalNotes = ref('');
                const resultDocText = ref('');

                async function updateOrderStatus() {
                    if (!selectedOrder.value) return;
                    isUpdatingStatus.value = true;
                    try {
                        const payload = {
                            order_id: selectedOrder.value.id,
                            status: newOrderStatus.value,
                            operator_notes: newOperatorNotes.value,
                            internal_notes: newInternalNotes.value
                        };
                        if (newOrderStatus.value === 'COMPLETED' && resultDocText.value) {
                            payload.result_document = {
                                text: resultDocText.value,
                                completed_at: new Date().toISOString()
                            };
                        }
                        const res = await fetchWithAuth('/api/admin/order/status', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(payload)
                        });
                        const result = await res.json();
                        if (result.ok) {
                            selectedOrder.value.status = newOrderStatus.value;
                            selectedOrder.value.operator_notes = newOperatorNotes.value;
                            await refreshData();
                            selectedOrder.value = null;
                        }
                    } catch (e) {
                        alert('خطا در به‌روزرسانی وضعیت سفارش');
                    } finally {
                        isUpdatingStatus.value = false;
                    }
                }

                async function quickStartProgress() {
                    newOrderStatus.value = 'IN_PROGRESS';
                    newOperatorNotes.value = 'پرونده توسط کارشناس در دست اقدام و ثبت سامانه قرار گرفت.';
                    await updateOrderStatus();
                }

                async function quickRequestInfo() {
                    const defect = prompt('موارد نقص مدارک یا اطلاعات مورد نیاز را وارد فرمایید (به متقاضی پیام داده می‌شود):', 'لطفاً تصویر واضح‌تری از صفحه اول شناسنامه/مدرک ارسال فرمایید.');
                    if (!defect) return;
                    newOrderStatus.value = 'NEED_INFO';
                    newOperatorNotes.value = defect;
                    await updateOrderStatus();
                }

                async function quickCompleteOrder() {
                    const resDoc = prompt('متن خروجی یا کد رهگیری صادرشده سامانه را وارد فرمایید:', 'کد رهگیری سامانه دولتی با موفقیت صادر گردید.');
                    if (!resDoc) return;
                    newOrderStatus.value = 'COMPLETED';
                    resultDocText.value = resDoc;
                    newOperatorNotes.value = 'پرونده با موفقیت تکمیل و مدارک نهایی صادر گردید.';
                    await updateOrderStatus();
                }

                function openAssignModal(order) {
                    assignOrderModal.value = order;
                    assignOperatorName.value = '';
                    assignOperatorNote.value = '';
                }

                async function submitAssignOperator() {
                    if (!assignOrderModal.value || !assignOperatorName.value) return;
                    isAssigningOperator.value = true;
                    try {
                        const res = await fetchWithAuth('/api/admin/order/assign', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                order_id: assignOrderModal.value.id,
                                operator_name: assignOperatorName.value,
                                note: assignOperatorNote.value
                            })
                        });
                        const data = await res.json();
                        if (data.ok) {
                            assignOrderModal.value.operator_notes = data.operator_notes;
                            assignOrderModal.value = null;
                            await refreshData();
                        } else {
                            alert('خطا در ارجاع پرونده: ' + (data.error || ''));
                        }
                    } catch (e) {
                        alert('خطا در برقراری ارتباط');
                    } finally {
                        isAssigningOperator.value = false;
                    }
                }

                function openMessageModal(order) {
                    messageModalOrder.value = order;
                    customMessageText.value = '';
                }

                async function sendCustomMessage() {
                    if (!messageModalOrder.value || !customMessageText.value) return;
                    isSendingCustomMessage.value = true;
                    try {
                        const res = await fetchWithAuth('/api/admin/order/message', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                telegram_id: messageModalOrder.value.telegram_id,
                                tracking_code: messageModalOrder.value.tracking_code,
                                message: customMessageText.value
                            })
                        });
                        const result = await res.json();
                        if (result.ok) {
                            alert('✅ پیام با موفقیت به تلگرام متقاضی ارسال شد.');
                            messageModalOrder.value = null;
                        }
                    } catch (e) {
                        alert('خطا در ارسال پیام تلگرام');
                    } finally {
                        isSendingCustomMessage.value = false;
                    }
                }

                // متدهای کیف پول
                async function refreshWalletsData() {
                    try {
                        const [resW, resTx] = await Promise.all([
                            fetchWithAuth('/api/admin/wallets'),
                            fetchWithAuth('/api/admin/wallet/transactions')
                        ]);
                        const dataW = await resW.json();
                        const dataTx = await resTx.json();
                        if (dataW.ok) adminWallets.value = dataW.wallets || [];
                        if (dataTx.ok) adminTransactions.value = dataTx.transactions || [];
                    } catch (e) {
                        console.error(e);
                    }
                }

                function openAdjustModal(wallet) {
                    adjustTargetWallet.value = wallet;
                    adjustType.value = 'TOPUP';
                    adjustAmount.value = 0;
                    adjustNotes.value = '';
                    adjustModalOpen.value = true;
                }

                async function submitAdjustWallet() {
                    if (!adjustAmount.value || adjustAmount.value <= 0 || !adjustNotes.value) {
                        alert('لطفاً مبلغ معتبر و شرح دقیق تراکنش را وارد فرمایید.');
                        return;
                    }
                    const signedAmount = adjustType.value === 'TOPUP' ? adjustAmount.value : -adjustAmount.value;
                    isSubmittingAdjust.value = true;
                    try {
                        const res = await fetchWithAuth('/api/admin/wallet/adjust', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                wallet_id: adjustTargetWallet.value.id,
                                amount: signedAmount,
                                notes: adjustNotes.value,
                                type: adjustType.value
                            })
                        });
                        const data = await res.json();
                        if (data.ok) {
                            adjustModalOpen.value = false;
                            await refreshWalletsData();
                        } else {
                            alert('خطا در ثبت تراکنش: ' + (data.error || 'نامشخص'));
                        }
                    } catch (e) {
                        alert('خطا در برقراری ارتباط');
                    } finally {
                        isSubmittingAdjust.value = false;
                    }
                }

                async function toggleFreezeWallet(wallet) {
                    const newFrozen = !wallet.is_frozen;
                    if (!confirm('آیا از تغییر وضعیت انسداد کیف پول اطمینان دارید؟')) return;
                    try {
                        const res = await fetchWithAuth('/api/admin/wallet/toggle-freeze', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ wallet_id: wallet.id, is_frozen: newFrozen })
                        });
                        const data = await res.json();
                        if (data.ok) await refreshWalletsData();
                    } catch (e) {
                        alert('خطا در تغییر وضعیت');
                    }
                }

                // متدهای ثبت‌نام‌های مقطعی
                async function fetchCampaigns() {
                    try {
                        const res = await fetchWithAuth('/api/admin/seasonal/campaigns');
                        const data = await res.json();
                        if (data.ok) campaigns.value = data.campaigns || [];
                    } catch (e) {
                        console.error(e);
                    }
                }

                async function toggleSeasonalActive(c) {
                    const newActive = !c.is_active;
                    try {
                        const res = await fetchWithAuth('/api/admin/seasonal/status', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ id: c.id, is_active: newActive })
                        });
                        const data = await res.json();
                        if (data.ok) await fetchCampaigns();
                    } catch (e) {
                        alert('خطا در تغییر وضعیت رویداد');
                    }
                }

                function openNewCampaignModal() {
                    editingCampaign.value = {
                        code: '',
                        title: '',
                        description: '',
                        start_at: new Date().toISOString().slice(0, 19),
                        end_at: new Date(Date.now() + 7 * 86400000).toISOString().slice(0, 19),
                        base_fee: 0,
                        status: 'ACTIVE',
                        is_active: true
                    };
                    campaignModalOpen.value = true;
                }

                function editCampaign(c) {
                    editingCampaign.value = { ...c };
                    campaignModalOpen.value = true;
                }

                async function saveCampaign() {
                    if (!editingCampaign.value.code || !editingCampaign.value.title || !editingCampaign.value.start_at || !editingCampaign.value.end_at) {
                        alert('لطفاً فیلدهای الزامی کد، عنوان و تاریخ‌های شروع و پایان را وارد فرمایید.');
                        return;
                    }
                    isSavingCampaign.value = true;
                    try {
                        const res = await fetchWithAuth('/api/admin/seasonal/campaign', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(editingCampaign.value)
                        });
                        const data = await res.json();
                        if (data.ok) {
                            campaignModalOpen.value = false;
                            await fetchCampaigns();
                            alert('رویداد ثبت‌نام با موفقیت ذخیره شد.');
                        } else {
                            alert(data.error || 'خطا در ذخیره رویداد');
                        }
                    } catch (e) {
                        alert('خطای ارتباط با سرور');
                    } finally {
                        isSavingCampaign.value = false;
                    }
                }

                function openBroadcastModal(c) {
                    broadcastForm.value = {
                        campaign_id: c.id,
                        campaign_title: c.title,
                        target: 'all',
                        custom_message: ''
                    };
                    broadcastModalOpen.value = true;
                }

                async function sendCampaignBroadcast() {
                    if (!confirm('آیا از ارسال این اطلاعیه به کاربران اطمینان دارید؟')) return;
                    isSendingBroadcast.value = true;
                    try {
                        const res = await fetchWithAuth('/api/admin/seasonal/broadcast', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(broadcastForm.value)
                        });
                        const data = await res.json();
                        if (data.ok) {
                            broadcastModalOpen.value = false;
                            alert(data.message || 'اطلاعیه با موفقیت ارسال شد.');
                        } else {
                            alert(data.error || 'خطا در ارسال اطلاعیه');
                        }
                    } catch (e) {
                        alert('خطا در ارسال اطلاعیه');
                    } finally {
                        isSendingBroadcast.value = false;
                    }
                }

                // متدهای چت زنده
                async function fetchSupportThreads() {
                    try {
                        const res = await fetchWithAuth('/api/admin/support/threads');
                        const data = await res.json();
                        if (data.ok) {
                            supportThreads.value = data.threads || [];
                            if (!selectedThread.value && supportThreads.value.length > 0) {
                                selectThread(supportThreads.value[0]);
                            }
                        }
                    } catch (e) {
                        console.error(e);
                    }
                }

                async function selectThread(th) {
                    selectedThread.value = th;
                    currentThreadMessages.value = [];
                    try {
                        const res = await fetchWithAuth('/api/admin/support/messages?thread_id=' + th.id);
                        const data = await res.json();
                        if (data.ok) currentThreadMessages.value = data.messages || [];
                    } catch (e) {
                        console.error(e);
                    }
                }

                async function sendSupportReply() {
                    if (!selectedThread.value || !supportReplyText.value.trim()) return;
                    isSendingSupportReply.value = true;
                    try {
                        const res = await fetchWithAuth('/api/admin/support/reply', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                thread_id: selectedThread.value.id,
                                telegram_id: selectedThread.value.telegram_id,
                                message: supportReplyText.value.trim()
                            })
                        });
                        const data = await res.json();
                        if (data.ok) {
                            supportReplyText.value = '';
                            await selectThread(selectedThread.value);
                            await fetchSupportThreads();
                        }
                    } catch (e) {
                        alert('خطا در ارسال پاسخ');
                    } finally {
                        isSendingSupportReply.value = false;
                    }
                }

                async function changeThreadStatus(status) {
                    if (!selectedThread.value) return;
                    try {
                        const res = await fetchWithAuth('/api/admin/support/status', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ thread_id: selectedThread.value.id, status })
                        });
                        const data = await res.json();
                        if (data.ok) {
                            selectedThread.value.status = status;
                            await fetchSupportThreads();
                        }
                    } catch (e) {
                        alert('خطا در تغییر وضعیت تیکت');
                    }
                }

                // متدهای کانال‌های ارتباطی
                async function fetchChannels() {
                    try {
                        const res = await fetchWithAuth('/api/admin/channels');
                        const data = await res.json();
                        if (data.ok) communicationChannels.value = data.channels || [];
                    } catch (e) {
                        console.error(e);
                    }
                }

                function openChannelEdit(ch) {
                    editingChannel.value = { ...ch };
                }

                async function saveChannel() {
                    if (!editingChannel.value) return;
                    isSavingChannel.value = true;
                    try {
                        const res = await fetchWithAuth('/api/admin/channel/update', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(editingChannel.value)
                        });
                        const data = await res.json();
                        if (data.ok) {
                            editingChannel.value = null;
                            await fetchChannels();
                        } else {
                            alert('خطا در ذخیره کانال');
                        }
                    } catch (e) {
                        alert('خطا در برقراری ارتباط');
                    } finally {
                        isSavingChannel.value = false;
                    }
                }

                // متدهای تنظیمات و لاگ‌های سیستم
                async function fetchSettingsAndLogs() {
                    try {
                        const [resSet, resLogs] = await Promise.all([
                            fetchWithAuth('/api/admin/settings'),
                            fetchWithAuth('/api/admin/audit-logs')
                        ]);
                        const dataSet = await resSet.json();
                        const dataLogs = await resLogs.json();
                        if (dataSet.ok) {
                            const feeObj = (dataSet.settings || []).find(s => s.key === 'witness_provision_fee');
                            if (feeObj) witnessProvisionFee.value = parseInt(feeObj.value, 10);
                            const cNum = (dataSet.settings || []).find(s => s.key === 'card_number');
                            if (cNum) settingCardNumber.value = cNum.value;
                            const cOwner = (dataSet.settings || []).find(s => s.key === 'card_owner');
                            if (cOwner) settingCardOwner.value = cOwner.value;
                            const sPhone = (dataSet.settings || []).find(s => s.key === 'support_phone');
                            if (sPhone) settingSupportPhone.value = sPhone.value;
                        }
                        if (dataLogs.ok) systemAuditLogs.value = dataLogs.logs || [];
                    } catch (e) {
                        console.error(e);
                    }
                }

                async function saveWitnessFee() {
                    if (!witnessProvisionFee.value || witnessProvisionFee.value < 0) return;
                    isSavingSetting.value = true;
                    try {
                        const res = await fetchWithAuth('/api/admin/setting/update', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ key: 'witness_provision_fee', value: witnessProvisionFee.value })
                        });
                        const data = await res.json();
                        if (data.ok) alert('✅ هزینه تأمین شاهد با موفقیت به‌روزرسانی شد.');
                        else alert('خطا در ذخیره تعرفه');
                    } catch (e) {
                        alert('خطا در برقراری ارتباط');
                    } finally {
                        isSavingSetting.value = false;
                    }
                }

                async function checkAllMonitorsNow() {
                    isCheckingMonitors.value = true;
                    try {
                        const res = await fetchWithAuth('/api/admin/monitors/check', { method: 'POST' });
                        if (res.ok) await refreshData();
                    } catch (e) {
                        console.error(e);
                    } finally {
                        isCheckingMonitors.value = false;
                    }
                }

                function exportCSV() {
                    let csv = '\uFEFFکد رهگیری,نام متقاضی,شناسه تلگرام,عنوان خدمت,وضعیت,تاریخ ثبت\n';
                    orders.value.forEach(o => {
                        csv += `"${o.tracking_code}","${o.full_name || ''}","${o.telegram_id}","${o.service_title}","${statusLabel(o.status)}","${o.created_at}"\n`;
                    });
                    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
                    const url = URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.setAttribute('href', url);
                    link.setAttribute('download', 'Limo_Orders_' + new Date().toISOString().slice(0,10) + '.csv');
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }

                function formatTomans(amount) {
                    if (!amount && amount !== 0) return '۰ تومان';
                    const tomans = Math.round(amount / 10);
                    return tomans.toLocaleString('fa-IR') + ' تومان';
                }

                function statusBadgeClass(status) {
                    switch (status) {
                        case 'PENDING': return 'bg-amber-100 text-amber-800';
                        case 'RECEIPT_SUBMITTED': return 'bg-purple-100 text-purple-800';
                        case 'APPROVED': return 'bg-emerald-100 text-emerald-800';
                        case 'IN_PROGRESS': return 'bg-blue-100 text-blue-800';
                        case 'PAYMENT_REJECTED': return 'bg-rose-100 text-rose-800';
                        case 'NEED_INFO': return 'bg-orange-100 text-orange-800';
                        case 'COMPLETED': return 'bg-blue-100 text-blue-800';
                        case 'CANCELLED': return 'bg-slate-100 text-slate-800';
                        default: return 'bg-slate-100 text-slate-800';
                    }
                }

                function statusLabel(status) {
                    switch (status) {
                        case 'PENDING': return 'در انتظار پرداخت';
                        case 'RECEIPT_SUBMITTED': return 'فیش در انتظار بررسی 💳';
                        case 'APPROVED': return 'پرداخت تأیید شد ✅';
                        case 'IN_PROGRESS': return 'در دست اقدام متصدی ⚙️';
                        case 'PAYMENT_REJECTED': return 'فیش رد شد ❌';
                        case 'NEED_INFO': return 'نقص مدارک';
                        case 'COMPLETED': return 'تکمیل شده';
                        case 'CANCELLED': return 'لغو شده';
                        default: return status || 'نامشخص';
                    }
                }

                async function quickApprovePayment() {
                    newOrderStatus.value = 'APPROVED';
                    newOperatorNotes.value = 'فیش واریز بررسی و صحت پرداخت تأیید گردید.';
                    await updateOrderStatus();
                }

                async function quickRejectPayment() {
                    const reason = prompt('علت رد فیش پرداخت را وارد فرمایید (به متقاضی اطلاع داده می‌شود):', 'مبلغ واریزی ناقص است یا فیش ناخوانا می‌باشد.');
                    if (!reason) return;
                    newOrderStatus.value = 'PAYMENT_REJECTED';
                    newOperatorNotes.value = reason;
                    await updateOrderStatus();
                }

                function seasonalBadgeClass(status) {
                    switch (status) {
                        case 'ACTIVE': return 'bg-emerald-100 text-emerald-800';
                        case 'SCHEDULED': return 'bg-blue-100 text-blue-800';
                        case 'EXPIRING_SOON': return 'bg-amber-100 text-amber-800';
                        case 'ENDED': return 'bg-slate-100 text-slate-600';
                        case 'SUSPENDED': return 'bg-rose-100 text-rose-800';
                        default: return 'bg-slate-100 text-slate-800';
                    }
                }

                function seasonalStatusLabel(status) {
                    switch (status) {
                        case 'ACTIVE': return 'فعال و باز';
                        case 'SCHEDULED': return 'زمان‌بندی شده';
                        case 'EXPIRING_SOON': return 'مهلت رو به اتمام';
                        case 'ENDED': return 'پایان یافته';
                        case 'SUSPENDED': return 'متوقف شده';
                        default: return 'پیش‌نویس';
                    }
                }

                function supportStatusBadgeClass(status) {
                    switch (status) {
                        case 'NEW': return 'bg-rose-100 text-rose-800';
                        case 'PENDING_SUPPORT':
                        case 'PENDING_OPERATOR': return 'bg-amber-100 text-amber-800';
                        case 'PENDING_CUSTOMER': return 'bg-blue-100 text-blue-800';
                        case 'CLOSED': return 'bg-slate-100 text-slate-600';
                        default: return 'bg-slate-100 text-slate-800';
                    }
                }

                function supportStatusLabel(status) {
                    switch (status) {
                        case 'NEW': return 'پیام جدید';
                        case 'PENDING_SUPPORT':
                        case 'PENDING_OPERATOR': return 'در انتظار پاسخ ما';
                        case 'PENDING_CUSTOMER': return 'منتظر پاسخ کاربر';
                        case 'CLOSED': return 'بسته شده';
                        default: return status || 'نامشخص';
                    }
                }

                function parseOrderData(data) {
                    if (typeof data === 'object' && data !== null) return data;
                    try { return JSON.parse(data); } catch { return {}; }
                }

                function formatFieldKey(key) {
                    const dict = {
                        tenant_phone: 'شماره تماس مستأجر',
                        landlord_phone: 'شماره تماس مالک',
                        landlord_national_id: 'کد ملی مالک',
                        deposit_and_rent: 'مبلغ رهن و اجاره ماهانه',
                        postal_code_and_bill: 'شناسه قبض برق و کد پستی ملک',
                        landlord_card_number: 'شماره کارت واریز کرایه',
                        witness_mode: 'وضعیت شاهدان',
                        witness_1_info: 'مشخصات شاهد اول',
                        witness_2_info: 'مشخصات شاهد دوم',
                        witness_provision_fee: 'هزینه تأمین دو شاهد رسمی',
                        national_id: 'کد ملی',
                        exam_type: 'نوع آزمون'
                    };
                    return dict[key] || key;
                }

                function formatDate(dStr) {
                    if (!dStr) return '-';
                    return dStr.replace('T', ' ').slice(0, 16);
                }

                onMounted(() => {
                    try {
                        const urlParams = new URLSearchParams(window.location.search);
                        const urlUser = urlParams.get('user');
                        const urlKey = urlParams.get('key') || urlParams.get('pass');
                        if (urlUser && urlKey) {
                            adminUsernameInput.value = urlUser;
                            adminPasswordInput.value = urlKey;
                            login();
                            return;
                        }
                    } catch (e) {}

                    const savedUser = safeGetStorage('limo_admin_user');
                    const savedPass = safeGetStorage('limo_admin_pass');
                    if (savedUser && savedPass) {
                        adminUsernameInput.value = savedUser;
                        adminPasswordInput.value = savedPass;
                        refreshData();
                    }
                });

                return {
                    isAuthenticated,
                    adminUsernameInput,
                    adminPasswordInput,
                    authError,
                    isLoading,
                    currentTab,
                    stats,
                    orders,
                    monitors,
                    searchQuery,
                    statusFilter,
                    pendingCount,
                    filteredOrders,
                    customersList,
                    customerSearchQ,
                    isLoadingCustomers,
                    selectedDossier,
                    dossierTab,
                    debouncedFetchCustomers,
                    openCustomerDossier,
                    catalogCategories,
                    catalogServices,
                    toggleServiceActive,
                    editServiceModal,
                    categoriesModal,
                    isSavingService,
                    isSavingCategory,
                    isSavingBank,
                    settingCardNumber,
                    settingCardOwner,
                    settingSupportPhone,
                    currentServiceForm,
                    newCategoryForm,
                    openNewServiceModal,
                    editService,
                    openCategoriesModal,
                    saveServiceForm,
                    saveNewCategory,
                    saveBankSettings,
                    showServiceFields,
                    adminWallets,
                    adminTransactions,
                    adjustModalOpen,
                    isSubmittingAdjust,
                    adjustTargetWallet,
                    adjustType,
                    adjustAmount,
                    adjustNotes,
                    openAdjustModal,
                    submitAdjustWallet,
                    toggleFreezeWallet,
                    campaigns,
                    toggleSeasonalActive,
                    campaignModalOpen,
                    broadcastModalOpen,
                    isSavingCampaign,
                    isSendingBroadcast,
                    editingCampaign,
                    broadcastForm,
                    openNewCampaignModal,
                    editCampaign,
                    saveCampaign,
                    openBroadcastModal,
                    sendCampaignBroadcast,
                    supportThreads,
                    selectedThread,
                    currentThreadMessages,
                    supportFilter,
                    supportReplyText,
                    isSendingSupportReply,
                    filteredSupportThreads,
                    selectThread,
                    sendSupportReply,
                    changeThreadStatus,
                    communicationChannels,
                    editingChannel,
                    isSavingChannel,
                    openChannelEdit,
                    saveChannel,
                    witnessProvisionFee,
                    isSavingSetting,
                    systemAuditLogs,
                    saveWitnessFee,
                    selectedOrder,
                    newOrderStatus,
                    newOperatorNotes,
                    isUpdatingStatus,
                    openOrderDetail,
                    updateOrderStatus,
                    quickApprovePayment,
                    quickRejectPayment,
                    newInternalNotes,
                    resultDocText,
                    quickStartProgress,
                    quickRequestInfo,
                    quickCompleteOrder,
                    assignOrderModal,
                    assignOperatorName,
                    assignOperatorNote,
                    isAssigningOperator,
                    openAssignModal,
                    submitAssignOperator,
                    messageModalOrder,
                    customMessageText,
                    isSendingCustomMessage,
                    openMessageModal,
                    sendCustomMessage,
                    isCheckingMonitors,
                    checkAllMonitorsNow,
                    switchTab,
                    refreshCurrentTab,
                    login,
                    logout,
                    exportCSV,
                    formatTomans,
                    statusBadgeClass,
                    statusLabel,
                    seasonalBadgeClass,
                    seasonalStatusLabel,
                    supportStatusBadgeClass,
                    supportStatusLabel,
                    parseOrderData,
                    formatFieldKey,
                    formatDate
                };
            }
        }).mount('#admin-app');
    </script>
</body>
</html>'''

import json

file_content = f"""/**
 * پنل مدیریت جامع و مستقل تحت وب کافی‌نت لیمو (Stand-alone Web Admin Dashboard)
 * شامل ۹ ماژول مستقل مصوب بر اساس سند حاکم پروژه:
 * ۱. داشبورد و آمار (overview)
 * ۲. مشتریان و پرونده‌ها (customers)
 * ۳. درخواست‌ها و ثبت‌نام‌ها (orders)
 * ۴. خدمات، دسته‌بندی‌ها و فرم‌ها (services)
 * ۵. کیف پول و تراکنش‌ها (wallets)
 * ۶. ثبت‌نام‌های مقطعی و اعلان‌ها (seasonal)
 * ۷. گفت‌وگوهای پشتیبانی (chats)
 * ۸. راه‌های ارتباطی (channels)
 * ۹. مدیران، دسترسی، تنظیمات و لاگ‌های سیستم (settings)
 * + پایش هوشمند سایت‌ها (monitors)
 */

export const ADMIN_DASHBOARD_HTML = {json.dumps(html_content, ensure_ascii=False)};
"""

out_path = os.path.join(os.path.dirname(__file__), "..", "cloudflare", "admin_html.js")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(file_content)

print(f"Generated admin_html.js successfully. Length: {len(file_content)} bytes.")
