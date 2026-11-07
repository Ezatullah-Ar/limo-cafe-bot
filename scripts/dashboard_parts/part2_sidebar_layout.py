# -*- coding: utf-8 -*-
# Part 2: Refined Right-Sidebar Dashboard Structure & Modern Header (Unique Limo Identity)

SIDEBAR_AND_LAYOUT = r'''
        <!-- بدنه اصلی داشبورد با ستون کناری راست با هویت اختصاصی لیمو -->
        <div v-else class="flex-1 min-h-screen flex bg-slate-100/90">
            
            <!-- پس‌زمینه نیمه‌شفاف موبایل هنگام باز بودن سایدبار -->
            <div v-if="mobileSidebarOpen" @click="mobileSidebarOpen = false"
                class="fixed inset-0 bg-slate-950/70 backdrop-blur-sm z-40 xl:hidden"></div>

            <!-- ستون کناری سمت راست با استایل اختصاصی لیمو (Emerald-Obsidian Gradient) -->
            <aside :class="{'translate-x-0': mobileSidebarOpen, 'translate-x-full xl:translate-x-0': !mobileSidebarOpen}"
                class="sidebar-gradient fixed top-0 bottom-0 right-0 w-68 border-l border-emerald-900/40 text-slate-300 z-50 flex flex-col justify-between transition-transform duration-300 ease-in-out shadow-2xl">
                
                <!-- بخش بالای سایدبار: لوگو و برند اختصاصی کافی‌نت لیمو -->
                <div>
                    <div class="p-4 border-b border-emerald-950/80 flex items-center justify-between">
                        <div class="flex items-center gap-3">
                            <div class="p-2 rounded-2xl bg-emerald-950/80 border border-emerald-500/30 shadow-inner flex items-center justify-center">
                                <img src="/logo.png" alt="لوگو لیمو" class="h-9 w-auto object-contain">
                            </div>
                            <div>
                                <span class="text-sm font-black text-white block leading-tight tracking-wide">
                                    کافی‌نت <span class="text-limo-400">لیمو</span>
                                </span>
                                <span class="text-[10px] text-emerald-400 font-medium block mt-0.5">پیشخوان فرماندهی و خدمات</span>
                            </div>
                        </div>
                        <button @click="mobileSidebarOpen = false" class="xl:hidden p-1.5 text-slate-400 hover:text-white rounded-lg">✕</button>
                    </div>

                    <!-- فهرست ماژول‌های مدیریتی دسته‌بندی‌شده -->
                    <nav class="p-3 space-y-4 text-xs font-bold overflow-y-auto max-h-[calc(100vh-12.5rem)]">
                        
                        <!-- بخش ۱: کارتابل و پردازش -->
                        <div class="space-y-1">
                            <span class="px-3 text-[10px] text-emerald-500/70 font-black tracking-wider uppercase block mb-1.5">
                                📌 کارتابل و پردازش
                            </span>
                            
                            <!-- پیشخوان آماری -->
                            <button @click="switchTab('overview')"
                                :class="{'border-r-4 border-limo-400 bg-gradient-to-l from-limo-500/20 via-emerald-500/10 to-transparent text-white font-black shadow-sm': currentTab === 'overview', 'text-slate-400 hover:bg-emerald-950/40 hover:text-white': currentTab !== 'overview'}"
                                class="w-full px-3 py-2 rounded-xl transition flex items-center justify-between text-right">
                                <span class="flex items-center gap-2.5">
                                    <span class="text-sm">📊</span>
                                    <span>پیشخوان و آمار</span>
                                </span>
                            </button>

                            <!-- سفارشات و پرونده‌ها -->
                            <button @click="switchTab('orders')"
                                :class="{'border-r-4 border-limo-400 bg-gradient-to-l from-limo-500/20 via-emerald-500/10 to-transparent text-white font-black shadow-sm': currentTab === 'orders', 'text-slate-400 hover:bg-emerald-950/40 hover:text-white': currentTab !== 'orders'}"
                                class="w-full px-3 py-2 rounded-xl transition flex items-center justify-between text-right">
                                <span class="flex items-center gap-2.5">
                                    <span class="text-sm">📦</span>
                                    <span>سفارشات و پرونده‌ها</span>
                                </span>
                                <span v-if="pendingCount > 0" class="bg-amber-400 text-slate-950 text-[10px] font-black px-2 py-0.5 rounded-full shadow-sm">
                                    {{ pendingCount }}
                                </span>
                            </button>

                            <!-- مدیریت مشتریان -->
                            <button @click="switchTab('customers')"
                                :class="{'border-r-4 border-limo-400 bg-gradient-to-l from-limo-500/20 via-emerald-500/10 to-transparent text-white font-black shadow-sm': currentTab === 'customers', 'text-slate-400 hover:bg-emerald-950/40 hover:text-white': currentTab !== 'customers'}"
                                class="w-full px-3 py-2 rounded-xl transition flex items-center justify-between text-right">
                                <span class="flex items-center gap-2.5">
                                    <span class="text-sm">👥</span>
                                    <span>مدیریت مراجعین (CRM)</span>
                                </span>
                                <span v-if="customers.length > 0" class="bg-emerald-950 text-emerald-300 text-[10px] px-2 py-0.5 rounded-full border border-emerald-800/40">
                                    {{ customers.length }}
                                </span>
                            </button>
                        </div>

                        <!-- بخش ۲: خدمات و سامانه‌ها -->
                        <div class="space-y-1 pt-1 border-t border-emerald-950/60">
                            <span class="px-3 text-[10px] text-emerald-500/70 font-black tracking-wider uppercase block mb-1.5 mt-2">
                                🛠️ خدمات و سامانه‌ها
                            </span>

                            <!-- خدمات و فرم‌ساز پویا -->
                            <button @click="switchTab('services')"
                                :class="{'border-r-4 border-limo-400 bg-gradient-to-l from-limo-500/20 via-emerald-500/10 to-transparent text-white font-black shadow-sm': currentTab === 'services', 'text-slate-400 hover:bg-emerald-950/40 hover:text-white': currentTab !== 'services'}"
                                class="w-full px-3 py-2 rounded-xl transition flex items-center justify-between text-right">
                                <span class="flex items-center gap-2.5">
                                    <span class="text-sm">🛠️</span>
                                    <span>خدمات و فرم‌ساز پویا</span>
                                </span>
                            </button>

                            <!-- دسته‌بندی خدمات -->
                            <button @click="switchTab('categories')"
                                :class="{'border-r-4 border-limo-400 bg-gradient-to-l from-limo-500/20 via-emerald-500/10 to-transparent text-white font-black shadow-sm': currentTab === 'categories', 'text-slate-400 hover:bg-emerald-950/40 hover:text-white': currentTab !== 'categories'}"
                                class="w-full px-3 py-2 rounded-xl transition flex items-center justify-between text-right">
                                <span class="flex items-center gap-2.5">
                                    <span class="text-sm">🏷️</span>
                                    <span>دسته‌بندی خدمات</span>
                                </span>
                            </button>

                            <!-- ثبت‌نام‌های مقطعی -->
                            <button @click="switchTab('seasonal')"
                                :class="{'border-r-4 border-limo-400 bg-gradient-to-l from-limo-500/20 via-emerald-500/10 to-transparent text-white font-black shadow-sm': currentTab === 'seasonal', 'text-slate-400 hover:bg-emerald-950/40 hover:text-white': currentTab !== 'seasonal'}"
                                class="w-full px-3 py-2 rounded-xl transition flex items-center justify-between text-right">
                                <span class="flex items-center gap-2.5">
                                    <span class="text-sm">📢</span>
                                    <span>ثبت‌نام‌های مقطعی</span>
                                </span>
                            </button>

                        </div>

                        <!-- بخش ۳: امور مشتریان و مالی -->
                        <div class="space-y-1 pt-1 border-t border-emerald-950/60">
                            <span class="px-3 text-[10px] text-emerald-500/70 font-black tracking-wider uppercase block mb-1.5 mt-2">
                                💬 امور مشتریان و مالی
                            </span>

                            <!-- گفتگوی زنده و تیکت‌ها -->
                            <button @click="switchTab('chats')"
                                :class="{'border-r-4 border-limo-400 bg-gradient-to-l from-limo-500/20 via-emerald-500/10 to-transparent text-white font-black shadow-sm': currentTab === 'chats', 'text-slate-400 hover:bg-emerald-950/40 hover:text-white': currentTab !== 'chats'}"
                                class="w-full px-3 py-2 rounded-xl transition flex items-center justify-between text-right">
                                <span class="flex items-center gap-2.5">
                                    <span class="text-sm">💬</span>
                                    <span>چت زنده و پشتیبانی</span>
                                </span>
                                <span v-if="pendingSupportCount > 0" class="bg-blue-500 text-white text-[10px] font-black px-2 py-0.5 rounded-full animate-pulse">
                                    {{ pendingSupportCount }}
                                </span>
                            </button>

                            <!-- کیف پول و تراکنش‌ها -->
                            <button @click="switchTab('wallets')"
                                :class="{'border-r-4 border-limo-400 bg-gradient-to-l from-limo-500/20 via-emerald-500/10 to-transparent text-white font-black shadow-sm': currentTab === 'wallets', 'text-slate-400 hover:bg-emerald-950/40 hover:text-white': currentTab !== 'wallets'}"
                                class="w-full px-3 py-2 rounded-xl transition flex items-center justify-between text-right">
                                <span class="flex items-center gap-2.5">
                                    <span class="text-sm">💳</span>
                                    <span>کیف پول و حساب‌ها</span>
                                </span>
                            </button>

                            <!-- راه‌های ارتباطی -->
                            <button @click="switchTab('channels')"
                                :class="{'border-r-4 border-limo-400 bg-gradient-to-l from-limo-500/20 via-emerald-500/10 to-transparent text-white font-black shadow-sm': currentTab === 'channels', 'text-slate-400 hover:bg-emerald-950/40 hover:text-white': currentTab !== 'channels'}"
                                class="w-full px-3 py-2 rounded-xl transition flex items-center justify-between text-right">
                                <span class="flex items-center gap-2.5">
                                    <span class="text-sm">📱</span>
                                    <span>راه‌های ارتباطی</span>
                                </span>
                            </button>
                        </div>

                        <!-- بخش ۴: سیستم، امنیت و پشتیبان‌گیری -->
                        <div class="space-y-1 pt-1 border-t border-emerald-950/60">
                            <span class="px-3 text-[10px] text-emerald-500/70 font-black tracking-wider uppercase block mb-1.5 mt-2">
                                ⚙️ سیستم و تنظیمات
                            </span>

                            <!-- سطل زباله ۳۰ روزه -->
                            <button @click="switchTab('trash')"
                                :class="{'border-r-4 border-limo-400 bg-gradient-to-l from-limo-500/20 via-emerald-500/10 to-transparent text-white font-black shadow-sm': currentTab === 'trash', 'text-slate-400 hover:bg-emerald-950/40 hover:text-white': currentTab !== 'trash'}"
                                class="w-full px-3 py-2 rounded-xl transition flex items-center justify-between text-right">
                                <span class="flex items-center gap-2.5">
                                    <span class="text-sm">🗑️</span>
                                    <span>سطل زباله (۳۰ روزه)</span>
                                </span>
                                <span v-if="trashItems.length > 0" class="bg-rose-500 text-white text-[10px] font-black px-2 py-0.5 rounded-full">
                                    {{ trashItems.length }}
                                </span>
                            </button>

                            <!-- پشتیبان‌گیری داده‌ها -->
                            <button @click="switchTab('backup')"
                                :class="{'border-r-4 border-limo-400 bg-gradient-to-l from-limo-500/20 via-emerald-500/10 to-transparent text-white font-black shadow-sm': currentTab === 'backup', 'text-slate-400 hover:bg-emerald-950/40 hover:text-white': currentTab !== 'backup'}"
                                class="w-full px-3 py-2 rounded-xl transition flex items-center justify-between text-right">
                                <span class="flex items-center gap-2.5">
                                    <span class="text-sm">💾</span>
                                    <span>پشتیبان‌گیری دیتابیس</span>
                                </span>
                            </button>

                            <!-- تنظیمات کافی‌نت و دسترسی‌ها -->
                            <button @click="switchTab('settings')"
                                :class="{'border-r-4 border-limo-400 bg-gradient-to-l from-limo-500/20 via-emerald-500/10 to-transparent text-white font-black shadow-sm': currentTab === 'settings', 'text-slate-400 hover:bg-emerald-950/40 hover:text-white': currentTab !== 'settings'}"
                                class="w-full px-3 py-2 rounded-xl transition flex items-center justify-between text-right">
                                <span class="flex items-center gap-2.5">
                                    <span class="text-sm">⚙️</span>
                                    <span>تنظیمات و دسترسی‌ها</span>
                                </span>
                            </button>
                        </div>
                    </nav>
                </div>

                <!-- بخش پایین سایدبار: مشخصات اپراتور و دکمه خروج امن -->
                <div class="p-3.5 border-t border-emerald-950/80 bg-black/40 space-y-2.5">
                    <div class="flex items-center gap-3">
                        <div class="w-8 h-8 rounded-xl bg-gradient-to-tr from-limo-600 to-lime-400 text-slate-950 flex items-center justify-center font-black text-xs shadow-md">
                            {{ (adminUser.username || 'A').charAt(0).toUpperCase() }}
                        </div>
                        <div class="overflow-hidden flex-1">
                            <span class="text-xs font-bold text-white block truncate">{{ adminUser.username || 'مدیر ارشد' }}</span>
                            <span class="text-[9px] text-emerald-400 font-medium flex items-center gap-1">
                                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
                                دسترسی فعال مدیریتی
                            </span>
                        </div>
                    </div>
                    <button @click="logout"
                        class="w-full py-2 px-3 bg-rose-950/30 hover:bg-rose-900/50 text-rose-300 border border-rose-800/30 rounded-xl text-xs font-bold transition flex items-center justify-center gap-2">
                        <span>خروج از سیستم</span>
                        <span>🚪</span>
                    </button>
                </div>
            </aside>

            <!-- محتوای اصلی داشبورد در سمت چپ سایدبار -->
            <div class="flex-1 xl:mr-68 min-h-screen flex flex-col bg-slate-100/90 transition-all main-scroll">
                
                <!-- نوار هدر مدرن با افکت شیشه‌ای و تاریخ شمسی -->
                <header class="glass-panel border-b border-slate-200/80 sticky top-0 z-30 shadow-sm px-4 sm:px-6 py-3 flex items-center justify-between">
                    <div class="flex items-center gap-3">
                        <!-- دکمه همبرگری باز کردن منو در موبایل -->
                        <button @click="mobileSidebarOpen = true"
                            class="xl:hidden p-2 bg-white hover:bg-slate-50 text-slate-700 rounded-xl transition border border-slate-200 shadow-sm">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
                            </svg>
                        </button>
                        
                        <div>
                            <div class="flex items-center gap-2">
                                <h2 class="text-sm sm:text-base font-black text-slate-900">{{ tabTitle(currentTab) }}</h2>
                                <span v-if="settingsForm.is_open === '1'" class="hidden md:inline-flex px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">🟢 کافی‌نت دایر است</span>
                                <span v-else-if="settingsForm.is_open === '0'" class="hidden md:inline-flex px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-100 text-rose-800">🔴 موقتاً بسته</span>
                            </div>
                            <span class="text-[11px] text-slate-400 font-mono hidden sm:block">{{ livePersianDate }}</span>
                        </div>
                    </div>

                    <!-- کنترل‌های سمت چپ هدر -->
                    <div class="flex items-center gap-2">
                        <!-- وضعیت اتصال پل مغازه -->
                        <div v-if="settingsForm.shop_sync_enabled === '1'" class="hidden lg:flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 text-blue-700 rounded-xl text-[11px] font-bold border border-blue-200">
                            <span class="text-xs">🔌</span>
                            <span>متصل به Cafinet_management</span>
                        </div>

                        <button @click="refreshCurrentTab" :disabled="isLoading" title="بروزرسانی داده‌ها"
                            class="p-2 text-slate-600 hover:text-limo-800 hover:bg-white bg-white/70 rounded-xl transition border border-slate-200 shadow-sm">
                            <span :class="{'animate-spin inline-block': isLoading}">🔄</span>
                        </button>
                        
                        <button @click="exportCSV" title="دانلود خروجی اکسل"
                            class="hidden sm:flex items-center gap-1.5 px-3 py-2 bg-white hover:bg-slate-50 text-slate-700 rounded-xl text-xs font-bold transition border border-slate-200 shadow-sm">
                            <span>📊 خروجی Excel</span>
                        </button>

                        <a href="https://t.me/limo_cafe_bot" target="_blank"
                            class="hidden md:flex items-center gap-1 px-3 py-2 bg-gradient-to-r from-limo-500 to-lime-600 hover:from-limo-400 hover:to-lime-500 text-slate-950 rounded-xl text-xs font-black transition shadow-sm">
                            <span>🤖 مشاهده ربات</span>
                        </a>
                    </div>
                </header>

                <!-- بدنه محتوای صفحات -->
                <main class="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 space-y-6">
'''
