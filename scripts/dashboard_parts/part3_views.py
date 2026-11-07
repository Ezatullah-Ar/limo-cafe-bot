# -*- coding: utf-8 -*-
# Part 3: Dashboard Views with Distinctive Visual Polish & Feature-Packed Settings

VIEWS_HTML = r'''
                <!-- ======================================================== -->
                <!-- ۱. ماژول پیشخوان و آمار (Overview) -->
                <!-- ======================================================== -->
                <div v-if="currentTab === 'overview'" class="space-y-6">
                    <!-- کارت‌های آمار اصلی با گرادیان‌های ملایم اختصاصی -->
                    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
                        <div class="bg-white rounded-3xl p-4 border border-slate-200/80 shadow-card-soft hover:shadow-card-hover transition-all">
                            <span class="text-[11px] text-slate-500 font-bold block">کل سفارشات ثبت‌شده</span>
                            <span class="text-2xl font-black text-slate-900 block mt-1.5 font-mono">{{ stats.total_orders }}</span>
                        </div>
                        <div class="bg-gradient-to-br from-amber-50 to-amber-100/40 rounded-3xl p-4 border border-amber-200/80 shadow-card-soft hover:shadow-card-hover transition-all">
                            <span class="text-[11px] text-amber-800 font-bold block">در انتظار بررسی</span>
                            <span class="text-2xl font-black text-amber-900 block mt-1.5 font-mono">{{ stats.pending_orders }}</span>
                        </div>
                        <div class="bg-gradient-to-br from-blue-50 to-blue-100/40 rounded-3xl p-4 border border-blue-200/80 shadow-card-soft hover:shadow-card-hover transition-all">
                            <span class="text-[11px] text-blue-800 font-bold block">در حال انجام</span>
                            <span class="text-2xl font-black text-blue-900 block mt-1.5 font-mono">{{ stats.approved_orders }}</span>
                        </div>
                        <div class="bg-gradient-to-br from-purple-50 to-purple-100/40 rounded-3xl p-4 border border-purple-200/80 shadow-card-soft hover:shadow-card-hover transition-all">
                            <span class="text-[11px] text-purple-800 font-bold block">نیازمند مدرک</span>
                            <span class="text-2xl font-black text-purple-900 block mt-1.5 font-mono">{{ stats.need_info_orders }}</span>
                        </div>
                        <div class="bg-gradient-to-br from-emerald-50 to-emerald-100/40 rounded-3xl p-4 border border-emerald-200/80 shadow-card-soft hover:shadow-card-hover transition-all">
                            <span class="text-[11px] text-emerald-800 font-bold block">تکمیل شده</span>
                            <span class="text-2xl font-black text-emerald-900 block mt-1.5 font-mono">{{ stats.completed_orders }}</span>
                        </div>
                        <div class="bg-gradient-to-br from-[#0b1f17] to-[#07140f] text-white rounded-3xl p-4 border border-emerald-900/40 shadow-card-soft hover:shadow-card-hover transition-all">
                            <span class="text-[11px] text-emerald-400 font-bold block">مراجعین CRM</span>
                            <span class="text-2xl font-black text-limo-400 block mt-1.5 font-mono">{{ stats.total_users }}</span>
                        </div>
                    </div>

                    <!-- ردیف دکمه‌های اقدام سریع (Quick Shortcuts) -->
                    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
                        <button @click="openNewCustomerModal" class="p-4 bg-white hover:bg-slate-50/80 rounded-3xl border border-slate-200/80 shadow-card-soft hover:shadow-card-hover text-right transition flex items-center gap-3">
                            <span class="p-2.5 bg-blue-100 text-blue-800 rounded-2xl text-base shadow-sm">➕</span>
                            <div>
                                <b class="text-xs text-slate-900 block">ثبت مراجع دستی</b>
                                <span class="text-[10px] text-slate-400">افزودن مستقیم به CRM</span>
                            </div>
                        </button>
                        <button @click="switchTab('services')" class="p-4 bg-white hover:bg-slate-50/80 rounded-3xl border border-slate-200/80 shadow-card-soft hover:shadow-card-hover text-right transition flex items-center gap-3">
                            <span class="p-2.5 bg-emerald-100 text-emerald-800 rounded-2xl text-base shadow-sm">📋</span>
                            <div>
                                <b class="text-xs text-slate-900 block">مدیریت خدمات و فرم‌ها</b>
                                <span class="text-[10px] text-slate-400">تنظیم کارمزد، اولویت و فیلدها</span>
                            </div>
                        </button>
                        <button @click="switchTab('chats')" class="p-4 bg-white hover:bg-slate-50/80 rounded-3xl border border-slate-200/80 shadow-card-soft hover:shadow-card-hover text-right transition flex items-center gap-3">
                            <span class="p-2.5 bg-indigo-100 text-indigo-800 rounded-2xl text-base shadow-sm">💬</span>
                            <div>
                                <b class="text-xs text-slate-900 block">چت زنده و پشتیبانی</b>
                                <span class="text-[10px] text-slate-400">پاسخ سریع به مراجعین</span>
                            </div>
                        </button>
                        <button @click="switchTab('settings')" class="p-4 bg-white hover:bg-slate-50/80 rounded-3xl border border-slate-200/80 shadow-card-soft hover:shadow-card-hover text-right transition flex items-center gap-3">
                            <span class="p-2.5 bg-limo-100 text-limo-900 rounded-2xl text-base shadow-sm">🔌</span>
                            <div>
                                <b class="text-xs text-slate-900 block">پل سیستم کافی‌نت</b>
                                <span class="text-[10px] text-slate-400">اتصال به Cafinet_management</span>
                            </div>
                        </button>
                    </div>

                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <!-- خلاصه آخرین سفارش‌ها -->
                        <div class="bg-white rounded-3xl p-5 border border-slate-200/80 shadow-card-soft space-y-4">
                            <div class="flex justify-between items-center">
                                <h3 class="font-black text-sm text-slate-900 flex items-center gap-2">
                                    <span>📦</span>
                                    <span>آخرین سفارش‌های ثبت‌شده</span>
                                </h3>
                                <button @click="switchTab('orders')" class="text-xs font-bold text-limo-700 hover:underline">کارتابل کامل ←</button>
                            </div>
                            <div class="overflow-x-auto">
                                <table class="w-full text-right text-xs">
                                    <thead>
                                        <tr class="text-slate-400 border-b border-slate-100">
                                            <th class="py-2.5 px-3">کد رهگیری</th>
                                            <th class="py-2.5 px-3">متقاضی</th>
                                            <th class="py-2.5 px-3">خدمت</th>
                                            <th class="py-2.5 px-3">وضعیت</th>
                                            <th class="py-2.5 px-3">عملیات</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr v-for="ord in orders.slice(0, 6)" :key="ord.id" class="border-b border-slate-50 hover:bg-slate-50/80 transition">
                                            <td class="py-2.5 px-3 font-mono font-bold text-slate-900">{{ ord.tracking_code }}</td>
                                            <td class="py-2.5 px-3">
                                                <button @click="openCustomerDossier({ id: ord.user_id, full_name: ord.full_name })"
                                                    class="font-bold text-blue-600 hover:underline text-right block">
                                                    {{ ord.full_name || 'کاربر تلگرام' }}
                                                </button>
                                            </td>
                                            <td class="py-2.5 px-3 text-slate-600 truncate max-w-[120px]">{{ ord.service_title }}</td>
                                            <td class="py-2.5 px-3">
                                                <span :class="statusBadgeClass(ord.status)" class="px-2.5 py-0.5 rounded-full text-[10px] font-bold">
                                                    {{ statusLabel(ord.status) }}
                                                </span>
                                            </td>
                                            <td class="py-2.5 px-3">
                                                <button @click="openOrderDetail(ord)" class="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-[11px] font-bold transition">
                                                    بررسی
                                                </button>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>

                        <!-- لیست مراجعین اخیر CRM (کلیک مستقیم جهت باز کردن پرونده) -->
                        <div class="bg-white rounded-3xl p-5 border border-slate-200/80 shadow-card-soft space-y-4">
                            <div class="flex justify-between items-center">
                                <h3 class="font-black text-sm text-slate-900 flex items-center gap-2">
                                    <span>👥</span>
                                    <span>مراجعین اخیر CRM (کلیک جهت باز کردن پرونده)</span>
                                </h3>
                                <button @click="switchTab('customers')" class="text-xs font-bold text-limo-700 hover:underline">مشاهده همه CRM ←</button>
                            </div>
                            <div class="divide-y divide-slate-100">
                                <div v-for="c in customers.slice(0, 6)" :key="c.id"
                                    @click="openCustomerDossier(c)"
                                    class="py-3 px-2 flex items-center justify-between hover:bg-slate-50/80 rounded-2xl cursor-pointer transition">
                                    <div class="flex items-center gap-3">
                                        <div class="w-10 h-10 rounded-2xl bg-gradient-to-tr from-emerald-950 to-slate-900 text-white flex items-center justify-center font-bold text-xs shadow-sm">
                                            👤
                                        </div>
                                        <div>
                                            <b class="text-xs text-slate-900 block">{{ c.full_name }}</b>
                                            <div class="text-[10px] text-slate-400 flex items-center gap-2 mt-0.5">
                                                <span v-if="c.username" class="text-blue-600 font-mono font-bold">@{{ c.username }}</span>
                                                <span v-else class="font-mono">ID: {{ c.telegram_id }}</span>
                                                <span v-if="c.phone_number" class="font-mono">| {{ c.phone_number }}</span>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="text-left">
                                        <span class="text-xs font-mono font-bold text-emerald-700 block">{{ formatTomans(c.wallet_balance) }}</span>
                                        <span class="text-[10px] text-slate-400">{{ c.order_count }} پرونده</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- ======================================================== -->
                <!-- ۲. ماژول سفارشات و پرونده‌ها (Orders) -->
                <!-- ======================================================== -->
                <div v-if="currentTab === 'orders'" class="space-y-4">
                    <!-- فیلترها و جستجوی سفارشات -->
                    <div class="flex flex-col md:flex-row gap-3 justify-between items-center bg-white p-4 rounded-3xl border border-slate-200/80 shadow-card-soft">
                        <div class="flex flex-wrap items-center gap-2 w-full md:w-auto">
                            <button @click="orderStatusFilter = 'ALL'" :class="{'bg-slate-900 text-white font-bold': orderStatusFilter === 'ALL', 'bg-slate-100 text-slate-600': orderStatusFilter !== 'ALL'}" class="px-3.5 py-1.5 rounded-xl text-xs transition">
                                همه ({{ orders.length }})
                            </button>
                            <button @click="orderStatusFilter = 'PENDING'" :class="{'bg-amber-500 text-slate-950 font-black': orderStatusFilter === 'PENDING', 'bg-slate-100 text-slate-600': orderStatusFilter !== 'PENDING'}" class="px-3.5 py-1.5 rounded-xl text-xs transition">
                                در انتظار بررسی ({{ orders.filter(o => o.status === 'PENDING').length }})
                            </button>
                            <button @click="orderStatusFilter = 'APPROVED'" :class="{'bg-blue-600 text-white font-bold': orderStatusFilter === 'APPROVED', 'bg-slate-100 text-slate-600': orderStatusFilter !== 'APPROVED'}" class="px-3.5 py-1.5 rounded-xl text-xs transition">
                                در حال انجام ({{ orders.filter(o => o.status === 'APPROVED').length }})
                            </button>
                            <button @click="orderStatusFilter = 'NEED_INFO'" :class="{'bg-purple-600 text-white font-bold': orderStatusFilter === 'NEED_INFO', 'bg-slate-100 text-slate-600': orderStatusFilter !== 'NEED_INFO'}" class="px-3.5 py-1.5 rounded-xl text-xs transition">
                                نقص مدرک ({{ orders.filter(o => o.status === 'NEED_INFO').length }})
                            </button>
                            <button @click="orderStatusFilter = 'COMPLETED'" :class="{'bg-emerald-600 text-white font-bold': orderStatusFilter === 'COMPLETED', 'bg-slate-100 text-slate-600': orderStatusFilter !== 'COMPLETED'}" class="px-3.5 py-1.5 rounded-xl text-xs transition">
                                تکمیل شده
                            </button>
                        </div>
                        <div class="w-full md:w-72">
                            <input v-model="orderSearchQuery" type="text" placeholder="جستجو کد رهگیری یا نام متقاضی..."
                                class="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:border-limo-500">
                        </div>
                    </div>

                    <!-- جدول سفارش‌ها مجهز به دکمه ارسال مستقیم به Cafinet_management -->
                    <div class="bg-white rounded-3xl border border-slate-200/80 shadow-card-soft overflow-hidden">
                        <div class="overflow-x-auto">
                            <table class="w-full text-right text-xs">
                                <thead>
                                    <tr class="bg-slate-50/80 text-slate-500 border-b border-slate-200">
                                        <th class="py-3.5 px-4 font-bold">کد رهگیری</th>
                                        <th class="py-3.5 px-4 font-bold">متقاضی (CRM)</th>
                                        <th class="py-3.5 px-4 font-bold">خدمت درخواستی</th>
                                        <th class="py-3.5 px-4 font-bold">وضعیت فعلی</th>
                                        <th class="py-3.5 px-4 font-bold">اپراتور مسئول</th>
                                        <th class="py-3.5 px-4 font-bold">تاریخ ثبت</th>
                                        <th class="py-3.5 px-4 font-bold text-center">عملیات</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-slate-100">
                                    <tr v-for="ord in filteredOrders" :key="ord.id" class="hover:bg-slate-50/80 transition">
                                        <td class="py-3.5 px-4 font-mono font-bold text-slate-900">{{ ord.tracking_code }}</td>
                                        <td class="py-3.5 px-4">
                                            <button @click="openCustomerDossier({ id: ord.user_id, full_name: ord.full_name })"
                                                class="font-bold text-blue-600 hover:underline block text-right">
                                                {{ ord.full_name || 'کاربر تلگرام' }}
                                            </button>
                                            <span class="text-[10px] text-slate-400 font-mono">{{ ord.telegram_id }}</span>
                                        </td>
                                        <td class="py-3.5 px-4 font-semibold text-slate-800">{{ ord.service_title }}</td>
                                        <td class="py-3.5 px-4">
                                            <span :class="statusBadgeClass(ord.status)" class="px-2.5 py-1 rounded-full text-[10px] font-bold inline-block">
                                                {{ statusLabel(ord.status) }}
                                            </span>
                                        </td>
                                        <td class="py-3.5 px-4">
                                            <span class="text-[11px] text-slate-600">{{ ord.assigned_operator_name || 'تخصیص‌نیافته' }}</span>
                                        </td>
                                        <td class="py-3.5 px-4 text-slate-400 font-mono text-[11px]">{{ formatDate(ord.created_at) }}</td>
                                        <td class="py-3.5 px-4">
                                            <div class="flex items-center justify-center gap-1.5">
                                                <button @click="openOrderDetail(ord)" class="px-3 py-1.5 bg-limo-100 hover:bg-limo-200 text-limo-950 rounded-xl font-bold text-[11px] transition">
                                                    بررسی پرونده
                                                </button>
                                                <!-- دکمه ارسال مستقیم سفارش به نرم‌افزار کافی‌نت -->
                                                <button @click="syncOrderToShop(ord.id)"
                                                    class="p-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-xl text-xs transition"
                                                    title="ارسال این سفارش به نرم‌افزار کافی‌نت (بخش سفارشات تلگرام)">
                                                    🔗
                                                </button>
                                                <button @click="softDeleteItem('order', ord.id, ord.tracking_code)" class="p-1.5 text-slate-400 hover:text-rose-600 rounded-xl transition" title="انتقال به سطل زباله">
                                                    🗑️
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                    <tr v-if="filteredOrders.length === 0">
                                        <td colspan="7" class="py-12 text-center text-slate-400 text-xs">سفارشی مطابق با فیلتر انتخابی یافت نشد.</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- ======================================================== -->
                <!-- ۳. ماژول مدیریت مراجعین (CRM) -->
                <!-- ======================================================== -->
                <div v-if="currentTab === 'customers'" class="space-y-4">
                    <div class="flex flex-col sm:flex-row gap-3 justify-between items-center bg-white p-4 rounded-3xl border border-slate-200/80 shadow-card-soft">
                        <div class="relative w-full sm:w-96">
                            <input v-model="customerSearchQuery" @input="debouncedFetchCustomers" type="text"
                                placeholder="جستجوی نام، موبایل، کدملی، شناسه یا یوزرنیم تلگرام..."
                                class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:border-limo-500">
                        </div>
                        <button @click="openNewCustomerModal"
                            class="w-full sm:w-auto px-5 py-2.5 bg-gradient-to-r from-limo-500 to-lime-600 hover:from-limo-400 hover:to-lime-500 text-slate-950 font-black rounded-xl text-xs transition shadow-sm flex items-center justify-center gap-2">
                            <span>➕</span>
                            <span>ثبت مشتری دستی جدید</span>
                        </button>
                    </div>

                    <div class="bg-white rounded-3xl border border-slate-200/80 shadow-card-soft overflow-hidden">
                        <div class="overflow-x-auto">
                            <table class="w-full text-right text-xs">
                                <thead>
                                    <tr class="bg-slate-50 text-slate-500 border-b border-slate-200">
                                        <th class="py-3.5 px-4 font-bold">نام و مشخصات متقاضی</th>
                                        <th class="py-3.5 px-4 font-bold">پروفایل تلگرام</th>
                                        <th class="py-3.5 px-4 font-bold">شماره تماس / کد ملی</th>
                                        <th class="py-3.5 px-4 font-bold">تعداد پرونده</th>
                                        <th class="py-3.5 px-4 font-bold">موجودی کیف پول</th>
                                        <th class="py-3.5 px-4 font-bold">تیکت‌های باز</th>
                                        <th class="py-3.5 px-4 font-bold text-center">عملیات CRM</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-slate-100">
                                    <tr v-for="c in customers" :key="c.id" class="hover:bg-slate-50 transition">
                                        <td class="py-3.5 px-4">
                                            <b class="text-slate-900 block text-xs">{{ c.full_name }}</b>
                                            <span class="text-[10px] text-slate-400 font-mono">عضویت: {{ formatDate(c.created_at) }}</span>
                                        </td>
                                        <td class="py-3.5 px-4">
                                            <div v-if="c.username">
                                                <a :href="'https://t.me/' + c.username" target="_blank" class="text-blue-600 hover:underline font-mono font-bold">
                                                    @{{ c.username }} ↗
                                                </a>
                                            </div>
                                            <div v-else class="text-slate-400 font-mono text-[11px]">بدون یوزرنیم</div>
                                            <span class="text-[10px] text-slate-500 font-mono">ID: {{ c.telegram_id }}</span>
                                        </td>
                                        <td class="py-3.5 px-4">
                                            <div class="font-mono text-slate-700">{{ c.phone_number || '---' }}</div>
                                            <div class="text-[10px] text-slate-400 font-mono" v-if="c.national_code">کدملی: {{ c.national_code }}</div>
                                            <div class="text-[10px] text-slate-400 font-mono" v-if="c.alien_code">فراگیر: {{ c.alien_code }}</div>
                                        </td>
                                        <td class="py-3.5 px-4">
                                            <span class="font-bold text-slate-800">{{ c.order_count }}</span>
                                            <span v-if="c.active_orders_count > 0" class="mr-1 text-[10px] bg-amber-100 text-amber-800 px-1.5 py-0.5 rounded font-bold">
                                                {{ c.active_orders_count }} جاری
                                            </span>
                                        </td>
                                        <td class="py-3.5 px-4">
                                            <b class="font-mono text-emerald-700">{{ formatTomans(c.wallet_balance) }}</b>
                                        </td>
                                        <td class="py-3.5 px-4">
                                            <span v-if="c.open_tickets_count > 0" class="bg-blue-100 text-blue-800 text-[10px] font-bold px-2 py-0.5 rounded-full">
                                                {{ c.open_tickets_count }} تیکت باز
                                            </span>
                                            <span v-else class="text-slate-400">---</span>
                                        </td>
                                        <td class="py-3.5 px-4">
                                            <div class="flex items-center justify-center gap-1.5">
                                                <button @click="openCustomerDossier(c)"
                                                    class="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl font-bold text-[11px] transition shadow-sm">
                                                    📁 پرونده کامل
                                                </button>
                                                <button @click="openDirectMsgModal(c)"
                                                    class="p-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-xl text-xs transition" title="ارسال پیام مستقیم ربات به تلگرام مشتری">
                                                    📩
                                                </button>
                                                <button @click="softDeleteItem('user', c.id, c.full_name)"
                                                    class="p-1.5 text-slate-400 hover:text-rose-600 rounded-xl transition" title="انتقال به سطل زباله">
                                                    🗑️
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                    <tr v-if="customers.length === 0">
                                        <td colspan="7" class="py-12 text-center text-slate-400 text-xs">مشتری با این مشخصات یافت نشد.</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- ======================================================== -->
                <!-- ۴. ماژول خدمات و فرم‌ساز پویا (Services & Form Builder) -->
                <!-- ======================================================== -->
                <div v-if="currentTab === 'services'" class="space-y-6">
                    <div class="flex flex-col sm:flex-row justify-between items-center gap-3 bg-white p-4 rounded-3xl border border-slate-200/80 shadow-card-soft">
                        <div class="flex flex-wrap items-center gap-2">
                            <button @click="serviceCategoryFilter = 'ALL'" :class="{'bg-slate-900 text-white': serviceCategoryFilter === 'ALL', 'bg-slate-100 text-slate-600': serviceCategoryFilter !== 'ALL'}" class="px-3 py-1.5 rounded-xl text-xs font-bold transition">
                                همه خدمات ({{ services.length }})
                            </button>
                            <button v-for="cat in categories" :key="cat.id" @click="serviceCategoryFilter = cat.id" :class="{'bg-slate-900 text-white': serviceCategoryFilter === cat.id, 'bg-slate-100 text-slate-600': serviceCategoryFilter !== cat.id}" class="px-3 py-1.5 rounded-xl text-xs font-bold transition">
                                {{ cat.title }}
                            </button>
                        </div>
                        <button @click="openNewServiceModal"
                            class="px-5 py-2.5 bg-gradient-to-r from-limo-500 to-lime-600 hover:from-limo-400 hover:to-lime-500 text-slate-950 font-black rounded-xl text-xs transition shadow-sm flex items-center gap-1.5">
                            <span>➕</span>
                            <span>تعریف خدمت جدید</span>
                        </button>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <div v-for="(s, index) in filteredServices" :key="s.id"
                        draggable="true"
                        @dragstart="onDragStart($event, index, 'services')"
                        @dragover.prevent="onDragOver($event, index)"
                        @drop="onDrop($event, index, 'services')"
                        @dragend="onDragEnd"
                        :class="{'ring-2 ring-limo-500 ring-offset-2': dragOverIndex === index && draggedType === 'services'}"
                        class="bg-white rounded-3xl p-5 border border-slate-200/80 shadow-card-soft space-y-4 hover:border-slate-300 transition cursor-grab active:cursor-grabbing select-none">
                            <div class="flex justify-between items-start">
                                <div>
                                    <span class="text-[10px] font-bold text-limo-900 bg-limo-100 px-2.5 py-0.5 rounded-full inline-block mb-1.5">
                                        {{ s.category_title || 'عمومی' }}
                                    </span>
                                    <h4 class="font-black text-sm text-slate-900">{{ s.title }}</h4>
                                    <span class="font-mono text-[10px] text-slate-400">{{ s.code }}</span>
                                </div>
                                <div class="flex items-center gap-1.5 bg-slate-50 border border-slate-200 rounded-xl px-2 py-1" title="تغییر اولویت (کشیدن و رها کردن یا تغییر عدد)">
                                    <span class="text-slate-400 hover:text-slate-600 font-bold select-none cursor-grab active:cursor-grabbing text-sm" title="برای جابه‌جایی بکشید و رها کنید">⠿</span>
                                    <span class="text-[10px] text-slate-400 font-bold">ترتیب:</span>
                                    <input type="number" v-model.number="s.order_priority" @change="updateItemPriority('services', s.id, s.order_priority)"
                                        class="w-12 text-center text-xs font-black bg-white border border-slate-200 rounded-lg py-0.5 focus:border-limo-500 focus:outline-none font-mono">
                                </div>
                                <button @click="toggleServiceActive(s)"
                                    :class="s.is_active ? 'bg-emerald-500' : 'bg-slate-300'"
                                    class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none">
                                    <span :class="s.is_active ? '-translate-x-5' : 'translate-x-0'" class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"></span>
                                </button>
                            </div>

                            <p class="text-xs text-slate-500 line-clamp-2 leading-relaxed">{{ s.description || 'توضیحاتی برای این خدمت ثبت نشده است.' }}</p>

                            <div class="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                                <div>
                                    <span class="text-[10px] text-slate-400 block">کارمزد پایه</span>
                                    <b class="font-mono text-slate-800">{{ formatTomans(s.base_fee) }}</b>
                                </div>
                                <div class="flex items-center gap-1.5">
                                    <button @click="editService(s)" class="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl text-xs transition">
                                        ✏️ فرم‌ساز و فیلدها
                                    </button>
                                    <button @click="softDeleteItem('service', s.id, s.title)" class="p-1.5 text-slate-400 hover:text-rose-600 rounded-xl transition" title="انتقال به سطل زباله">
                                        🗑️
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- ======================================================== -->
                <!-- ۵. ماژول دسته‌بندی خدمات (Categories CRUD) -->
                <!-- ======================================================== -->
                <div v-if="currentTab === 'categories'" class="space-y-4">
                    <div class="flex justify-between items-center bg-white p-4 rounded-3xl border border-slate-200/80 shadow-card-soft">
                        <div>
                            <h3 class="text-sm font-black text-slate-900">دسته‌بندی‌های خدمات کافی‌نت</h3>
                            <p class="text-xs text-slate-500">مدیریت، ایجاد، ویرایش و چیدمان اولویت دسته‌ها در مینی‌اپلیکیشن</p>
                        </div>
                        <button @click="openCategoriesModal"
                            class="px-5 py-2.5 bg-gradient-to-r from-limo-500 to-lime-600 hover:from-limo-400 hover:to-lime-500 text-slate-950 font-black rounded-xl text-xs transition shadow-sm flex items-center gap-1.5">
                            <span>➕</span>
                            <span>دسته‌بندی جدید</span>
                        </button>
                    </div>

                    <div class="bg-white rounded-3xl border border-slate-200/80 shadow-card-soft overflow-hidden">
                        <div class="overflow-x-auto">
                            <table class="w-full text-right text-xs">
                            <thead>
                                <tr class="bg-slate-50 text-slate-500 border-b border-slate-200">
                                    <th class="py-3.5 px-4 font-bold">شناسه / کد</th>
                                    <th class="py-3.5 px-4 font-bold">عنوان دسته‌بندی</th>
                                    <th class="py-3.5 px-4 font-bold">توضیحات</th>
                                    <th class="py-3.5 px-4 font-bold">اولویت نمایش</th>
                                    <th class="py-3.5 px-4 font-bold text-center">وضعیت</th>
                                    <th class="py-3.5 px-4 font-bold text-center">عملیات</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100">
                                <tr v-for="(cat, index) in categories" :key="cat.id"
                                    draggable="true"
                                    @dragstart="onDragStart($event, index, 'categories')"
                                    @dragover.prevent="onDragOver($event, index)"
                                    @drop="onDrop($event, index, 'categories')"
                                    @dragend="onDragEnd"
                                    :class="{'bg-limo-50': dragOverIndex === index && draggedType === 'categories'}"
                                    class="hover:bg-slate-50 transition cursor-grab active:cursor-grabbing select-none">
                                    <td class="py-3 px-4 font-mono font-bold text-slate-900">{{ cat.code }}</td>
                                    <td class="py-3 px-4 font-bold text-slate-800">{{ cat.title }}</td>
                                    <td class="py-3 px-4 text-slate-500">{{ cat.description || '---' }}</td>
                                    <td class="py-3 px-4 font-mono">{{ cat.order_priority || 0 }}</td>
                                    <td class="py-3 px-4 text-center">
                                        <button @click="toggleCategoryStatus(cat)" :class="cat.is_active ? 'bg-emerald-500' : 'bg-slate-300'" class="relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full transition-colors duration-200 ease-in-out focus:outline-none" title="تغییر وضعیت فعال/غیرفعال">
                                            <span :class="cat.is_active ? '-translate-x-4' : 'translate-x-0'" class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-lg ring-0 transition duration-200 ease-in-out"></span>
                                        </button>
                                    </td>
                                    <td class="py-3 px-4 text-center">
                                        <div class="flex items-center justify-center gap-2">
                                            <div class="flex items-center justify-center gap-1 bg-slate-50 border border-slate-200 rounded-lg px-1.5 py-0.5" title="تغییر اولویت (کشیدن و رها کردن یا تغییر عدد)">
                                                <span class="text-slate-400 hover:text-slate-600 font-bold select-none cursor-grab active:cursor-grabbing text-sm" title="برای جابه‌جایی بکشید و رها کنید">⠿</span>
                                                <input type="number" v-model.number="cat.order_priority" @change="updateItemPriority('categories', cat.id, cat.order_priority)"
                                                    class="w-11 text-center text-xs font-black bg-white border border-slate-200 rounded py-0.5 focus:border-limo-500 focus:outline-none font-mono">
                                            </div>
                                            <button @click="editCategory(cat)" class="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-bold transition">
                                                ویرایش ✏️
                                            </button>
                                            <button @click="softDeleteItem('category', cat.id, cat.title)" class="p-1.5 text-slate-400 hover:text-rose-600 rounded-lg transition" title="انتقال به سطل زباله">
                                                🗑️
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                        </div>
                    </div>
                </div>

                <!-- ======================================================== -->
                <!-- ۶. ماژول کیف پول و امور مالی (Wallets) -->
                <!-- ======================================================== -->
                <div v-if="currentTab === 'wallets'" class="space-y-6">
                    <div class="flex justify-between items-center bg-white p-4 rounded-3xl border border-slate-200/80 shadow-card-soft">
                        <div>
                            <h3 class="text-sm font-black text-slate-900">کیف پول متقاضیان و دفاتر مالی</h3>
                            <p class="text-xs text-slate-500">مشاهده مانده، شارژ دستی حساب و ثبت تراکنش‌های مالی</p>
                        </div>
                        <button @click="openAdjustModal(null)"
                            class="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-black rounded-xl text-xs transition shadow-sm flex items-center gap-1.5">
                            <span>💳</span>
                            <span>شارژ یا کسر دستی موجودی</span>
                        </button>
                    </div>

                    <div class="bg-white rounded-3xl border border-slate-200/80 shadow-card-soft overflow-hidden">
                        <div class="overflow-x-auto">
                            <table class="w-full text-right text-xs">
                            <thead>
                                <tr class="bg-slate-50 text-slate-500 border-b border-slate-200">
                                    <th class="py-3.5 px-4 font-bold">مشتری</th>
                                    <th class="py-3.5 px-4 font-bold">شناسه تلگرام</th>
                                    <th class="py-3.5 px-4 font-bold">موجودی فعلی</th>
                                    <th class="py-3.5 px-4 font-bold">تعداد تراکنش</th>
                                    <th class="py-3.5 px-4 font-bold">وضعیت حساب</th>
                                    <th class="py-3.5 px-4 font-bold text-center">عملیات مالی</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100">
                                <tr v-for="w in wallets" :key="w.id" class="hover:bg-slate-50 transition">
                                    <td class="py-3 px-4 font-bold text-slate-900">{{ w.full_name }}</td>
                                    <td class="py-3 px-4 font-mono text-slate-600">{{ w.telegram_id }}</td>
                                    <td class="py-3 px-4">
                                        <b class="font-mono text-emerald-700 text-sm">{{ formatTomans(w.balance) }}</b>
                                    </td>
                                    <td class="py-3 px-4 font-mono">{{ w.tx_count || 0 }} تراکنش</td>
                                    <td class="py-3 px-4">
                                        <span :class="w.is_frozen ? 'bg-rose-100 text-rose-800' : 'bg-emerald-100 text-emerald-800'" class="px-2 py-0.5 rounded-full text-[10px] font-bold">
                                            {{ w.is_frozen ? 'مسدود' : 'فعال' }}
                                        </span>
                                    </td>
                                    <td class="py-3 px-4 text-center">
                                        <div class="flex items-center justify-center gap-1.5">
                                            <button @click="openAdjustModal(w)" class="px-2.5 py-1.5 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 rounded-lg text-xs font-bold transition">
                                                شارژ / کسر ➕
                                            </button>
                                            <button @click="toggleFreezeWallet(w)" class="px-2.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-bold transition">
                                                {{ w.is_frozen ? 'رفع مسدودی' : 'مسدودسازی' }}
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                        </div>
                    </div>
                </div>

                <!-- ======================================================== -->
                <!-- ۷. ماژول ثبت‌نام‌های مقطعی (Seasonal Campaigns) -->
                <!-- ======================================================== -->
                <div v-if="currentTab === 'seasonal'" class="space-y-6">
                    <div class="flex justify-between items-center bg-white p-4 rounded-3xl border border-slate-200/80 shadow-card-soft">
                        <div>
                            <h3 class="text-sm font-black text-slate-900">ثبت‌نام‌های مقطعی، کنکور و آزمون‌ها</h3>
                            <p class="text-xs text-slate-500">مدیریت رویدادهای فصلی و ارسال اطلاعیه عمومی به متقاضیان</p>
                        </div>
                        <button @click="openNewCampaignModal"
                            class="px-5 py-2.5 bg-gradient-to-r from-limo-500 to-lime-600 hover:from-limo-400 hover:to-lime-500 text-slate-950 font-black rounded-xl text-xs transition shadow-sm flex items-center gap-1.5">
                            <span>➕</span>
                            <span>ایجاد ثبت‌نام مقطعی جدید</span>
                        </button>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <div v-for="(c, index) in seasonalCampaigns" :key="c.id"
                        draggable="true"
                        @dragstart="onDragStart($event, index, 'campaigns')"
                        @dragover.prevent="onDragOver($event, index)"
                        @drop="onDrop($event, index, 'campaigns')"
                        @dragend="onDragEnd"
                        :class="{'ring-2 ring-limo-500 ring-offset-2': dragOverIndex === index && draggedType === 'campaigns'}"
                        class="bg-white rounded-3xl p-5 border border-slate-200/80 shadow-card-soft space-y-4 hover:border-slate-300 transition cursor-grab active:cursor-grabbing select-none">
                            <div class="flex justify-between items-start">
                                <div>
                                    <span :class="seasonalBadgeClass(c.status)" class="px-2 py-0.5 rounded-full text-[10px] font-bold inline-block mb-1">
                                        {{ seasonalStatusLabel(c.status) }}
                                    </span>
                                    <h4 class="font-black text-sm text-slate-900">{{ c.title }}</h4>
                                    <span class="font-mono text-[10px] text-slate-400">{{ c.code }}</span>
                                </div>
                                <div class="flex items-center gap-1.5 bg-slate-50 border border-slate-200 rounded-xl px-2 py-1" title="تغییر اولویت (کشیدن و رها کردن یا تغییر عدد)">
                                    <span class="text-slate-400 hover:text-slate-600 font-bold select-none cursor-grab active:cursor-grabbing text-sm" title="برای جابه‌جایی بکشید و رها کنید">⠿</span>
                                    <span class="text-[10px] text-slate-400 font-bold">ترتیب:</span>
                                    <input type="number" v-model.number="c.order_priority" @change="updateItemPriority('campaigns', c.id, c.order_priority)"
                                        class="w-12 text-center text-xs font-black bg-white border border-slate-200 rounded-lg py-0.5 focus:border-limo-500 focus:outline-none font-mono">
                                </div>
                                <button @click="toggleSeasonalActive(c)"
                                    :class="c.is_active ? 'bg-emerald-500' : 'bg-slate-300'"
                                    class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none">
                                    <span :class="c.is_active ? '-translate-x-5' : 'translate-x-0'" class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"></span>
                                </button>
                            </div>

                            <p class="text-xs text-slate-500 line-clamp-2 leading-relaxed">{{ c.description || 'توضیحات ندارد.' }}</p>

                            <div class="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                                <div class="font-mono text-slate-600 text-[11px]">
                                    {{ c.start_at ? formatDate(c.start_at) : '---' }}
                                </div>
                                <div class="flex items-center gap-1.5">
                                    <button @click="editCampaign(c)" class="px-2.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl text-xs transition">
                                        ویرایش ✏️
                                    </button>
                                    <button @click="openBroadcastModal(c)" class="p-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg text-xs transition" title="ارسال اطلاعیه عمومی">
                                        📢
                                    </button>
                                    <button @click="softDeleteItem('campaign', c.id, c.title)" class="p-1.5 text-slate-400 hover:text-rose-600 rounded-lg transition" title="انتقال به سطل زباله">
                                        🗑️
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- ======================================================== -->
                <!-- ۸. ماژول گفتگوی زنده و تیکت‌ها (Chats & Support) -->
                <!-- ======================================================== -->
                <div v-if="currentTab === 'chats'" class="space-y-4">
                    <div class="bg-white rounded-3xl border border-slate-200/80 shadow-card-soft overflow-hidden flex flex-col md:flex-row h-[75vh]">
                        <!-- ستون راست: لیست تیکت‌ها -->
                        <div class="w-full md:w-80 border-b md:border-b-0 md:border-l border-slate-200 flex flex-col bg-slate-50/60">
                            <div class="p-4 border-b border-slate-200 bg-white">
                                <h3 class="font-black text-sm text-slate-800">مکالمات پشتیبانی</h3>
                                <p class="text-[11px] text-slate-400">تیکت‌های ارسال شده از ربات و وب</p>
                            </div>
                            <div class="flex-1 overflow-y-auto divide-y divide-slate-100">
                                <div v-for="th in supportThreads" :key="th.id"
                                    @click="selectThread(th)"
                                    :class="selectedThread?.id === th.id ? 'bg-blue-50/80 border-r-4 border-blue-600' : 'hover:bg-slate-100/60'"
                                    class="p-3.5 cursor-pointer transition text-xs space-y-1">
                                    <div class="flex justify-between items-center">
                                        <b class="text-slate-900 truncate">{{ th.full_name || 'کاربر تلگرام' }}</b>
                                        <span :class="supportStatusBadgeClass(th.status)" class="px-2 py-0.5 rounded-full text-[9px] font-bold">
                                            {{ supportStatusLabel(th.status) }}
                                        </span>
                                    </div>
                                    <p class="text-[11px] text-slate-500 truncate">{{ th.last_message || 'پیامی نیست' }}</p>
                                    <div class="text-[10px] text-slate-400 flex items-center justify-between font-mono">
                                        <span>تیکت #{{ th.id }}</span>
                                        <span>{{ formatDate(th.updated_at) }}</span>
                                    </div>
                                </div>
                                <div v-if="supportThreads.length === 0" class="p-8 text-center text-slate-400 text-xs">
                                    مکالمه فعالی وجود ندارد.
                                </div>
                            </div>
                        </div>

                        <!-- ستون چپ: پنجره چت فعال با هدر کامل مشخصات تلگرام متقاضی -->
                        <div class="flex-1 flex flex-col bg-white">
                            <div v-if="selectedThread" class="flex-1 flex flex-col h-full">
                                <!-- هدر چت با نمایش آیدی و پروفایل تلگرام -->
                                <div class="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/70">
                                    <div class="flex items-center gap-3">
                                        <div class="w-10 h-10 rounded-2xl bg-gradient-to-tr from-emerald-950 to-slate-900 text-white flex items-center justify-center font-black text-sm shadow-sm">
                                            {{ (selectedThread.full_name || 'U').charAt(0) }}
                                        </div>
                                        <div>
                                            <div class="flex items-center gap-2">
                                                <b class="text-sm text-slate-900">{{ selectedThread.full_name }}</b>
                                                <a v-if="selectedThread.username" :href="'https://t.me/' + selectedThread.username" target="_blank"
                                                    class="text-xs text-blue-600 hover:underline font-mono font-bold">
                                                    @{{ selectedThread.username }} ↗
                                                </a>
                                            </div>
                                            <div class="text-[11px] text-slate-500 font-mono flex items-center gap-2 mt-0.5">
                                                <span>شناسه تلگرام: <code>{{ selectedThread.telegram_id }}</code></span>
                                                <span v-if="selectedThread.user_id">| کاربر #{{ selectedThread.user_id }}</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div class="flex items-center gap-2">
                                        <button @click="openCustomerDossier({ id: selectedThread.user_id, full_name: selectedThread.full_name })"
                                            class="px-3 py-1.5 bg-slate-200 hover:bg-slate-300 text-slate-800 rounded-xl text-xs font-bold transition">
                                            📁 پرونده کامل
                                        </button>
                                        <select v-model="selectedThread.status" @change="changeThreadStatus(selectedThread.id, selectedThread.status)"
                                            class="px-2.5 py-1.5 bg-white border border-slate-200 rounded-xl text-xs font-bold text-slate-700">
                                            <option value="PENDING_OPERATOR">در انتظار اپراتور</option>
                                            <option value="PENDING_CUSTOMER">در انتظار مشتری</option>
                                            <option value="CLOSED">بسته شده</option>
                                        </select>
                                    </div>
                                </div>

                                <!-- لیست پیام‌های چت -->
                                <div class="flex-1 p-4 overflow-y-auto space-y-3 bg-slate-50/40">
                                    <div v-for="msg in threadMessages" :key="msg.id"
                                        :class="msg.sender_role === 'OPERATOR' ? 'mr-auto text-left' : 'ml-auto text-right'"
                                        class="max-w-[75%] space-y-1">
                                        <div :class="msg.sender_role === 'OPERATOR' ? 'bg-gradient-to-r from-limo-500 to-lime-600 text-slate-950 font-bold' : 'bg-white border border-slate-200 text-slate-800'"
                                            class="p-3 rounded-2xl text-xs leading-relaxed shadow-sm">
                                            {{ msg.message_text }}
                                        </div>
                                        <span class="text-[10px] text-slate-400 block px-1 font-mono">
                                            {{ formatDate(msg.created_at) }}
                                        </span>
                                    </div>
                                    <div v-if="threadMessages.length === 0" class="text-center py-12 text-slate-400 text-xs">
                                        پیامی در این مکالمه موجود نیست.
                                    </div>
                                </div>

                                <!-- جعبه ارسال پیام پاسخ -->
                                <form @submit.prevent="sendSupportReply" class="p-3 border-t border-slate-200 bg-white flex gap-2">
                                    <input v-model="supportReplyText" type="text" placeholder="پاسخ خود به مشتری را بنویسید (مستقیماً در تلگرام ارسال می‌شود)..."
                                        class="flex-1 px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:border-limo-500">
                                    <button type="submit" :disabled="!supportReplyText.trim() || isSendingReply"
                                        class="px-5 py-2.5 bg-gradient-to-r from-limo-500 to-lime-600 hover:from-limo-400 hover:to-lime-500 text-slate-950 font-black rounded-xl text-xs transition shadow-sm flex items-center gap-1.5">
                                        <span>ارسال به تلگرام</span>
                                        <span>🚀</span>
                                    </button>
                                </form>
                            </div>
                            <div v-else class="flex-1 flex items-center justify-center text-slate-400 text-xs">
                                یک مکالمه را از ستون راست انتخاب فرمایید.
                            </div>
                        </div>
                    </div>
                </div>

                <!-- ======================================================== -->
                <!-- ۱۰. ماژول راه‌های ارتباطی (Communication Channels) -->
                <!-- ======================================================== -->
                <div v-if="currentTab === 'channels'" class="space-y-4">
                    <div class="flex justify-between items-center bg-white p-4 rounded-3xl border border-slate-200/80 shadow-card-soft">
                        <div>
                            <h3 class="text-sm font-black text-slate-900">کانال‌های ارتباطی و تماس کافی‌نت</h3>
                            <p class="text-xs text-slate-500">مدیریت راه‌های ارتباطی و فعال / غیرفعال‌سازی آنی دکمه‌ها</p>
                        </div>
                    </div>

                    <div class="bg-white rounded-3xl border border-slate-200/80 shadow-card-soft overflow-hidden">
                        <div class="overflow-x-auto">
                            <table class="w-full text-right text-xs">
                            <thead>
                                <tr class="bg-slate-50 text-slate-500 border-b border-slate-200">
                                    <th class="py-3.5 px-4 font-bold">عنوان کانال</th>
                                    <th class="py-3.5 px-4 font-bold">کلید سیستم</th>
                                    <th class="py-3.5 px-4 font-bold">مقدار / شماره / لینک</th>
                                    <th class="py-3.5 px-4 font-bold">وضعیت فعال بودن</th>
                                    <th class="py-3.5 px-4 font-bold text-center">عملیات</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100">
                                <tr v-for="(ch, index) in communicationChannels" :key="ch.id"
                                    draggable="true"
                                    @dragstart="onDragStart($event, index, 'channels')"
                                    @dragover.prevent="onDragOver($event, index)"
                                    @drop="onDrop($event, index, 'channels')"
                                    @dragend="onDragEnd"
                                    :class="{'bg-limo-50': dragOverIndex === index && draggedType === 'channels'}"
                                    class="hover:bg-slate-50 transition cursor-grab active:cursor-grabbing select-none">
                                    <td class="py-3 px-4 font-bold text-slate-900">{{ ch.title }}</td>
                                    <td class="py-3 px-4 font-mono text-slate-400">{{ ch.key }}</td>
                                    <td class="py-3 px-4 font-mono text-slate-700">{{ ch.value || '---' }}</td>
                                    <td class="py-3 px-4">
                                        <div class="flex items-center gap-1.5 bg-slate-50 border border-slate-200 rounded-xl px-2 py-1" title="تغییر اولویت (کشیدن و رها کردن یا تغییر عدد)">
                                            <span class="text-slate-400 hover:text-slate-600 font-bold select-none cursor-grab active:cursor-grabbing text-sm" title="برای جابه‌جایی بکشید و رها کنید">⠿</span>
                                            <span class="text-[10px] text-slate-400 font-bold">ترتیب:</span>
                                            <input type="number" v-model.number="ch.order_priority" @change="updateItemPriority('channels', ch.id, ch.order_priority)"
                                                class="w-12 text-center text-xs font-black bg-white border border-slate-200 rounded-lg py-0.5 focus:border-limo-500 focus:outline-none font-mono">
                                        </div>
                                <button @click="toggleChannelActive(ch)"
                                            :class="ch.is_active ? 'bg-emerald-500' : 'bg-slate-300'"
                                            class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none">
                                            <span :class="ch.is_active ? '-translate-x-5' : 'translate-x-0'" class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"></span>
                                        </button>
                                    </td>
                                    <td class="py-3 px-4 text-center">
                                        <div class="flex items-center justify-center gap-2">
                                            <button @click="openChannelEdit(ch)" class="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-bold transition">
                                                ویرایش ✏️
                                            </button>
                                            <button @click="softDeleteItem('channel', ch.id, ch.title)" class="p-1.5 text-slate-400 hover:text-rose-600 rounded-lg transition" title="انتقال به سطل زباله">
                                                🗑️
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                        </div>
                    </div>
                </div>

                <!-- ======================================================== -->
                <!-- ۱۱. ماژول سطل زباله ۳۰ روزه (Soft Delete Trash) -->
                <!-- ======================================================== -->
                <div v-if="currentTab === 'trash'" class="space-y-4">
                    <div class="p-4 bg-amber-50 border border-amber-200 rounded-3xl flex items-center justify-between text-xs text-amber-900 shadow-card-soft">
                        <div class="flex items-center gap-3">
                            <span class="text-2xl">🗑️</span>
                            <div>
                                <b class="block font-bold">بایگانی موقت و سطل زباله ۳۰ روزه لیمو</b>
                                <span class="text-[11px] text-amber-700">تمام موارد حذف‌شده به مدت ۳۰ روز در این بخش نگهداری می‌شوند و امکان بازگردانی ۱-کلیکه دارند. پس از ۳۰ روز به طور خودکار پاک‌سازی دائمی خواهند شد.</span>
                            </div>
                        </div>
                        <button @click="fetchTrashItems" class="px-4 py-2 bg-amber-200/70 hover:bg-amber-200 text-amber-950 rounded-xl font-bold transition shadow-sm">
                            بروزرسانی لیست 🔄
                        </button>
                    </div>

                    <div class="bg-white rounded-3xl border border-slate-200/80 shadow-card-soft overflow-hidden">
                        <div class="overflow-x-auto">
                            <table class="w-full text-right text-xs">
                            <thead>
                                <tr class="bg-slate-50 text-slate-500 border-b border-slate-200">
                                    <th class="py-3.5 px-4 font-bold">نوع موجودیت</th>
                                    <th class="py-3.5 px-4 font-bold">عنوان / کد رهگیری</th>
                                    <th class="py-3.5 px-4 font-bold">مشخصات</th>
                                    <th class="py-3.5 px-4 font-bold">تاریخ حذف</th>
                                    <th class="py-3.5 px-4 font-bold">مهلت تا پاک‌سازی دائمی</th>
                                    <th class="py-3.5 px-4 font-bold text-center">عملیات بازیابی / حذف</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100">
                                <tr v-for="item in trashItems" :key="item.table + '-' + item.id" class="hover:bg-slate-50 transition">
                                    <td class="py-3 px-4">
                                        <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-700">
                                            {{ item.type_label }}
                                        </span>
                                    </td>
                                    <td class="py-3 px-4 font-bold text-slate-900">{{ item.title || item.code }}</td>
                                    <td class="py-3 px-4 text-slate-500 font-mono text-[11px]">{{ item.subtitle || item.code || '---' }}</td>
                                    <td class="py-3 px-4 text-slate-400 font-mono">{{ formatDate(item.deleted_at) }}</td>
                                    <td class="py-3 px-4">
                                        <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200 font-mono">
                                            ⏳ {{ item.days_left }} روز مانده
                                        </span>
                                    </td>
                                    <td class="py-3 px-4 text-center">
                                        <div class="flex items-center justify-center gap-2">
                                            <button @click="restoreTrashItem(item)"
                                                class="px-3 py-1 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 rounded-lg text-xs font-bold transition flex items-center gap-1">
                                                <span>♻️</span>
                                                <span>بازیابی</span>
                                            </button>
                                            <button @click="purgeTrashItem(item)"
                                                class="px-2.5 py-1 bg-rose-50 hover:bg-rose-100 text-rose-700 rounded-lg text-xs font-bold transition flex items-center gap-1">
                                                <span>⛔</span>
                                                <span>حذف دائمی</span>
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                                <tr v-if="trashItems.length === 0">
                                    <td colspan="6" class="py-12 text-center text-slate-400 text-xs">سطل زباله خالی است. هیچ موردی حذف نشده است.</td>
                                </tr>
                            </tbody>
                        </table>
                        </div>
                    </div>
                </div>

                <!-- ======================================================== -->
                <!-- ۱۲. ماژول پشتیبان‌گیری و خروجی داده (Backup & Export) -->
                <!-- ======================================================== -->
                <div v-if="currentTab === 'backup'" class="space-y-6">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div class="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-card-soft space-y-4">
                            <div class="w-12 h-12 rounded-2xl bg-limo-100 text-limo-900 flex items-center justify-center text-2xl font-black shadow-sm">
                                💾
                            </div>
                            <div>
                                <h3 class="font-black text-sm text-slate-900">دریافت نسخه پشتیبان کامل (JSON Dump)</h3>
                                <p class="text-xs text-slate-500 mt-1 leading-relaxed">
                                    پشتیبان‌گیری جامع ۱-کلیکه از تمام جداول پایگاه داده D1 شامل کاربران، سفارشات، تیکت‌ها، خدمات، ثبت‌نام‌های مقطعی، کیف پول و تنظیمات سیستم.
                                </p>
                            </div>
                            <button @click="exportFullBackup" :disabled="isExportingBackup"
                                class="w-full py-3 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-2xl text-xs transition flex items-center justify-center gap-2 shadow-sm">
                                <span v-if="isExportingBackup" class="animate-spin text-sm">⏳</span>
                                <span>📥 دانلود فایل پشتیبان دیتابیس (JSON)</span>
                            </button>
                        </div>

                        <div class="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-card-soft space-y-4">
                            <div class="w-12 h-12 rounded-2xl bg-emerald-100 text-emerald-800 flex items-center justify-center text-2xl font-black shadow-sm">
                                📊
                            </div>
                            <div>
                                <h3 class="font-black text-sm text-slate-900">خروجی اکسل سفارش‌ها (CSV)</h3>
                                <p class="text-xs text-slate-500 mt-1 leading-relaxed">
                                    دریافت لیست تمام سفارش‌های ثبت‌شده با کد رهگیری، مشخصات کامل متقاضی، شماره تماس و وضعیت با فرمت سازگار با نرم‌افزار Excel.
                                </p>
                            </div>
                            <button @click="exportCSV"
                                class="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-2xl text-xs transition flex items-center justify-center gap-2 shadow-sm">
                                <span>📊 دانلود فایل اکسل سفارش‌ها (CSV)</span>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- ======================================================== -->
                <!-- ۱۳. ماژول تنظیمات جامع، ویژگی‌ها و دسترسی‌ها (Settings & Features) -->
                <!-- ======================================================== -->
                <div v-if="currentTab === 'settings'" class="space-y-6">
                    
                    <!-- تب‌های داخلی بخش تنظیمات -->
                    <div class="bg-white p-2 rounded-2xl border border-slate-200/80 shadow-card-soft flex flex-wrap gap-1 text-xs font-bold">
                        <button @click="settingsActiveSubTab = 'business'"
                            :class="settingsActiveSubTab === 'business' ? 'bg-slate-900 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'"
                            class="px-4 py-2 rounded-xl transition flex items-center gap-1.5">
                            <span>🏢 هویت کسب‌وکار و حضور</span>
                        </button>
                        <button @click="settingsActiveSubTab = 'rbac'"
                            :class="settingsActiveSubTab === 'rbac' ? 'bg-slate-900 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'"
                            class="px-4 py-2 rounded-xl transition flex items-center gap-1.5">
                            <span>🔑 اپراتورها و سطوح دسترسی</span>
                        </button>
                        <button @click="settingsActiveSubTab = 'sync'"
                            :class="settingsActiveSubTab === 'sync' ? 'bg-slate-900 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'"
                            class="px-4 py-2 rounded-xl transition flex items-center gap-1.5">
                            <span>🔌 اتصال به Cafinet_management</span>
                        </button>
                        <button @click="settingsActiveSubTab = 'finance'"
                            :class="settingsActiveSubTab === 'finance' ? 'bg-slate-900 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'"
                            class="px-4 py-2 rounded-xl transition flex items-center gap-1.5">
                            <span>💳 امور مالی و حساب‌ها</span>
                        </button>
                        <button @click="settingsActiveSubTab = 'system'"
                            :class="settingsActiveSubTab === 'system' ? 'bg-slate-900 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'"
                            class="px-4 py-2 rounded-xl transition flex items-center gap-1.5">
                            <span>🛡️ سیستم، فایل‌ها و امنیت</span>
                        </button>
                    </div>

                    <!-- بخش ۱: هویت کسب‌وکار و حضور -->
                    <div v-if="settingsActiveSubTab === 'business'" class="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-card-soft space-y-6">
                        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 pb-4 border-b border-slate-100">
                            <div>
                                <h3 class="font-black text-sm text-slate-900">هویت، اطلاعات کاری و وضعیت حضور کافی‌نت</h3>
                                <p class="text-xs text-slate-500 mt-0.5">تنظیم ساعات کاری رسمی، خطوط پشتیبانی و وضعیت فعالیت جاری</p>
                            </div>
                            <!-- کلید وضعیت فوری باز/بسته بودن کافی‌نت -->
                            <div class="flex items-center gap-2 p-2 bg-slate-50 rounded-2xl border border-slate-200">
                                <span class="text-xs font-bold text-slate-700">وضعیت حضور:</span>
                                <button @click="settingsForm.is_open = '1'"
                                    :class="settingsForm.is_open === '1' ? 'bg-emerald-600 text-white font-black' : 'bg-white text-slate-600'"
                                    class="px-3 py-1 rounded-xl text-xs transition shadow-sm">
                                    🟢 باز است
                                </button>
                                <button @click="settingsForm.is_open = '0'"
                                    :class="settingsForm.is_open === '0' ? 'bg-rose-600 text-white font-black' : 'bg-white text-slate-600'"
                                    class="px-3 py-1 rounded-xl text-xs transition shadow-sm">
                                    🔴 تعطیل موقت
                                </button>
                            </div>
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                            <div class="space-y-1.5">
                                <label class="block font-bold text-slate-700">نام نمایشی کافی‌نت</label>
                                <input v-model="settingsForm.shop_title" type="text" placeholder="کافی‌نت آنلاین لیمو"
                                    class="w-full px-4 py-2.5 border border-slate-200 rounded-xl">
                            </div>
                            <div class="space-y-1.5">
                                <label class="block font-bold text-slate-700">ساعات کاری و فعالیت رسمی</label>
                                <input v-model="settingsForm.business_hours" type="text" placeholder="شنبه تا پنج‌شنبه: ۸:۳۰ الی ۲۱:۰۰"
                                    class="w-full px-4 py-2.5 border border-slate-200 rounded-xl">
                            </div>
                            <div class="space-y-1.5">
                                <label class="block font-bold text-slate-700">شماره تماس ثابت دفتر</label>
                                <input v-model="settingsForm.support_phones" type="text" placeholder="021-xxxxxxxx"
                                    class="w-full px-4 py-2.5 border border-slate-200 rounded-xl font-mono">
                            </div>
                            <div class="space-y-1.5">
                                <label class="block font-bold text-slate-700">شماره همراه پشتیبانی و خط اضطراری</label>
                                <input v-model="settingsForm.emergency_phone" type="text" placeholder="0912xxxxxxx"
                                    class="w-full px-4 py-2.5 border border-slate-200 rounded-xl font-mono">
                            </div>
                            <div class="space-y-1.5 md:col-span-2">
                                <label class="block font-bold text-slate-700">نشانی فیزیکی دفتر کافی‌نت</label>
                                <input v-model="settingsForm.shop_address" type="text" placeholder="تهران، خیابان آزادی، پلاک ..."
                                    class="w-full px-4 py-2.5 border border-slate-200 rounded-xl">
                            </div>
                            <!-- ویرایشگر محتوای صفحه درباره ما در مینی‌اپلیکیشن -->
                            <div class="space-y-1.5 md:col-span-2 p-4 bg-slate-50 rounded-2xl border border-slate-200">
                                <div class="flex justify-between items-center mb-1">
                                    <label class="block font-bold text-slate-800 text-xs">📖 محتوای صفحه «درباره ما» در مینی‌اپلیکیشن</label>
                                    <span class="text-[10px] text-slate-400 font-medium">قابل ویرایش مستقیم و نمایش لحظه‌ای به مشتریان</span>
                                </div>
                                <textarea v-model="settingsForm.about_us_content" rows="4" placeholder="معرفی کافی‌نت لیمو، تعهدات، سوابق و استانداردهای خدمات..."
                                    class="w-full px-4 py-3 border border-slate-200 rounded-xl bg-white text-xs leading-relaxed"></textarea>
                            </div>

                            <!-- تنظیم موشن‌گرافیک مینی‌اپلیکیشن -->
                            <div class="space-y-1.5 md:col-span-2 p-4 bg-slate-50 rounded-2xl border border-slate-200 flex items-center justify-between">
                                <div>
                                    <span class="font-bold text-slate-800 text-xs block">✨ انیمیشن‌ها و موشن‌گرافیک مینی‌اپلیکیشن</span>
                                    <span class="text-[10px] text-slate-400 block mt-0.5">افکت‌های بصری شناور و پالس آنلاین برای جذابیت بیشتر</span>
                                </div>
                                <label class="relative inline-flex items-center cursor-pointer">
                                    <input type="checkbox" v-model="settingsForm.motion_graphics_enabled" true-value="1" false-value="0" class="sr-only peer">
                                    <div class="w-11 h-6 bg-slate-300 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:right-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-600"></div>
                                </label>
                            </div>
                        </div>

                        <div class="pt-4 border-t border-slate-100 flex justify-end">
                            <button @click="saveShopSettings" :disabled="isSavingSettings"
                                class="px-6 py-2.5 bg-gradient-to-r from-limo-500 to-lime-600 hover:from-limo-400 hover:to-lime-500 text-slate-950 font-black rounded-xl text-xs transition shadow-sm">
                                ذخیره اطلاعات کسب‌وکار
                            </button>
                        </div>
                    </div>

                    <!-- بخش ۲: اپراتورها و سطوح دسترسی (RBAC) -->
                    <div v-if="settingsActiveSubTab === 'rbac'" class="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-card-soft space-y-6">
                        <div class="flex justify-between items-center pb-4 border-b border-slate-100">
                            <div>
                                <h3 class="font-black text-sm text-slate-900">مدیریت اپراتورها و سطوح دسترسی به پنل</h3>
                                <p class="text-xs text-slate-500 mt-0.5">تعریف و تخصیص نقش‌های مدیریتی (مدیر کل، اپراتور ثبت‌نام، پشتیبان چت، حسابدار)</p>
                            </div>
                            <button @click="openNewOperatorModal"
                                class="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-xl text-xs transition shadow-sm flex items-center gap-1.5">
                                <span>➕</span>
                                <span>افزودن اپراتور جدید</span>
                            </button>
                        </div>

                        <!-- جدول اپراتورها -->
                        <div class="overflow-x-auto">
                            <table class="w-full text-right text-xs">
                                <thead>
                                    <tr class="bg-slate-50 text-slate-500 border-b border-slate-200">
                                        <th class="py-3 px-4 font-bold">نام اپراتور</th>
                                        <th class="py-3 px-4 font-bold">نام کاربری ورود</th>
                                        <th class="py-3 px-4 font-bold">سطح دسترسی (نقش)</th>
                                        <th class="py-3 px-4 font-bold">وضعیت حساب</th>
                                        <th class="py-3 px-4 font-bold">تاریخ ایجاد</th>
                                        <th class="py-3 px-4 font-bold text-center">عملیات</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-slate-100">
                                    <tr v-for="op in operatorsList" :key="op.id" class="hover:bg-slate-50 transition">
                                        <td class="py-3 px-4 font-bold text-slate-900">{{ op.full_name }}</td>
                                        <td class="py-3 px-4 font-mono text-slate-600">{{ op.username }}</td>
                                        <td class="py-3 px-4">
                                            <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold"
                                                :class="op.role === 'SUPER_ADMIN' ? 'bg-purple-100 text-purple-800' : (op.role === 'SUPPORT' ? 'bg-blue-100 text-blue-800' : 'bg-slate-100 text-slate-700')">
                                                {{ op.role_title || op.role }}
                                            </span>
                                        </td>
                                        <td class="py-3 px-4">
                                            <span :class="op.is_active ? 'text-emerald-700 bg-emerald-50 border-emerald-200' : 'text-rose-700 bg-rose-50 border-rose-200'" class="px-2 py-0.5 rounded-full text-[10px] font-bold border">
                                                {{ op.is_active ? 'فعال' : 'غیرفعال' }}
                                            </span>
                                        </td>
                                        <td class="py-3 px-4 text-slate-400 font-mono text-[11px]">{{ op.created_at || '---' }}</td>
                                        <td class="py-3 px-4 text-center">
                                            <button v-if="op.id !== 1" @click="deleteOperator(op.id)"
                                                class="px-2.5 py-1 bg-rose-50 hover:bg-rose-100 text-rose-700 rounded-lg text-xs font-bold transition">
                                                حذف دسترسی 🗑️
                                            </button>
                                            <span v-else class="text-[10px] text-slate-400 font-bold">غیرقابل‌حذف (مالک)</span>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- بخش ۳: پل اتصال و یکپارچه‌سازی با Cafinet_management -->
                    <div v-if="settingsActiveSubTab === 'sync'" class="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-card-soft space-y-6">
                        <div class="flex items-center justify-between pb-4 border-b border-slate-100">
                            <div class="flex items-center gap-3">
                                <div class="w-12 h-12 rounded-2xl bg-blue-100 text-blue-800 flex items-center justify-center text-2xl font-black shadow-sm">
                                    🔌
                                </div>
                                <div>
                                    <h3 class="font-black text-sm text-slate-900">یکپارچه‌سازی با نرم‌افزار مغازه (Cafinet_management)</h3>
                                    <p class="text-xs text-slate-500 mt-0.5">ارسال آنی سفارشات دریافتی از ربات تلگرام به کارتابل سفارشات نرم‌افزار کافی‌نت مستقر روی سیستم</p>
                                </div>
                            </div>

                            <!-- کلید فعال‌سازی همگام‌سازی -->
                            <label class="relative inline-flex items-center cursor-pointer">
                                <input type="checkbox" v-model="settingsForm.shop_sync_enabled" true-value="1" false-value="0" class="sr-only peer">
                                <div class="w-11 h-6 bg-slate-300 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:right-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                            </label>
                        </div>

                        <div class="grid grid-cols-1 gap-4 text-xs">
                            <div class="space-y-1.5">
                                <label class="block font-bold text-slate-700">نشانی وب‌هوک سفارشات نرم‌افزار کافی‌نت (Webhook Ingestion URL)</label>
                                <div class="flex gap-2">
                                    <input v-model="settingsForm.shop_sync_url" type="url" placeholder="http://localhost:3000/api/bot-orders"
                                        class="flex-1 px-4 py-2.5 border border-slate-200 rounded-xl font-mono text-xs focus:outline-none focus:border-blue-500">
                                    <button @click="testShopSyncConnection" :disabled="isTestingSync"
                                        class="px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl text-xs transition shadow-sm flex items-center gap-1.5">
                                        <span v-if="isTestingSync" class="animate-spin text-sm">⏳</span>
                                        <span>⚡ تست اتصال زنده</span>
                                    </button>
                                </div>
                                <span class="text-[10px] text-slate-400 block mt-1 leading-relaxed">
                                    نکته: در صورتی که نرم‌افزار کافی‌نت روی رایانه مغازه اجرا شده است، نشانی پیش‌فرض <code>http://localhost:3000/api/bot-orders</code> یا نشانی تونل کلودفلر آن را وارد فرمایید.
                                </span>
                            </div>

                            <!-- نتیجه آخرین تست اتصال -->
                            <div v-if="syncTestResult" :class="syncTestResult.ok ? 'bg-emerald-50 border-emerald-200 text-emerald-900' : 'bg-rose-50 border-rose-200 text-rose-900'"
                                class="p-3.5 rounded-2xl border text-xs flex items-center justify-between">
                                <div class="flex items-center gap-2">
                                    <span>{{ syncTestResult.ok ? '✅' : '❌' }}</span>
                                    <b>{{ syncTestResult.message }}</b>
                                </div>
                                <span v-if="syncTestResult.latency_ms" class="font-mono font-bold">{{ syncTestResult.latency_ms }}ms</span>
                            </div>
                        </div>

                        <div class="pt-4 border-t border-slate-100 flex justify-end">
                            <button @click="saveShopSettings" :disabled="isSavingSettings"
                                class="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-black rounded-xl text-xs transition shadow-sm">
                                ذخیره تنظیمات پل ارتباطی
                            </button>
                        </div>
                    </div>

                    <!-- بخش ۴: امور مالی و شماره حساب‌ها -->
                    <div v-if="settingsActiveSubTab === 'finance'" class="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-card-soft space-y-6">
                        <div class="pb-4 border-b border-slate-100">
                            <h3 class="font-black text-sm text-slate-900">تنظیمات مالی و حساب‌های بانکی</h3>
                            <p class="text-xs text-slate-500 mt-0.5">مشخصات کارت جهت واریز متقاضیان و سقف‌های مجاز شارژ کیف پول</p>
                        </div>

                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                            <div class="space-y-1.5">
                                <label class="block font-bold text-slate-700">شماره کارت بانکی پیش‌فرض (۱۶ رقم)</label>
                                <input v-model="settingsForm.card_number" type="text" placeholder="6037-xxxx-xxxx-xxxx"
                                    class="w-full px-4 py-2.5 border border-slate-200 rounded-xl font-mono text-sm tracking-wider">
                            </div>
                            <div class="space-y-1.5">
                                <label class="block font-bold text-slate-700">نام کامل دارنده کارت</label>
                                <input v-model="settingsForm.card_holder_name" type="text" placeholder="کافی‌نت لیمو / نام صاحب حساب"
                                    class="w-full px-4 py-2.5 border border-slate-200 rounded-xl">
                            </div>
                            <div class="space-y-1.5">
                                <label class="block font-bold text-slate-700">شماره شبا بانکی (IR)</label>
                                <input v-model="settingsForm.card_iban" type="text" placeholder="IRxxxxxxxxxxxxxxxxxxxx"
                                    class="w-full px-4 py-2.5 border border-slate-200 rounded-xl font-mono">
                            </div>
                            <div class="space-y-1.5">
                                <label class="block font-bold text-slate-700">حداقل مبلغ شارژ کیف پول (تومان)</label>
                                <input v-model.number="settingsForm.min_wallet_topup" type="number" placeholder="10000"
                                    class="w-full px-4 py-2.5 border border-slate-200 rounded-xl font-mono">
                            </div>
                        </div>

                        <div class="pt-4 border-t border-slate-100 flex justify-end">
                            <button @click="saveShopSettings" :disabled="isSavingSettings"
                                class="px-6 py-2.5 bg-gradient-to-r from-limo-500 to-lime-600 hover:from-limo-400 hover:to-lime-500 text-slate-950 font-black rounded-xl text-xs transition shadow-sm">
                                ذخیره اطلاعات بانکی و مالی
                            </button>
                        </div>
                    </div>

                    <!-- بخش ۵: سیستم، فایل‌ها و امنیت -->
                    <div v-if="settingsActiveSubTab === 'system'" class="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-card-soft space-y-6">
                        <div class="pb-4 border-b border-slate-100">
                            <h3 class="font-black text-sm text-slate-900">تنظیمات سیستم، سقف آپلود و اعلان‌های تلگرام</h3>
                            <p class="text-xs text-slate-500 mt-0.5">پیکربندی اعلان‌های خودکار بات، سقف حجم مدارک و حالت تعمیرات</p>
                        </div>

                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                            <div class="space-y-1.5">
                                <label class="block font-bold text-slate-700">سقف حجم مجاز آپلود مدارک (مگابایت)</label>
                                <input v-model.number="settingsForm.max_upload_size_mb" type="number" placeholder="15"
                                    class="w-full px-4 py-2.5 border border-slate-200 rounded-xl font-mono">
                            </div>
                            <div class="space-y-1.5">
                                <label class="block font-bold text-slate-700">شناسه عددی تلگرام مدیر (ADMIN_ID جهت اعلان‌های فوری)</label>
                                <input v-model="settingsForm.admin_tg_id" type="number" placeholder="مثال: 123456789"
                                    class="w-full px-4 py-2.5 border border-slate-200 rounded-xl font-mono">
                            </div>
                            <div class="space-y-1.5 md:col-span-2">
                                <label class="block font-bold text-slate-700">فرمت‌های مجاز مدارک</label>
                                <input v-model="settingsForm.allowed_file_types" type="text" placeholder="jpg, jpeg, png, pdf, zip"
                                    class="w-full px-4 py-2.5 border border-slate-200 rounded-xl font-mono">
                            </div>
                        </div>

                        <div class="pt-4 border-t border-slate-100 flex justify-end">
                            <button @click="saveShopSettings" :disabled="isSavingSettings"
                                class="px-6 py-2.5 bg-gradient-to-r from-limo-500 to-lime-600 hover:from-limo-400 hover:to-lime-500 text-slate-950 font-black rounded-xl text-xs transition shadow-sm">
                                ذخیره تنظیمات سیستمی
                            </button>
                        </div>
                    </div>

                </div>

                </main>
            </div>
        </div>
'''
