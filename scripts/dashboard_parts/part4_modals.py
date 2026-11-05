# -*- coding: utf-8 -*-
# Part 4: Admin Dashboard Modals (Dossier, Order Details with Shop Sync, Service Form Builder, Operators, etc.)

MODALS_HTML = r'''
        <!-- ======================================================== -->
        <!-- مودال ۱: پرونده جامع مشتری (Customer Dossier Modal) -->
        <!-- ======================================================== -->
        <div v-if="selectedDossier" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm">
            <div class="bg-white rounded-3xl max-w-4xl w-full max-h-[92vh] flex flex-col shadow-2xl border border-slate-100 text-right overflow-hidden">
                <!-- سربرگ پرونده مشتری با اطلاعات هویتی و تلگرام -->
                <div class="p-6 border-b border-slate-100 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-slate-50/80">
                    <div class="flex items-center gap-3">
                        <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-emerald-950 to-slate-900 text-white flex items-center justify-center font-black text-base shadow-sm">
                            👤
                        </div>
                        <div>
                            <div class="flex items-center gap-2">
                                <h3 class="font-black text-base text-slate-900">{{ selectedDossier.user.full_name }}</h3>
                                <span class="text-[10px] bg-slate-200 text-slate-700 px-2.5 py-0.5 rounded-full font-bold">{{ selectedDossier.user.role }}</span>
                            </div>
                            <div class="text-xs text-slate-500 mt-1 flex flex-wrap items-center gap-2">
                                <span v-if="selectedDossier.user.username" class="font-mono text-blue-600 font-bold">@{{ selectedDossier.user.username }}</span>
                                <span class="font-mono">شناسه تلگرام: <code>{{ selectedDossier.user.telegram_id }}</code></span>
                                <span v-if="selectedDossier.user.phone_number" class="font-mono">| همراه: {{ selectedDossier.user.phone_number }}</span>
                            </div>
                        </div>
                    </div>

                    <!-- دکمه‌های اقدام سریع در هدر پرونده -->
                    <div class="flex items-center gap-2 w-full sm:w-auto justify-end">
                        <button @click="openDirectMsgModal(selectedDossier.user)"
                            class="px-3 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-bold transition flex items-center gap-1 shadow-sm">
                            <span>📩</span>
                            <span>ارسال پیام از طرف ربات</span>
                        </button>
                        <a v-if="selectedDossier.user.username" :href="'https://t.me/' + selectedDossier.user.username" target="_blank"
                            class="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold transition flex items-center gap-1 border border-slate-200">
                            <span>✈️</span>
                            <span>چت در تلگرام</span>
                        </a>
                        <button @click="selectedDossier = null" class="p-2 text-slate-400 hover:text-slate-600 rounded-xl">✕</button>
                    </div>
                </div>

                <!-- نوار مالی مشتری با امکان شارژ مستقیم -->
                <div class="px-6 py-3 bg-emerald-50/60 border-b border-emerald-100/60 flex justify-between items-center text-xs">
                    <div class="flex items-center gap-3">
                        <span class="text-slate-600">موجودی کیف پول:</span>
                        <b class="font-mono text-sm text-emerald-800">{{ formatTomans(selectedDossier.wallet.balance) }}</b>
                        <span :class="selectedDossier.wallet.is_frozen ? 'bg-rose-100 text-rose-800' : 'bg-emerald-100 text-emerald-800'" class="px-2 py-0.5 rounded-full text-[10px] font-bold">
                            {{ selectedDossier.wallet.is_frozen ? 'مسدود' : 'فعال' }}
                        </span>
                    </div>
                    <button @click="openAdjustModal(selectedDossier.wallet, selectedDossier.user)"
                        class="px-3 py-1.5 bg-emerald-700 hover:bg-emerald-600 text-white rounded-lg font-bold text-xs transition shadow-sm flex items-center gap-1">
                        <span>➕</span>
                        <span>شارژ / کسر دستی کیف پول</span>
                    </button>
                </div>

                <!-- تب‌های پرونده مشتری -->
                <div class="flex border-b border-slate-200 px-6 gap-3 text-xs font-bold text-slate-500 bg-white overflow-x-auto">
                    <button @click="dossierTab = 'orders'" :class="{'text-limo-800 border-b-2 border-limo-600 py-3': dossierTab === 'orders'}" class="py-3 whitespace-nowrap transition">
                        سفارشات متقاضی ({{ selectedDossier.orders.length }})
                    </button>
                    <button @click="dossierTab = 'chat'" :class="{'text-limo-800 border-b-2 border-limo-600 py-3': dossierTab === 'chat'}" class="py-3 whitespace-nowrap transition">
                        🗨️ گفتگوی زنده دوطرفه درون پرونده
                    </button>
                    <button @click="dossierTab = 'info'" :class="{'text-limo-800 border-b-2 border-limo-600 py-3': dossierTab === 'info'}" class="py-3 whitespace-nowrap transition">
                        📝 اطلاعات هویتی و یادداشت‌ها
                    </button>
                    <button @click="dossierTab = 'transactions'" :class="{'text-limo-800 border-b-2 border-limo-600 py-3': dossierTab === 'transactions'}" class="py-3 whitespace-nowrap transition">
                        تراکنش‌های کیف پول ({{ selectedDossier.transactions.length }})
                    </button>
                    <button @click="dossierTab = 'threads'" :class="{'text-limo-800 border-b-2 border-limo-600 py-3': dossierTab === 'threads'}" class="py-3 whitespace-nowrap transition">
                        تیکت‌های ثبت‌شده ({{ selectedDossier.support_threads.length }})
                    </button>
                    <button @click="dossierTab = 'logs'" :class="{'text-limo-800 border-b-2 border-limo-600 py-3': dossierTab === 'logs'}" class="py-3 whitespace-nowrap transition">
                        لاگ‌های حسابرسی ({{ selectedDossier.audit_logs.length }})
                    </button>
                </div>

                <!-- محتوای تب‌های پرونده -->
                <div class="p-6 overflow-y-auto flex-1 space-y-4">
                    <!-- تب سفارش‌های متقاضی -->
                    <div v-if="dossierTab === 'orders'" class="space-y-3">
                        <div v-if="selectedDossier.orders.length === 0" class="text-center py-8 text-slate-400 text-xs">سفارشی برای این متقاضی ثبت نشده است.</div>
                        <div v-for="ord in selectedDossier.orders" :key="ord.id" class="p-4 bg-slate-50 rounded-2xl border border-slate-200 text-xs space-y-2 hover:border-slate-300 transition">
                            <div class="flex justify-between items-center">
                                <b class="font-mono text-slate-900 text-sm">{{ ord.tracking_code }} - {{ ord.service_title }}</b>
                                <div class="flex items-center gap-2">
                                    <span :class="statusBadgeClass(ord.status)" class="px-2.5 py-0.5 rounded-full text-[10px] font-bold">{{ statusLabel(ord.status) }}</span>
                                    <button @click="openOrderDetail(ord)" class="px-3 py-1 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-bold transition">
                                        👁️ مشاهده جزییات
                                    </button>
                                </div>
                            </div>
                            <div class="text-[11px] text-slate-500">یادداشت اپراتور: {{ ord.operator_notes || 'ندارد' }}</div>
                            <div class="text-[10px] text-slate-400 font-mono">ثبت: {{ formatDate(ord.created_at) }}</div>
                        </div>
                    </div>

                    <!-- تب گفتگوی زنده دوطرفه درون پرونده مشتری -->
                    <div v-if="dossierTab === 'chat'" class="space-y-4">
                        <div class="p-3 bg-blue-50 border border-blue-200 rounded-xl text-xs text-blue-900">
                            💬 <b>پنل چت اختصاصی با {{ selectedDossier.user.full_name }}:</b> پیام‌های ارسالی از این بخش مستقیماً به پی‌وی تلگرام مشتری مخابره و در تاریخچه مکالمات ذخیره می‌شود.
                        </div>

                        <div class="border border-slate-200 rounded-2xl p-4 h-64 overflow-y-auto space-y-3 bg-slate-50/50">
                            <div v-for="m in dossierChatMessages" :key="m.id"
                                :class="m.sender_role === 'OPERATOR' ? 'mr-auto text-left' : 'ml-auto text-right'"
                                class="max-w-[80%] space-y-1">
                                <div :class="m.sender_role === 'OPERATOR' ? 'bg-gradient-to-r from-limo-500 to-lime-600 text-slate-950 font-bold' : 'bg-white border border-slate-200 text-slate-800'"
                                    class="p-2.5 rounded-xl text-xs shadow-sm leading-relaxed">
                                    {{ m.message_text }}
                                </div>
                                <span class="text-[10px] text-slate-400 block px-1 font-mono">{{ formatDate(m.created_at) }}</span>
                            </div>
                            <div v-if="dossierChatMessages.length === 0" class="text-center py-12 text-slate-400 text-xs">
                                هنوز مکالمه‌ای با این مشتری انجام نشده است.
                            </div>
                        </div>

                        <form @submit.prevent="sendDossierChatReply" class="flex gap-2">
                            <input v-model="dossierReplyText" type="text" placeholder="متن پیام جهت ارسال مستقیم به تلگرام مشتری..."
                                class="flex-1 px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:border-limo-500">
                            <button type="submit" :disabled="!dossierReplyText.trim() || isSendingDossierReply"
                                class="px-5 py-2.5 bg-gradient-to-r from-limo-500 to-lime-600 hover:from-limo-400 hover:to-lime-500 text-slate-950 font-black rounded-xl text-xs transition shadow-sm flex items-center gap-1.5">
                                <span>ارسال فوری</span>
                                <span>🚀</span>
                            </button>
                        </form>
                    </div>

                    <!-- تب اطلاعات هویتی و یادداشت‌ها -->
                    <div v-if="dossierTab === 'info'" class="space-y-4">
                        <form @submit.prevent="saveCustomerInfo" class="space-y-4">
                            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                                <div>
                                    <label class="block font-bold text-slate-700 mb-1">نام و نام خانوادگی</label>
                                    <input v-model="customerEditForm.full_name" type="text" required
                                        class="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs">
                                </div>
                                <div>
                                    <label class="block font-bold text-slate-700 mb-1">شماره همراه</label>
                                    <input v-model="customerEditForm.phone_number" type="tel"
                                        class="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs font-mono">
                                </div>
                                <div>
                                    <label class="block font-bold text-slate-700 mb-1">کد ملی</label>
                                    <input v-model="customerEditForm.national_code" type="text"
                                        class="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs font-mono">
                                </div>
                                <div>
                                    <label class="block font-bold text-slate-700 mb-1">کد فراگیر اتباع (در صورت وجود)</label>
                                    <input v-model="customerEditForm.alien_code" type="text"
                                        class="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs font-mono">
                                </div>
                                <div>
                                    <label class="block font-bold text-slate-700 mb-1">نام کاربری تلگرام (Username)</label>
                                    <input v-model="customerEditForm.username" type="text" placeholder="بدون @"
                                        class="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs font-mono">
                                </div>
                                <div>
                                    <label class="block font-bold text-slate-700 mb-1">شناسه یکتای تلگرام (Telegram ID)</label>
                                    <input :value="selectedDossier.user.telegram_id" type="text" disabled
                                        class="w-full px-3 py-2 bg-slate-100 border border-slate-200 rounded-xl text-xs font-mono text-slate-500">
                                </div>
                            </div>
                            <div>
                                <label class="block text-xs font-bold text-slate-700 mb-1">یادداشت‌های داخلی و توضیحات پرونده</label>
                                <textarea v-model="customerEditForm.notes" rows="3" placeholder="یادداشت‌های ویژه اپراتور در خصوص این مشتری..."
                                    class="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs"></textarea>
                            </div>
                            <div class="flex justify-between items-center pt-2">
                                <button type="button" @click="softDeleteItem('user', selectedDossier.user.id, selectedDossier.user.full_name)"
                                    class="px-3 py-2 bg-rose-50 hover:bg-rose-100 text-rose-700 rounded-xl text-xs font-bold transition">
                                    🗑️ انتقال مشتری به سطل زباله
                                </button>
                                <button type="submit" :disabled="isSavingCustomer"
                                    class="px-5 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold transition">
                                    ذخیره تغییرات مشخصات
                                </button>
                            </div>
                        </form>
                    </div>

                    <!-- تب تراکنش‌های مالی -->
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

                    <!-- تب تیکت‌های پشتیبانی -->
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

                    <!-- تب لاگ‌های حسابرسی -->
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

        <!-- ======================================================== -->
        <!-- مودال ۲: ایجاد دستی مشتری جدید (New Customer Modal) -->
        <!-- ======================================================== -->
        <div v-if="newCustomerModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm">
            <div class="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-slate-100 text-right space-y-4">
                <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                    <h3 class="font-black text-sm text-slate-900">➕ ثبت مشتری جدید در CRM</h3>
                    <button @click="newCustomerModal = false" class="p-1 text-slate-400 hover:text-slate-600">✕</button>
                </div>

                <form @submit.prevent="submitNewCustomer" class="space-y-3 text-xs">
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">نام و نام خانوادگی مشتری <span class="text-rose-500">*</span></label>
                        <input v-model="newCustomerForm.full_name" type="text" required placeholder="مثال: محمد امینی"
                            class="w-full px-3 py-2 border border-slate-200 rounded-xl">
                    </div>
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">شماره همراه</label>
                            <input v-model="newCustomerForm.phone_number" type="tel" placeholder="09xxxxxxxxx"
                                class="w-full px-3 py-2 border border-slate-200 rounded-xl font-mono">
                        </div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">کد ملی</label>
                            <input v-model="newCustomerForm.national_code" type="text" placeholder="۱۰ رقم"
                                class="w-full px-3 py-2 border border-slate-200 rounded-xl font-mono">
                        </div>
                    </div>
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">شناسه تلگرام (اختیاری)</label>
                            <input v-model="newCustomerForm.telegram_id" type="number" placeholder="مثال: 12345678"
                                class="w-full px-3 py-2 border border-slate-200 rounded-xl font-mono">
                        </div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">یوزرنیم تلگرام (اختیاری)</label>
                            <input v-model="newCustomerForm.username" type="text" placeholder="بدون @"
                                class="w-full px-3 py-2 border border-slate-200 rounded-xl font-mono">
                        </div>
                    </div>
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">کد فراگیر اتباع (در صورت وجود)</label>
                        <input v-model="newCustomerForm.alien_code" type="text" placeholder="کد آمایش یا گذرنامه"
                            class="w-full px-3 py-2 border border-slate-200 rounded-xl font-mono">
                    </div>
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">یادداشت‌های داخلی پرونده</label>
                        <textarea v-model="newCustomerForm.notes" rows="2" placeholder="توضیحات اختصاصی در مورد متقاضی..."
                            class="w-full px-3 py-2 border border-slate-200 rounded-xl"></textarea>
                    </div>
                    <div class="pt-2 flex justify-end gap-2">
                        <button type="button" @click="newCustomerModal = false" class="px-4 py-2 bg-slate-100 hover:bg-slate-200 rounded-xl text-slate-600 font-bold">انصراف</button>
                        <button type="submit" :disabled="isCreatingCustomer"
                            class="px-5 py-2 bg-gradient-to-r from-limo-500 to-lime-600 hover:from-limo-400 hover:to-lime-500 text-slate-950 font-black rounded-xl">
                            ایجاد پرونده مشتری
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- ======================================================== -->
        <!-- مودال ۳: ارسال مستقیم پیام تلگرام (Direct Msg Modal) -->
        <!-- ======================================================== -->
        <div v-if="directMsgModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm">
            <div class="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl border border-slate-100 text-right space-y-4">
                <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                    <h3 class="font-black text-sm text-slate-900">📩 ارسال پیام از طرف ربات به تلگرام مشتری</h3>
                    <button @click="directMsgModal = false" class="p-1 text-slate-400 hover:text-slate-600">✕</button>
                </div>
                <div class="p-3 bg-blue-50 border border-blue-100 rounded-xl text-xs text-blue-900">
                    گیرنده: <b>{{ directMsgTarget.full_name }}</b> (شناسه تلگرام: <code class="font-mono">{{ directMsgTarget.telegram_id }}</code>)
                </div>
                <form @submit.prevent="submitDirectMsg" class="space-y-3 text-xs">
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">متن پیام ارسالی به تلگرام متقاضی <span class="text-rose-500">*</span></label>
                        <textarea v-model="directMsgText" rows="4" required placeholder="متن پیام خود را بنویسید..."
                            class="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs"></textarea>
                    </div>
                    <div class="pt-2 flex justify-end gap-2">
                        <button type="button" @click="directMsgModal = false" class="px-4 py-2 bg-slate-100 rounded-xl text-slate-600 font-bold">انصراف</button>
                        <button type="submit" :disabled="!directMsgText.trim() || isSendingDirectMsg"
                            class="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl flex items-center gap-1.5">
                            <span v-if="isSendingDirectMsg" class="animate-spin text-sm">⏳</span>
                            <span>ارسال پیام تلگرام 🚀</span>
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- ======================================================== -->
        <!-- مودال ۴: جزییات سفارش و تغییر وضعیت + ارسال به نرم‌افزار کافی‌نت -->
        <!-- ======================================================== -->
        <div v-if="selectedOrder" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm">
            <div class="bg-white rounded-3xl max-w-3xl w-full max-h-[90vh] flex flex-col shadow-2xl border border-slate-100 text-right overflow-hidden">
                <div class="p-5 border-b border-slate-100 flex justify-between items-center bg-slate-50">
                    <div>
                        <div class="flex items-center gap-2">
                            <h3 class="font-black text-sm text-slate-900">پرونده سفارش: {{ selectedOrder.service_title }}</h3>
                            <span :class="statusBadgeClass(selectedOrder.status)" class="px-2 py-0.5 rounded-full text-[10px] font-bold">{{ statusLabel(selectedOrder.status) }}</span>
                        </div>
                        <div class="text-xs text-slate-500 font-mono mt-0.5">کد رهگیری: {{ selectedOrder.tracking_code }} | متقاضی: {{ selectedOrder.full_name }}</div>
                    </div>
                    <button @click="selectedOrder = null" class="p-1.5 text-slate-400 hover:text-slate-600 rounded-xl">✕</button>
                </div>

                <div class="p-6 overflow-y-auto flex-1 space-y-5 text-xs">
                    <!-- داده‌های فرم ثبت شده متقاضی -->
                    <div class="space-y-3">
                        <h4 class="font-black text-xs text-slate-800 flex items-center gap-1.5">
                            <span>📋</span>
                            <span>اقلام و فیلدهای ثبت‌شده متقاضی</span>
                        </h4>
                        <div class="bg-slate-50 rounded-2xl p-4 border border-slate-200 grid grid-cols-1 sm:grid-cols-2 gap-3">
                            <div v-for="(val, key) in parseOrderData(selectedOrder.form_data)" :key="key" class="border-b border-slate-100 pb-2">
                                <span class="text-[10px] text-slate-400 block">{{ formatFieldKey(key) }}</span>
                                <b class="text-slate-800 font-mono text-[11px] break-all">{{ val || '---' }}</b>
                            </div>
                        </div>
                    </div>

                    <!-- بخش تغییر وضعیت و ثبت یادداشت اپراتور -->
                    <div class="space-y-3 pt-3 border-t border-slate-100">
                        <h4 class="font-black text-xs text-slate-800">تغییر وضعیت پرونده و ارسال پیام خودکار</h4>
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                            <div>
                                <label class="block font-bold text-slate-700 mb-1">وضعیت جدید</label>
                                <select v-model="newOrderStatus" class="w-full px-3 py-2 border border-slate-200 rounded-xl font-bold text-xs bg-white">
                                    <option value="PENDING">در انتظار بررسی</option>
                                    <option value="APPROVED">تأیید و در حال انجام</option>
                                    <option value="NEED_INFO">نقص مدارک / نیازمند اطلاعات</option>
                                    <option value="COMPLETED">تکمیل شده و تحویل داده شده</option>
                                    <option value="REJECTED">رد شده / لغو شده</option>
                                </select>
                            </div>
                            <div>
                                <label class="block font-bold text-slate-700 mb-1">یادداشت برای متقاضی (در تلگرام ارسال می‌شود)</label>
                                <input v-model="newOperatorNotes" type="text" placeholder="مثال: پرونده با موفقیت انجام شد..."
                                    class="w-full px-3 py-2 border border-slate-200 rounded-xl text-xs">
                            </div>
                        </div>
                    </div>
                </div>

                <div class="p-4 border-t border-slate-100 bg-slate-50 flex flex-wrap justify-between items-center gap-2">
                    <div class="flex items-center gap-2">
                        <button @click="softDeleteItem('order', selectedOrder.id, selectedOrder.tracking_code)"
                            class="px-3 py-2 bg-rose-50 hover:bg-rose-100 text-rose-700 rounded-xl text-xs font-bold transition">
                            🗑️ انتقال به سطل زباله
                        </button>
                        <!-- دکمه اتصال و ارسال به نرم‌افزار کافی‌نت -->
                        <button @click="syncOrderToShop(selectedOrder.id)"
                            class="px-3 py-2 bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 rounded-xl text-xs font-bold transition flex items-center gap-1.5 shadow-sm">
                            <span>🔗</span>
                            <span>ارسال به نرم‌افزار کافی‌نت (سفارشات تلگرام)</span>
                        </button>
                    </div>

                    <div class="flex items-center gap-2">
                        <button @click="selectedOrder = null" class="px-4 py-2 bg-white border border-slate-200 rounded-xl text-slate-600 text-xs font-bold">بستن</button>
                        <button @click="updateOrderStatus" :disabled="isUpdatingStatus"
                            class="px-5 py-2 bg-gradient-to-r from-limo-500 to-lime-600 hover:from-limo-400 hover:to-lime-500 text-slate-950 rounded-xl text-xs font-black transition shadow-sm">
                            ثبت تغییر وضعیت
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- ======================================================== -->
        <!-- مودال ۵: فرم‌ساز پویا و ویرایش خدمت (Service Modal) -->
        <!-- ======================================================== -->
        <div v-if="serviceModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm">
            <div class="bg-white rounded-3xl max-w-3xl w-full max-h-[92vh] flex flex-col shadow-2xl border border-slate-100 text-right overflow-hidden">
                <div class="p-5 border-b border-slate-100 flex justify-between items-center bg-slate-50">
                    <h3 class="font-black text-sm text-slate-900">🛠️ ویرایش خدمت و فرم‌ساز فیلدهای اختصاصی</h3>
                    <button @click="serviceModal = false" class="p-1.5 text-slate-400 hover:text-slate-600 rounded-xl">✕</button>
                </div>

                <div class="p-6 overflow-y-auto flex-1 space-y-5 text-xs">
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">عنوان خدمت <span class="text-rose-500">*</span></label>
                            <input v-model="serviceForm.title" type="text" required class="w-full px-3 py-2 border border-slate-200 rounded-xl">
                        </div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">کد یکتای سیستم <span class="text-rose-500">*</span></label>
                            <input v-model="serviceForm.code" type="text" required class="w-full px-3 py-2 border border-slate-200 rounded-xl font-mono">
                        </div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">دسته‌بندی</label>
                            <select v-model="serviceForm.category_id" class="w-full px-3 py-2 border border-slate-200 rounded-xl bg-white">
                                <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.title }}</option>
                            </select>
                        </div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">کارمزد پایه (تومان)</label>
                            <input v-model.number="serviceForm.base_fee" type="number" class="w-full px-3 py-2 border border-slate-200 rounded-xl font-mono">
                        </div>
                    </div>

                    <div>
                        <label class="block font-bold text-slate-700 mb-1">توضیحات و راهنمای متقاضی</label>
                        <textarea v-model="serviceForm.description" rows="2" class="w-full px-3 py-2 border border-slate-200 rounded-xl"></textarea>
                    </div>

                    <!-- تنظیم هزینه شاهدان برای خدمت کد رهگیری مسکن -->
                    <div v-if="serviceForm.code === 'HOUSING_TRACKING_CODE' || (serviceForm.title && serviceForm.title.includes('رهگیری'))"
                        class="p-4 bg-amber-50 border border-amber-200 rounded-2xl space-y-2">
                        <div class="flex items-center gap-2">
                            <span class="text-xl">🏠</span>
                            <b class="text-amber-900 font-bold">تنظیم اختصاصی هزینه تأمین دو شاهد رسمی (انتقال‌یافته از تنظیمات)</b>
                        </div>
                        <p class="text-[11px] text-amber-700">این مبلغ در صورتی که متقاضی گزینه «تأمین شاهد توسط لیمو» را انتخاب فرماید، به فاکتور افزوده می‌شود.</p>
                        <div class="flex items-center gap-3">
                            <input v-model.number="serviceForm.witness_fee" type="number" placeholder="3500000"
                                class="w-48 px-3 py-2 border border-amber-300 rounded-xl text-xs font-mono">
                            <span class="text-xs font-bold text-amber-900 font-mono">{{ formatTomans(serviceForm.witness_fee || 0) }}</span>
                        </div>
                    </div>

                    <!-- بخش فرم‌ساز فیلدهای سفارشی پویا -->
                    <div class="space-y-3 pt-3 border-t border-slate-100">
                        <div class="flex justify-between items-center">
                            <div>
                                <h4 class="font-black text-xs text-slate-800">فرم‌ساز پویا: فیلدهای سفارشی مورد نیاز متقاضی</h4>
                                <p class="text-[10px] text-slate-400">فیلدهایی که در صفحه مینی‌اپلیکیشن برای ثبت این خدمت به مشتری نمایش داده می‌شوند</p>
                            </div>
                            <button type="button" @click="addCustomField"
                                class="px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-xl font-bold text-xs transition flex items-center gap-1">
                                <span>➕ افزودن فیلد</span>
                            </button>
                        </div>

                        <div class="space-y-2">
                            <div v-for="(field, index) in customFields" :key="index"
                                class="p-3 bg-slate-50 border border-slate-200 rounded-xl grid grid-cols-1 sm:grid-cols-12 gap-2 items-center">
                                <div class="sm:col-span-4">
                                    <label class="block text-[10px] text-slate-400 mb-0.5">عنوان نمایشی فیلد</label>
                                    <input v-model="field.label" type="text" placeholder="مثال: شماره دانشجویی"
                                        class="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg text-xs bg-white">
                                </div>
                                <div class="sm:col-span-3">
                                    <label class="block text-[10px] text-slate-400 mb-0.5">شناسه متغیر (Key)</label>
                                    <input v-model="field.name" type="text" placeholder="student_id"
                                        class="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg text-xs font-mono bg-white">
                                </div>
                                <div class="sm:col-span-3">
                                    <label class="block text-[10px] text-slate-400 mb-0.5">نوع داده</label>
                                    <select v-model="field.type" class="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg text-xs bg-white">
                                        <option value="text">متن ساده (Text)</option>
                                        <option value="number">عدد (Number)</option>
                                        <option value="date">تاریخ شمسی (Date)</option>
                                        <option value="select">انتخابی چندگزینه‌ای (Select)</option>
                                        <option value="file">آپلود مدرک / فایل (File)</option>
                                    </select>
                                </div>
                                <div class="sm:col-span-1 flex items-center justify-center pt-3">
                                    <label class="flex items-center gap-1 cursor-pointer">
                                        <input type="checkbox" v-model="field.required" class="rounded text-limo-600">
                                        <span class="text-[10px] text-slate-600 font-bold">الزامی</span>
                                    </label>
                                </div>
                                <div class="sm:col-span-1 flex justify-end pt-3">
                                    <button type="button" @click="removeCustomField(index)" class="p-1 text-slate-400 hover:text-rose-600">✕</button>
                                </div>
                            </div>
                            <div v-if="customFields.length === 0" class="p-6 text-center text-slate-400 text-xs border border-dashed border-slate-200 rounded-xl">
                                فیلد سفارشی خاصی تعریف نشده است. جهت ایجاد فیلد دکمه «افزودن فیلد» را فشار دهید.
                            </div>
                        </div>
                    </div>
                </div>

                <div class="p-4 border-t border-slate-100 bg-slate-50 flex justify-end gap-2">
                    <button type="button" @click="serviceModal = false" class="px-4 py-2 bg-white border border-slate-200 rounded-xl text-slate-600 text-xs font-bold">انصراف</button>
                    <button type="button" @click="saveServiceWithFields" :disabled="isSavingService"
                        class="px-6 py-2 bg-gradient-to-r from-limo-500 to-lime-600 hover:from-limo-400 hover:to-lime-500 text-slate-950 font-black rounded-xl text-xs transition shadow-sm">
                        ذخیره خدمت و فیلدها
                    </button>
                </div>
            </div>
        </div>

        <!-- ======================================================== -->
        <!-- مودال ۶: مدیریت دسته‌بندی‌ها (Category Modal) -->
        <!-- ======================================================== -->
        <div v-if="categoryModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm">
            <div class="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl border border-slate-100 text-right space-y-4">
                <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                    <h3 class="font-black text-sm text-slate-900">{{ categoryForm.id ? 'ویرایش دسته‌بندی' : '➕ دسته‌بندی جدید' }}</h3>
                    <button @click="categoryModal = false" class="p-1 text-slate-400 hover:text-slate-600">✕</button>
                </div>
                <form @submit.prevent="saveCategoryForm" class="space-y-3 text-xs">
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">عنوان دسته‌بندی <span class="text-rose-500">*</span></label>
                        <input v-model="categoryForm.title" type="text" required placeholder="مثال: امور دانشجویی" class="w-full px-3 py-2 border border-slate-200 rounded-xl">
                    </div>
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">کد یکتا (انگلیسی) <span class="text-rose-500">*</span></label>
                        <input v-model="categoryForm.code" type="text" required placeholder="STUDENT_SERVICES" class="w-full px-3 py-2 border border-slate-200 rounded-xl font-mono">
                    </div>
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">اولویت نمایش (عددی)</label>
                        <input v-model.number="categoryForm.order_priority" type="number" placeholder="1" class="w-full px-3 py-2 border border-slate-200 rounded-xl font-mono">
                    </div>
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">توضیحات</label>
                        <textarea v-model="categoryForm.description" rows="2" class="w-full px-3 py-2 border border-slate-200 rounded-xl"></textarea>
                    </div>
                    <div class="pt-2 flex justify-end gap-2">
                        <button type="button" @click="categoryModal = false" class="px-4 py-2 bg-slate-100 rounded-xl font-bold text-slate-600">انصراف</button>
                        <button type="submit" class="px-5 py-2 bg-gradient-to-r from-limo-500 to-lime-600 hover:from-limo-400 hover:to-lime-500 text-slate-950 font-black rounded-xl">ذخیره دسته‌بندی</button>
                    </div>
                </form>
            </div>
        </div>

        <!-- ======================================================== -->
        <!-- مودال ۷: شارژ / کسر دستی کیف پول (Wallet Modal) -->
        <!-- ======================================================== -->
        <div v-if="walletModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm">
            <div class="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl border border-slate-100 text-right space-y-4">
                <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                    <h3 class="font-black text-sm text-slate-900">💳 شارژ یا کسر دستی موجودی کیف پول</h3>
                    <button @click="walletModal = false" class="p-1 text-slate-400 hover:text-slate-600">✕</button>
                </div>

                <div class="p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs">
                    مشتری: <b>{{ walletForm.customer_name || 'انتخاب نشده' }}</b>
                </div>

                <form @submit.prevent="submitWalletAdjust" class="space-y-3 text-xs">
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">مبلغ به تومان (عدد مثبت جهت شارژ، عدد منفی جهت کسر) <span class="text-rose-500">*</span></label>
                        <input v-model.number="walletForm.amount" type="number" required placeholder="50000"
                            class="w-full px-3 py-2 border border-slate-200 rounded-xl font-mono text-sm">
                        <span class="text-[10px] text-slate-400 block mt-1">معادل: {{ formatTomans(walletForm.amount || 0) }}</span>
                    </div>
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">بابت / شرح تراکنش حسابداری <span class="text-rose-500">*</span></label>
                        <input v-model="walletForm.notes" type="text" required placeholder="شارژ دستی توسط مدیریت بابت..."
                            class="w-full px-3 py-2 border border-slate-200 rounded-xl">
                    </div>
                    <div class="pt-2 flex justify-end gap-2">
                        <button type="button" @click="walletModal = false" class="px-4 py-2 bg-slate-100 rounded-xl font-bold text-slate-600">انصراف</button>
                        <button type="submit" :disabled="isAdjustingWallet" class="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl">
                            ثبت تراکنش در کیف پول
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- ======================================================== -->
        <!-- مودال ۸: ایجاد و ویرایش ثبت‌نام مقطعی (Campaign Modal) -->
        <!-- ======================================================== -->
        <div v-if="campaignModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm">
            <div class="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-slate-100 text-right space-y-4">
                <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                    <h3 class="font-black text-sm text-slate-900">{{ campaignForm.id ? 'ویرایش ثبت‌نام مقطعی' : '➕ ثبت‌نام مقطعی جدید' }}</h3>
                    <button @click="campaignModal = false" class="p-1 text-slate-400 hover:text-slate-600">✕</button>
                </div>
                <form @submit.prevent="saveCampaignForm" class="space-y-3 text-xs">
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">عنوان رویداد / آزمون <span class="text-rose-500">*</span></label>
                        <input v-model="campaignForm.title" type="text" required placeholder="مثال: کنکور سراسری نوبت اول" class="w-full px-3 py-2 border border-slate-200 rounded-xl">
                    </div>
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">کد رویداد <span class="text-rose-500">*</span></label>
                            <input v-model="campaignForm.code" type="text" required placeholder="KONKUR_1405" class="w-full px-3 py-2 border border-slate-200 rounded-xl font-mono">
                        </div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">وضعیت رویداد</label>
                            <select v-model="campaignForm.status" class="w-full px-3 py-2 border border-slate-200 rounded-xl bg-white font-bold">
                                <option value="OPEN">ثبت‌نام فعال</option>
                                <option value="COMING_SOON">به‌زودی</option>
                                <option value="CLOSED">پایان مهلت</option>
                            </select>
                        </div>
                    </div>
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">تاریخ شروع</label>
                            <input v-model="campaignForm.start_at" type="date" class="w-full px-3 py-2 border border-slate-200 rounded-xl font-mono">
                        </div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">تاریخ پایان مهلت</label>
                            <input v-model="campaignForm.end_at" type="date" class="w-full px-3 py-2 border border-slate-200 rounded-xl font-mono">
                        </div>
                    </div>
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">تعرفه ثبت‌نام (تومان)</label>
                            <input v-model.number="campaignForm.base_fee" type="number" placeholder="50000" class="w-full px-3 py-2 border border-slate-200 rounded-xl font-mono">
                        </div>
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">اولویت نمایش (ترتیب)</label>
                            <input v-model.number="campaignForm.order_priority" type="number" placeholder="10" class="w-full px-3 py-2 border border-slate-200 rounded-xl font-mono">
                        </div>
                    </div>
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">توضیحات و مدارک مورد نیاز</label>
                        <textarea v-model="campaignForm.description" rows="2" placeholder="توضیحات و مدارک لازم برای ثبت‌نام در این رویداد..." class="w-full px-3 py-2 border border-slate-200 rounded-xl"></textarea>
                    </div>
                    <div class="pt-2 flex justify-end gap-2">
                        <button type="button" @click="campaignModal = false" class="px-4 py-2 bg-slate-100 rounded-xl font-bold text-slate-600">انصراف</button>
                        <button type="submit" class="px-5 py-2 bg-gradient-to-r from-limo-500 to-lime-600 hover:from-limo-400 hover:to-lime-500 text-slate-950 font-black rounded-xl">ذخیره رویداد مقطعی</button>
                    </div>
                </form>
            </div>
        </div>

        <!-- ======================================================== -->
        <!-- مودال ۹: ویرایش و ایجاد پایش سامانه (Monitor Modal) -->
        <!-- ======================================================== -->
        <div v-if="monitorModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm">
            <div class="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl border border-slate-100 text-right space-y-4">
                <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                    <h3 class="font-black text-sm text-slate-900">{{ monitorForm.id ? 'ویرایش سامانه پایش' : '➕ افزودن سامانه برای پایش' }}</h3>
                    <button @click="monitorModal = false" class="p-1 text-slate-400 hover:text-slate-600">✕</button>
                </div>
                <form @submit.prevent="saveMonitorForm" class="space-y-3 text-xs">
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">عنوان سامانه <span class="text-rose-500">*</span></label>
                        <input v-model="monitorForm.title" type="text" required placeholder="مثال: سامانه نوبت‌دهی تثبیت هویت" class="w-full px-3 py-2 border border-slate-200 rounded-xl">
                    </div>
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">کد یکتا <span class="text-rose-500">*</span></label>
                        <input v-model="monitorForm.code" type="text" required placeholder="IVSF" class="w-full px-3 py-2 border border-slate-200 rounded-xl font-mono">
                    </div>
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">نشانی اینترنتی سامانه (URL) <span class="text-rose-500">*</span></label>
                        <input v-model="monitorForm.url" type="url" required placeholder="http://ivsf.nsia.gov.af/" class="w-full px-3 py-2 border border-slate-200 rounded-xl font-mono">
                    </div>
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">فاصله بررسی خودکار (دقیقه)</label>
                        <input v-model.number="monitorForm.check_interval_minutes" type="number" placeholder="15" class="w-full px-3 py-2 border border-slate-200 rounded-xl font-mono">
                    </div>
                    <div class="pt-2 flex justify-end gap-2">
                        <button type="button" @click="monitorModal = false" class="px-4 py-2 bg-slate-100 rounded-xl font-bold text-slate-600">انصراف</button>
                        <button type="submit" class="px-5 py-2 bg-slate-900 text-white font-bold rounded-xl">ذخیره سامانه</button>
                    </div>
                </form>
            </div>
        </div>

        <!-- ======================================================== -->
        <!-- مودال ۱۰: ارسال اطلاعیه عمومی به کاربران (Broadcast Modal) -->
        <!-- ======================================================== -->
        <div v-if="broadcastModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm">
            <div class="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl border border-slate-100 text-right space-y-4">
                <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                    <h3 class="font-black text-sm text-slate-900">📢 ارسال اطلاعیه عمومی به متقاضیان تلگرام</h3>
                    <button @click="broadcastModal = false" class="p-1 text-slate-400 hover:text-slate-600">✕</button>
                </div>
                <div class="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-900">
                    این پیام به متقاضیانی که یادآور ثبت‌نام <b>{{ broadcastCampaign?.title }}</b> را فعال کرده‌اند ارسال خواهد شد.
                </div>
                <form @submit.prevent="submitBroadcast" class="space-y-3 text-xs">
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">متن اطلاعیه عمومی <span class="text-rose-500">*</span></label>
                        <textarea v-model="broadcastMessage" rows="4" required placeholder="ثبت‌نام آغاز شد! جهت تکمیل پرونده اقدام فرمایید..." class="w-full px-3 py-2 border border-slate-200 rounded-xl"></textarea>
                    </div>
                    <div class="pt-2 flex justify-end gap-2">
                        <button type="button" @click="broadcastModal = false" class="px-4 py-2 bg-slate-100 rounded-xl font-bold text-slate-600">انصراف</button>
                        <button type="submit" :disabled="isBroadcasting" class="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl">
                            ارسال اطلاعیه به تلگرام
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- ======================================================== -->
        <!-- مودال ۱۱: ویرایش کانال ارتباطی (Channel Modal) -->
        <!-- ======================================================== -->
        <div v-if="channelModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm">
            <div class="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl border border-slate-100 text-right space-y-4">
                <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                    <h3 class="font-black text-sm text-slate-900">ویرایش کانال ارتباطی</h3>
                    <button @click="channelModal = false" class="p-1 text-slate-400 hover:text-slate-600">✕</button>
                </div>
                <form @submit.prevent="saveChannelForm" class="space-y-3 text-xs">
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">عنوان کانال</label>
                        <input v-model="channelForm.title" type="text" required class="w-full px-3 py-2 border border-slate-200 rounded-xl">
                    </div>
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">شماره یا آیدی / لینک</label>
                        <input v-model="channelForm.value" type="text" class="w-full px-3 py-2 border border-slate-200 rounded-xl font-mono">
                    </div>
                    <div class="pt-2 flex justify-end gap-2">
                        <button type="button" @click="channelModal = false" class="px-4 py-2 bg-slate-100 rounded-xl font-bold text-slate-600">انصراف</button>
                        <button type="submit" class="px-5 py-2 bg-gradient-to-r from-limo-500 to-lime-600 hover:from-limo-400 hover:to-lime-500 text-slate-950 font-black rounded-xl">ذخیره</button>
                    </div>
                </form>
            </div>
        </div>

        <!-- ======================================================== -->
        <!-- مودال ۱۲: افزودن و ویرایش اپراتور سیستم (Operator Modal) -->
        <!-- ======================================================== -->
        <div v-if="operatorModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm">
            <div class="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl border border-slate-100 text-right space-y-4">
                <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                    <h3 class="font-black text-sm text-slate-900">➕ تعریف اپراتور و سطح دسترسی جدید</h3>
                    <button @click="operatorModal = false" class="p-1 text-slate-400 hover:text-slate-600">✕</button>
                </div>
                <form @submit.prevent="saveOperatorForm" class="space-y-3 text-xs">
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">نام کامل اپراتور <span class="text-rose-500">*</span></label>
                        <input v-model="operatorForm.full_name" type="text" required placeholder="مثال: علی رضایی" class="w-full px-3 py-2 border border-slate-200 rounded-xl">
                    </div>
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">نام کاربری ورود (Username) <span class="text-rose-500">*</span></label>
                        <input v-model="operatorForm.username" type="text" required placeholder="operator1" class="w-full px-3 py-2 border border-slate-200 rounded-xl font-mono">
                    </div>
                    <div>
                        <label class="block font-bold text-slate-700 mb-1">سطح دسترسی (نقش اپراتور)</label>
                        <select v-model="operatorForm.role" class="w-full px-3 py-2 border border-slate-200 rounded-xl bg-white font-bold">
                            <option value="SUPER_ADMIN">مدیر کل (دسترسی کامل به تمام بخش‌ها و مالی)</option>
                            <option value="REGISTRAR">اپراتور ثبت‌نام (بررسی سفارشات و خدمات)</option>
                            <option value="SUPPORT">پشتیبان چت (پاسخگویی به گفتگوی زنده متقاضیان)</option>
                            <option value="ACCOUNTANT">حسابدار (مشاهده تراکنش‌ها و امور مالی)</option>
                        </select>
                    </div>
                    <div class="pt-2 flex justify-end gap-2">
                        <button type="button" @click="operatorModal = false" class="px-4 py-2 bg-slate-100 rounded-xl font-bold text-slate-600">انصراف</button>
                        <button type="submit" class="px-5 py-2 bg-slate-900 text-white font-bold rounded-xl">ثبت دسترسی اپراتور</button>
                    </div>
                </form>
            </div>
        </div>
'''
