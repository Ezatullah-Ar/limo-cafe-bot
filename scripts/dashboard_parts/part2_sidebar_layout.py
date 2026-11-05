# -*- coding: utf-8 -*-
# Part 2: Right-Sidebar Dashboard Structure & Top Bar

SIDEBAR_AND_LAYOUT = r'''
        <!-- بدنه اصلی داشبورد با ستون کناری راست (Right-Sidebar Dashboard) -->
        <div v-else class="flex-1 min-h-screen flex bg-slate-100">
            
            <!-- پس‌زمینه نیمه‌شفاف موبایل هنگام باز بودن سایدبار -->
            <div v-if="mobileSidebarOpen" @click="mobileSidebarOpen = false"
                class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm z-40 xl:hidden"></div>

            <!-- ستون کناری سمت راست (Right Sidebar) -->
            <aside :class="{'translate-x-0': mobileSidebarOpen, 'translate-x-full xl:translate-x-0': !mobileSidebarOpen}"
                class="fixed top-0 bottom-0 right-0 w-68 bg-slate-900 border-l border-slate-800 text-slate-300 z-50 flex flex-col justify-between transition-transform duration-300 ease-in-out shadow-2xl">
                
                <!-- بخش بالای سایدبار: برندینگ و لوگو -->
                <div>
                    <div class="p-5 border-b border-slate-800 flex items-center justify-between">
                        <div class="flex items-center gap-3">
                            <img src="/logo.png" alt="لوگو لیمو" class="h-10 w-auto object-contain">
                            <div>
                                <span class="text-sm font-black text-white block leading-tight">کافی‌نت لیمو</span>
                                <span class="text-[11px] text-slate-400 font-medium">داشبورد جامع مدیریت</span>
                            </div>
                        </div>
                        <button @click="mobileSidebarOpen = false" class="xl:hidden p-1.5 text-slate-400 hover:text-white rounded-lg">✕</button>
                    </div>

                    <!-- فهرست ماژول‌های مدیریتی منو -->
                    <nav class="p-3 space-y-1 text-xs font-bold overflow-y-auto max-h-[calc(100vh-12rem)]">
                        <!-- پیشخوان آماری -->
                        <button @click="switchTab('overview')"
                            :class="{'bg-limo-600 text-slate-950 font-black shadow-lg shadow-limo-900/30': currentTab === 'overview', 'text-slate-300 hover:bg-slate-800 hover:text-white': currentTab !== 'overview'}"
                            class="w-full px-3.5 py-2.5 rounded-xl transition flex items-center justify-between text-right">
                            <span class="flex items-center gap-2.5">
                                <span class="text-base">📊</span>
                                <span>پیشخوان و آمار</span>
                            </span>
                        </button>

                        <!-- سفارشات و درخواست‌ها -->
                        <button @click="switchTab('orders')"
                            :class="{'bg-limo-600 text-slate-950 font-black shadow-lg shadow-limo-900/30': currentTab === 'orders', 'text-slate-300 hover:bg-slate-800 hover:text-white': currentTab !== 'orders'}"
                            class="w-full px-3.5 py-2.5 rounded-xl transition flex items-center justify-between text-right">
                            <span class="flex items-center gap-2.5">
                                <span class="text-base">📦</span>
                                <span>سفارشات و پرونده‌ها</span>
                            </span>
                            <span v-if="pendingCount > 0" class="bg-amber-500 text-slate-950 text-[10px] font-black px-2 py-0.5 rounded-full">
                                {{ pendingCount }}
                            </span>
                        </button>

                        <!-- مدیریت مشتریان -->
                        <button @click="switchTab('customers')"
                            :class="{'bg-limo-600 text-slate-950 font-black shadow-lg shadow-limo-900/30': currentTab === 'customers', 'text-slate-300 hover:bg-slate-800 hover:text-white': currentTab !== 'customers'}"
                            class="w-full px-3.5 py-2.5 rounded-xl transition flex items-center justify-between text-right">
                            <span class="flex items-center gap-2.5">
                                <span class="text-base">👥</span>
                                <span>مدیریت مشتریان (CRM)</span>
                            </span>
                            <span v-if="customers.length > 0" class="bg-slate-800 text-slate-300 text-[10px] px-2 py-0.5 rounded-full border border-slate-700">
                                {{ customers.length }}
                            </span>
                        </button>

                        <!-- خدمات و فرم‌ساز پویا -->
                        <button @click="switchTab('services')"
                            :class="{'bg-limo-600 text-slate-950 font-black shadow-lg shadow-limo-900/30': currentTab === 'services', 'text-slate-300 hover:bg-slate-800 hover:text-white': currentTab !== 'services'}"
                            class="w-full px-3.5 py-2.5 rounded-xl transition flex items-center justify-between text-right">
                            <span class="flex items-center gap-2.5">
                                <span class="text-base">🛠️</span>
                                <span>خدمات و فرم‌ساز</span>
                            </span>
                        </button>

                        <!-- دسته‌بندی خدمات -->
                        <button @click="switchTab('categories')"
                            :class="{'bg-limo-600 text-slate-950 font-black shadow-lg shadow-limo-900/30': currentTab === 'categories', 'text-slate-300 hover:bg-slate-800 hover:text-white': currentTab !== 'categories'}"
                            class="w-full px-3.5 py-2.5 rounded-xl transition flex items-center justify-between text-right">
                            <span class="flex items-center gap-2.5">
                                <span class="text-base">🏷️</span>
                                <span>دسته‌بندی خدمات</span>
                            </span>
                        </button>

                        <!-- کیف پول و تراکنش‌ها -->
                        <button @click="switchTab('wallets')"
                            :class="{'bg-limo-600 text-slate-950 font-black shadow-lg shadow-limo-900/30': currentTab === 'wallets', 'text-slate-300 hover:bg-slate-800 hover:text-white': currentTab !== 'wallets'}"
                            class="w-full px-3.5 py-2.5 rounded-xl transition flex items-center justify-between text-right">
                            <span class="flex items-center gap-2.5">
                                <span class="text-base">💳</span>
                                <span>کیف پول و مالی</span>
                            </span>
                        </button>

                        <!-- ثبت‌نام‌های مقطعی -->
                        <button @click="switchTab('seasonal')"
                            :class="{'bg-limo-600 text-slate-950 font-black shadow-lg shadow-limo-900/30': currentTab === 'seasonal', 'text-slate-300 hover:bg-slate-800 hover:text-white': currentTab !== 'seasonal'}"
                            class="w-full px-3.5 py-2.5 rounded-xl transition flex items-center justify-between text-right">
                            <span class="flex items-center gap-2.5">
                                <span class="text-base">📢</span>
                                <span>ثبت‌نام‌های مقطعی</span>
                            </span>
                        </button>

                        <!-- گفتگوی زنده و تیکت‌ها -->
                        <button @click="switchTab('chats')"
                            :class="{'bg-limo-600 text-slate-950 font-black shadow-lg shadow-limo-900/30': currentTab === 'chats', 'text-slate-300 hover:bg-slate-800 hover:text-white': currentTab !== 'chats'}"
                            class="w-full px-3.5 py-2.5 rounded-xl transition flex items-center justify-between text-right">
                            <span class="flex items-center gap-2.5">
                                <span class="text-base">💬</span>
                                <span>گفتگوی زنده و تیکت</span>
                            </span>
                            <span v-if="pendingSupportCount > 0" class="bg-blue-500 text-white text-[10px] font-black px-2 py-0.5 rounded-full animate-pulse">
                                {{ pendingSupportCount }}
                            </span>
                        </button>

                        <!-- پایش سامانه‌ها -->
                        <button @click="switchTab('monitors')"
                            :class="{'bg-limo-600 text-slate-950 font-black shadow-lg shadow-limo-900/30': currentTab === 'monitors', 'text-slate-300 hover:bg-slate-800 hover:text-white': currentTab !== 'monitors'}"
                            class="w-full px-3.5 py-2.5 rounded-xl transition flex items-center justify-between text-right">
                            <span class="flex items-center gap-2.5">
                                <span class="text-base">🌐</span>
                                <span>پایش هوشمند سایت‌ها</span>
                            </span>
                        </button>

                        <!-- راه‌های ارتباطی -->
                        <button @click="switchTab('channels')"
                            :class="{'bg-limo-600 text-slate-950 font-black shadow-lg shadow-limo-900/30': currentTab === 'channels', 'text-slate-300 hover:bg-slate-800 hover:text-white': currentTab !== 'channels'}"
                            class="w-full px-3.5 py-2.5 rounded-xl transition flex items-center justify-between text-right">
                            <span class="flex items-center gap-2.5">
                                <span class="text-base">📱</span>
                                <span>راه‌های ارتباطی</span>
                            </span>
                        </button>

                        <!-- سطل زباله ۳۰ روزه -->
                        <button @click="switchTab('trash')"
                            :class="{'bg-limo-600 text-slate-950 font-black shadow-lg shadow-limo-900/30': currentTab === 'trash', 'text-slate-300 hover:bg-slate-800 hover:text-white': currentTab !== 'trash'}"
                            class="w-full px-3.5 py-2.5 rounded-xl transition flex items-center justify-between text-right">
                            <span class="flex items-center gap-2.5">
                                <span class="text-base">🗑️</span>
                                <span>سطل زباله (۳۰ روزه)</span>
                            </span>
                            <span v-if="trashItems.length > 0" class="bg-rose-500 text-white text-[10px] font-black px-2 py-0.5 rounded-full">
                                {{ trashItems.length }}
                            </span>
                        </button>

                        <!-- پشتیبان‌گیری و خروجی -->
                        <button @click="switchTab('backup')"
                            :class="{'bg-limo-600 text-slate-950 font-black shadow-lg shadow-limo-900/30': currentTab === 'backup', 'text-slate-300 hover:bg-slate-800 hover:text-white': currentTab !== 'backup'}"
                            class="w-full px-3.5 py-2.5 rounded-xl transition flex items-center justify-between text-right">
                            <span class="flex items-center gap-2.5">
                                <span class="text-base">💾</span>
                                <span>پشتیبان‌گیری داده‌ها</span>
                            </span>
                        </button>

                        <!-- تنظیمات جامع سامانه -->
                        <button @click="switchTab('settings')"
                            :class="{'bg-limo-600 text-slate-950 font-black shadow-lg shadow-limo-900/30': currentTab === 'settings', 'text-slate-300 hover:bg-slate-800 hover:text-white': currentTab !== 'settings'}"
                            class="w-full px-3.5 py-2.5 rounded-xl transition flex items-center justify-between text-right">
                            <span class="flex items-center gap-2.5">
                                <span class="text-base">⚙️</span>
                                <span>تنظیمات کافی‌نت</span>
                            </span>
                        </button>
                    </nav>
                </div>

                <!-- بخش پایین سایدبار: کارت مشخصات مدیر و دکمه خروج -->
                <div class="p-4 border-t border-slate-800 bg-slate-950/60 space-y-3">
                    <div class="flex items-center gap-3">
                        <div class="w-9 h-9 rounded-xl bg-limo-600 text-slate-950 flex items-center justify-center font-black text-sm shadow-md">
                            {{ (adminUser.username || 'A').charAt(0).toUpperCase() }}
                        </div>
                        <div class="overflow-hidden flex-1">
                            <span class="text-xs font-bold text-white block truncate">{{ adminUser.username || 'مدیر ارشد' }}</span>
                            <span class="text-[10px] text-emerald-400 font-medium flex items-center gap-1">
                                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                                آنلاین (دسترسی کامل)
                            </span>
                        </div>
                    </div>
                    <button @click="logout"
                        class="w-full py-2 px-3 bg-rose-950/40 hover:bg-rose-900/60 text-rose-300 border border-rose-800/40 rounded-xl text-xs font-bold transition flex items-center justify-center gap-2">
                        <span>🚪</span>
                        <span>خروج امن از سیستم</span>
                    </button>
                </div>
            </aside>

            <!-- محتوای اصلی داشبورد در سمت چپ سایدبار -->
            <div class="flex-1 xl:mr-68 min-h-screen flex flex-col bg-slate-50 transition-all main-scroll">
                
                <!-- نوار هدر بالای صفحه اصلی -->
                <header class="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm px-4 sm:px-6 py-3 flex items-center justify-between">
                    <div class="flex items-center gap-3">
                        <!-- دکمه همبرگری باز کردن منو در موبایل -->
                        <button @click="mobileSidebarOpen = true"
                            class="xl:hidden p-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl transition">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
                            </svg>
                        </button>
                        
                        <div>
                            <h2 class="text-base font-black text-slate-900">{{ tabTitle(currentTab) }}</h2>
                            <p class="text-[11px] text-slate-400 hidden sm:block">سامانه جامع خدمات اینترنتی و کنسولی کافی‌نت لیمو</p>
                        </div>
                    </div>

                    <!-- کنترل‌های سمت چپ هدر -->
                    <div class="flex items-center gap-2">
                        <button @click="refreshCurrentTab" :disabled="isLoading" title="بروزرسانی داده‌ها"
                            class="p-2 text-slate-500 hover:text-limo-700 hover:bg-slate-100 rounded-xl transition border border-slate-200">
                            <span :class="{'animate-spin inline-block': isLoading}">🔄</span>
                        </button>
                        <button @click="exportCSV" title="دانلود اکسل سفارش‌ها"
                            class="hidden md:flex items-center gap-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold transition border border-slate-200">
                            <span>📊 خروجی Excel</span>
                        </button>
                        <span class="hidden lg:inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-50 text-emerald-700 rounded-xl text-[11px] font-bold border border-emerald-100">
                            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
                            سامانه آنلاین
                        </span>
                    </div>
                </header>

                <!-- محتوای صفحات تب‌ها -->
                <main class="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 space-y-6">
'''
