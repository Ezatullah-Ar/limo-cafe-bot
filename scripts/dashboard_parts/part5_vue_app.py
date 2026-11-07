# -*- coding: utf-8 -*-
# Part 5: Vue 3 Application Logic and Methods

VUE_APP_SCRIPT = r'''
    </div>

    <!-- اسکریپت ویو جی‌اس ۳ (Vue 3 Single Page Application) -->
    <script>
        const { createApp, ref, computed, onMounted } = Vue;

        createApp({
            setup() {
                // وضعیت احراز هویت
                const isAuthenticated = ref(false);
                const adminUser = ref({ username: 'admin' });
                const loginUsername = ref('admin');
                const loginPassword = ref('');
                const loginError = ref('');
                const isLoggingIn = ref(false);

                // ناوبری و تب فعال
                const currentTab = ref('overview');
                const mobileSidebarOpen = ref(false);
                const isLoading = ref(false);

                // آمار کلی
                const stats = ref({
                    total_orders: 0,
                    pending_orders: 0,
                    approved_orders: 0,
                    need_info_orders: 0,
                    completed_orders: 0,
                    total_users: 0
                });

                // داده‌های اصلی سیستم
                const orders = ref([]);
                const customers = ref([]);
                const services = ref([]);
                const categories = ref([]);
                const wallets = ref([]);
                const seasonalCampaigns = ref([]);
                const supportThreads = ref([]);
                const communicationChannels = ref([]);
                                const trashItems = ref([]);

                // فیلترهای سفارشات
                const orderStatusFilter = ref('ALL');
                const orderSearchQuery = ref('');
                const customerSearchQuery = ref('');
                const serviceCategoryFilter = ref('ALL');

                // مودال پرونده مشتری
                const selectedDossier = ref(null);
                const dossierTab = ref('orders');
                const dossierChatMessages = ref([]);
                const dossierReplyText = ref('');
                const isSendingDossierReply = ref(false);
                const customerEditForm = ref({});
                const isSavingCustomer = ref(false);

                // مودال افزودن مشتری دستی جدید
                const newCustomerModal = ref(false);
                const newCustomerForm = ref({
                    full_name: '',
                    phone_number: '',
                    national_code: '',
                    alien_code: '',
                    telegram_id: '',
                    username: '',
                    notes: ''
                });
                const isCreatingCustomer = ref(false);

                // مودال ارسال پیام مستقیم تلگرام
                const directMsgModal = ref(false);
                const directMsgTarget = ref({});
                const directMsgText = ref('');
                const isSendingDirectMsg = ref(false);

                // مودال جزییات سفارش
                const selectedOrder = ref(null);
                const newOrderStatus = ref('PENDING');
                const newOperatorNotes = ref('');
                const isUpdatingStatus = ref(false);

                // مودال خدمت و فرم‌ساز پویا
                const serviceModal = ref(false);
                const serviceForm = ref({
                    id: null,
                    category_id: 1,
                    code: '',
                    title: '',
                    description: '',
                    guide_content: '',
                    image_url: '',
                    official_url: '',
                    base_fee: 0,
                    witness_fee: 3500000,
                    order_priority: 0,
                    is_active: 1
                });
                const customFields = ref([]);
                const isSavingService = ref(false);

                // مودال دسته‌بندی
                const categoryModal = ref(false);
                const categoryForm = ref({
                    id: null,
                    code: '',
                    title: '',
                    description: '',
                    order_priority: 0
                });

                // مودال کیف پول
                const walletModal = ref(false);
                const walletForm = ref({
                    wallet_id: null,
                    user_id: null,
                    customer_name: '',
                    amount: 0,
                    notes: ''
                });
                const isAdjustingWallet = ref(false);

                // مودال ثبت‌نام مقطعی
                const campaignModal = ref(false);
                const campaignForm = ref({
                    id: null,
                    code: '',
                    title: '',
                    description: '',
                    status: 'OPEN',
                    is_active: 1
                });

                // مودال برودکست
                const broadcastModal = ref(false);
                const broadcastCampaign = ref(null);
                const broadcastMessage = ref('');
                const isBroadcasting = ref(false);

                // مودال کانال ارتباطی
                const channelModal = ref(false);
                const channelForm = ref({
                    id: null,
                    title: '',
                    key: '',
                    value: '',
                    is_active: 1
                });

                // ماژول چت زنده پشتیبانی
                const selectedThread = ref(null);
                const threadMessages = ref([]);
                const supportReplyText = ref('');
                const isSendingReply = ref(false);

                // تنظیمات کافی‌نت
                // تنظیمات پیشرفته و تب‌های فرعی
                const settingsActiveSubTab = ref('business');
                const operatorsList = ref([]);
                const operatorModal = ref(false);
                const operatorForm = ref({
                    id: null,
                    username: '',
                    full_name: '',
                    role: 'REGISTRAR'
                });
                const isSavingOperator = ref(false);
                const isTestingSync = ref(false);
                const syncTestResult = ref(null);
                const livePersianDate = ref('');

                // فرم جامع تنظیمات کافی‌نت لیمو
                const settingsForm = ref({
                    shop_name: 'کافی‌نت آنلاین لیمو',
                    is_open: '1',
                    shop_phone: '021-xxxxxxxx',
                    emergency_phone: '0912xxxxxxx',
                    work_hours: 'شنبه تا چهارشنبه ۸:۳۰ الی ۲۰:۳۰ | پنجشنبه‌ها ۸:۳۰ الی ۱۴:۰۰',
                    shop_address: 'تهران، میدان آزادی، مجتمع اداری لیمو',
                    shop_sync_enabled: '1',
                    shop_sync_url: 'http://localhost:3000/api/bot-orders',
                    shop_sync_api_key: 'limo_sync_secret_2026',
                    card_number: '6037-9918-xxxx-xxxx',
                    card_holder_name: 'کافی‌نت آنلاین لیمو',
                    card_iban: 'IRxxxxxxxxxxxxxxxxxxxx',
                    min_wallet_topup: 10000,
                    max_upload_size_mb: 15,
                    admin_tg_id: '',
                    allowed_file_types: 'jpg, jpeg, png, pdf, zip',
                    about_us_content: '',
                    motion_graphics_enabled: '1'
                });
                const isSavingSettings = ref(false);
                const isExportingBackup = ref(false);

                // مدیریت نشست و خروج خودکار امنیتی در صورت عدم فعالیت (Inactivity Timeout)
                const INACTIVITY_TIMEOUT_MS = 20 * 60 * 1000; // ۲۰ دقیقه
                let inactivityCheckInterval = null;
                const showInactivityWarning = ref(false);
                const remainingSeconds = ref(60);
                let lastActivityTimestamp = Date.now();

                function recordUserActivity() {
                    const now = Date.now();
                    // کنترل فرکانس ذخیره‌سازی در حافظه مرورگر (حداکثر یک‌بار در هر ۲ ثانیه)
                    if (now - lastActivityTimestamp > 2000) {
                        lastActivityTimestamp = now;
                        localStorage.setItem('limo_admin_last_activity', String(now));
                    }
                }

                function isSessionExpired() {
                    const token = localStorage.getItem('limo_admin_token');
                    if (!token) return true;
                    const savedTimeStr = localStorage.getItem('limo_admin_last_activity');
                    if (!savedTimeStr) return false;
                    const savedTime = parseInt(savedTimeStr, 10);
                    if (isNaN(savedTime)) return false;
                    return (Date.now() - savedTime > INACTIVITY_TIMEOUT_MS);
                }

                function checkSessionExpiry() {
                    if (!isAuthenticated.value) return;
                    if (isSessionExpired()) {
                        logoutDueToInactivity();
                    }
                }

                function logoutDueToInactivity() {
                    showInactivityWarning.value = false;
                    logout();
                    alert('⚠️ نشست شما به دلیل عدم فعالیت به مدت ۲۰ دقیقه به‌صورت خودکار و امن بسته شد. لطفاً دوباره وارد شوید.');
                }

                function extendSession() {
                    lastActivityTimestamp = Date.now();
                    localStorage.setItem('limo_admin_last_activity', String(lastActivityTimestamp));
                    showInactivityWarning.value = false;
                }
                // مدیریت مرتب‌سازی و کشیدن و رها کردن (Drag & Drop)
                const draggedIndex = ref(null);
                const draggedType = ref(null);
                const dragOverIndex = ref(null);

                function onDragStart(event, index, type) {
                    draggedIndex.value = index;
                    draggedType.value = type;
                    if (event && event.dataTransfer) {
                        event.dataTransfer.effectAllowed = 'move';
                        try { event.dataTransfer.setData('text/plain', String(index)); } catch(e) {}
                    }
                }

                function onDragOver(event, index) {
                    dragOverIndex.value = index;
                }

                function onDragEnd() {
                    draggedIndex.value = null;
                    draggedType.value = null;
                    dragOverIndex.value = null;
                }

                async function onDrop(event, targetIndex, type) {
                    if (draggedIndex.value === null || draggedType.value !== type || draggedIndex.value === targetIndex) {
                        onDragEnd();
                        return;
                    }

                    let list = null;
                    let endpointType = '';
                    if (type === 'services') {
                        list = filteredServices.value;
                        endpointType = 'services';
                    } else if (type === 'categories') {
                        list = categories.value;
                        endpointType = 'categories';
                    } else if (type === 'campaigns') {
                        list = seasonalCampaigns.value;
                        endpointType = 'campaigns';
                    } else if (type === 'channels') {
                        list = communicationChannels.value;
                        endpointType = 'channels';
                    }

                    if (!list || targetIndex < 0 || targetIndex >= list.length) {
                        onDragEnd();
                        return;
                    }

                    const fromIdx = draggedIndex.value;
                    const toIdx = targetIndex;

                    // جابه‌جایی المان در آرایه محلی
                    const [movedItem] = list.splice(fromIdx, 1);
                    list.splice(toIdx, 0, movedItem);

                    // محاسبه مجدد اولویت‌ها به ترتیب جدید (بالاترین آیتم بیشترین اولویت را می‌گیرد)
                    const total = list.length;
                    const updates = [];
                    list.forEach((item, idx) => {
                        item.order_priority = (total - idx) * 10;
                        updates.push({ id: item.id, priority: item.order_priority });
                    });

                    onDragEnd();

                    // ارسال ترتیبی به سرور
                    for (const u of updates) {
                        fetchWithAuth('/api/admin/priority/update', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ table: endpointType, type: endpointType, id: u.id, priority: u.priority, order_priority: u.priority })
                        }).catch(() => {});
                    }
                }


                // محاسبات وضعیت‌ها
                const pendingCount = computed(() => orders.value.filter(o => o.status === 'PENDING').length);
                const pendingSupportCount = computed(() => supportThreads.value.filter(t => t.status === 'PENDING_OPERATOR').length);

                const filteredOrders = computed(() => {
                    return orders.value.filter(o => {
                        const matchStatus = (orderStatusFilter.value === 'ALL') || (o.status === orderStatusFilter.value);
                        const q = orderSearchQuery.value.trim().toLowerCase();
                        const matchQuery = !q || (o.tracking_code && o.tracking_code.toLowerCase().includes(q)) || (o.full_name && o.full_name.toLowerCase().includes(q));
                        return matchStatus && matchQuery;
                    });
                });

                const filteredServices = computed(() => {
                    if (serviceCategoryFilter.value === 'ALL') return services.value;
                    return services.value.filter(s => s.category_id === serviceCategoryFilter.value);
                });

                // توابع کمکی احراز هویت
                function getAuthHeader() {
                    const token = localStorage.getItem('limo_admin_token');
                    return token ? { 'Authorization': 'Basic ' + token } : {};
                }

                async function fetchWithAuth(url, options = {}) {
                    options.headers = {
                        ...(options.headers || {}),
                        ...getAuthHeader()
                    };
                    const res = await fetch(url, options);
                    if (res.status === 401) {
                        isAuthenticated.value = false;
                        localStorage.removeItem('limo_admin_token');
                    }
                    return res;
                }

                // عملیات ورود و خروج
                async function login() {
                    loginError.value = '';
                    isLoggingIn.value = true;
                    try {
                        const token = btoa(`${loginUsername.value.trim()}:${loginPassword.value.trim()}`);
                        const res = await fetch('/api/admin/data', {
                            headers: { 'Authorization': 'Basic ' + token }
                        });
                        const data = await res.json();
                        if (res.ok && data.ok) {
                            localStorage.setItem('limo_admin_token', token);
                            localStorage.setItem('limo_admin_username', loginUsername.value.trim());
                            adminUser.value.username = loginUsername.value.trim();
                            isAuthenticated.value = true;
                            refreshData();
                            resetInactivityTimer();
                        } else {
                            loginError.value = 'نام کاربری یا کلمه عبور نادرست است.';
                        }
                    } catch (e) {
                        loginError.value = 'خطا در ارتباط با سرور.';
                    } finally {
                        isLoggingIn.value = false;
                    }
                }

                function logout() {
                    if (inactivityTimer) clearTimeout(inactivityTimer);
                    if (warningTimer) clearInterval(warningTimer);
                    showInactivityWarning.value = false;
                    localStorage.removeItem('limo_admin_token');
                    localStorage.removeItem('limo_admin_username');
                    isAuthenticated.value = false;
                    loginPassword.value = '';
                }

                // بارگذاری اولیه و جامع داده‌ها
                async function refreshData() {
                    isLoading.value = true;
                    try {
                        const res = await fetchWithAuth('/api/admin/data');
                        const data = await res.json();
                        if (data.ok) {
                            stats.value = data.stats || stats.value;
                            orders.value = data.orders || [];
                                                    }
                        await Promise.all([
                            fetchCustomers(),
                            fetchServices(),
                            fetchWallets(),
                            fetchCampaigns(),
                            fetchSupportThreads(),
                            fetchChannels(),
                            fetchTrashItems(),
                            fetchSettings(),
                            fetchOperators()
                        ]);
                    } catch (e) {
                        console.error("Error refreshing data:", e);
                    } finally {
                        isLoading.value = false;
                    }
                }

                function switchTab(tab) {
                    currentTab.value = tab;
                    mobileSidebarOpen.value = false;
                    refreshCurrentTab();
                }

                function refreshCurrentTab() {
                    if (currentTab.value === 'overview' || currentTab.value === 'orders') refreshData();
                    else if (currentTab.value === 'customers') fetchCustomers();
                    else if (currentTab.value === 'services' || currentTab.value === 'categories') fetchServices();
                    else if (currentTab.value === 'wallets') fetchWallets();
                    else if (currentTab.value === 'seasonal') fetchCampaigns();
                    else if (currentTab.value === 'chats') fetchSupportThreads();
                                        else if (currentTab.value === 'channels') fetchChannels();
                    else if (currentTab.value === 'trash') fetchTrashItems();
                    else if (currentTab.value === 'settings') { fetchSettings(); fetchOperators(); }
                    else if (currentTab.value === 'settings') fetchSettings();
                }

                // مدیریت مشتریان CRM
                let debounceTimer = null;
                function debouncedFetchCustomers() {
                    clearTimeout(debounceTimer);
                    debounceTimer = setTimeout(fetchCustomers, 300);
                }

                async function fetchCustomers() {
                    try {
                        const q = encodeURIComponent(customerSearchQuery.value || '');
                        const res = await fetchWithAuth(`/api/admin/customers?q=${q}`);
                        const data = await res.json();
                        if (data.ok) customers.value = data.customers || [];
                    } catch(e) {
                        console.error(e);
                    }
                }

                async function openCustomerDossier(c) {
                    if (!c || !c.id) return;
                    try {
                        const res = await fetchWithAuth(`/api/admin/customer/dossier?user_id=${c.id}`);
                        const data = await res.json();
                        if (data.ok) {
                            selectedDossier.value = data.dossier;
                            customerEditForm.value = { ...data.dossier.user };
                            dossierTab.value = 'orders';
                            loadDossierChat(c.id);
                        }
                    } catch (e) {
                        alert("خطا در باز کردن پرونده مشتری.");
                    }
                }

                async function loadDossierChat(userId) {
                    dossierChatMessages.value = [];
                    if (!selectedDossier.value?.support_threads?.length) return;
                    const threadId = selectedDossier.value.support_threads[0].id;
                    try {
                        const res = await fetchWithAuth(`/api/admin/support/messages?thread_id=${threadId}`);
                        const data = await res.json();
                        if (data.ok) dossierChatMessages.value = data.messages || [];
                    } catch(e) {}
                }

                async function sendDossierChatReply() {
                    if (!dossierReplyText.value.trim() || !selectedDossier.value) return;
                    isSendingDossierReply.value = true;
                    try {
                        const res = await fetchWithAuth('/api/admin/customer/direct-message', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                user_id: selectedDossier.value.user.id,
                                telegram_id: selectedDossier.value.user.telegram_id,
                                message: dossierReplyText.value.trim()
                            })
                        });
                        const data = await res.json();
                        if (data.ok) {
                            dossierChatMessages.value.push({
                                id: Date.now(),
                                sender_role: 'OPERATOR',
                                message_text: dossierReplyText.value.trim(),
                                created_at: new Date().toISOString()
                            });
                            dossierReplyText.value = '';
                        } else {
                            alert(data.error || "خطا در ارسال پیام.");
                        }
                    } catch (e) {
                        alert("خطا در برقراری ارتباط.");
                    } finally {
                        isSendingDossierReply.value = false;
                    }
                }

                function openNewCustomerModal() {
                    newCustomerForm.value = {
                        full_name: '',
                        phone_number: '',
                        national_code: '',
                        alien_code: '',
                        telegram_id: '',
                        username: '',
                        notes: ''
                    };
                    newCustomerModal.value = true;
                }

                async function submitNewCustomer() {
                    if (!newCustomerForm.value.full_name.trim()) return;
                    isCreatingCustomer.value = true;
                    try {
                        const res = await fetchWithAuth('/api/admin/customer/create', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(newCustomerForm.value)
                        });
                        const data = await res.json();
                        if (data.ok) {
                            alert("✅ مشتری جدید با موفقیت ثبت شد.");
                            newCustomerModal.value = false;
                            fetchCustomers();
                        } else {
                            alert("خطا: " + (data.error || "امکان ثبت وجود ندارد."));
                        }
                    } catch(e) {
                        alert("خطا در ثبت مشتری.");
                    } finally {
                        isCreatingCustomer.value = false;
                    }
                }

                async function saveCustomerInfo() {
                    if (!selectedDossier.value) return;
                    isSavingCustomer.value = true;
                    try {
                        const res = await fetchWithAuth('/api/admin/customer/update', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ id: selectedDossier.value.user.id, ...customerEditForm.value })
                        });
                        const data = await res.json();
                        if (data.ok) {
                            alert("✅ مشخصات متقاضی به‌روز شد.");
                            selectedDossier.value.user = { ...selectedDossier.value.user, ...customerEditForm.value };
                            fetchCustomers();
                        } else {
                            alert(data.error || "خطا در ذخیره اطلاعات.");
                        }
                    } catch (e) {
                        alert("خطای سرور.");
                    } finally {
                        isSavingCustomer.value = false;
                    }
                }

                function openDirectMsgModal(c) {
                    if (!c) return;
                    directMsgTarget.value = c;
                    directMsgText.value = '';
                    directMsgModal.value = true;
                }

                async function submitDirectMsg() {
                    if (!directMsgText.value.trim() || !directMsgTarget.value) return;
                    isSendingDirectMsg.value = true;
                    try {
                        const res = await fetchWithAuth('/api/admin/customer/direct-message', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                user_id: directMsgTarget.value.id,
                                telegram_id: directMsgTarget.value.telegram_id,
                                message: directMsgText.value.trim()
                            })
                        });
                        const data = await res.json();
                        if (data.ok) {
                            alert("✅ پیام تلگرام با موفقیت به مشتری ارسال شد.");
                            directMsgModal.value = false;
                        } else {
                            alert("خطا: " + (data.error || "ارسال ناموفق بود."));
                        }
                    } catch (e) {
                        alert("خطا در ارسال پیام مستقیم.");
                    } finally {
                        isSendingDirectMsg.value = false;
                    }
                }

                // سفارشات
                function openOrderDetail(ord) {
                    selectedOrder.value = ord;
                    newOrderStatus.value = ord.status;
                    newOperatorNotes.value = ord.operator_notes || '';
                }

                async function updateOrderStatus() {
                    if (!selectedOrder.value) return;
                    isUpdatingStatus.value = true;
                    try {
                        const res = await fetchWithAuth('/api/admin/order/status', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                order_id: selectedOrder.value.id,
                                status: newOrderStatus.value,
                                notes: newOperatorNotes.value
                            })
                        });
                        const data = await res.json();
                        if (data.ok) {
                            alert("✅ وضعیت سفارش با موفقیت بروز شد.");
                            selectedOrder.value = null;
                            refreshData();
                        } else {
                            alert(data.error || "خطا در بروزرسانی.");
                        }
                    } catch(e) {
                        alert("خطا در ارتباط با سرور.");
                    } finally {
                        isUpdatingStatus.value = false;
                    }
                }

                // خدمات و فرم‌ساز پویا
                async function fetchServices() {
                    try {
                        const res = await fetchWithAuth('/api/admin/services');
                        const data = await res.json();
                        if (data.ok) {
                            services.value = data.services || [];
                            categories.value = data.categories || [];
                        }
                    } catch(e) {
                        console.error(e);
                    }
                }

                function openNewServiceModal() {
                    serviceForm.value = {
                        id: null,
                        category_id: categories.value[0]?.id || 1,
                        code: '',
                        title: '',
                        description: '',
                        guide_content: '',
                        image_url: '',
                        official_url: '',
                        base_fee: 0,
                        witness_fee: 3500000,
                        order_priority: 0,
                        is_active: 1
                    };
                    customFields.value = [];
                    serviceModal.value = true;
                }

                function editService(s) {
                    serviceForm.value = {
                        ...s,
                        guide_content: s.guide_content || '',
                        image_url: s.image_url || '',
                        official_url: s.official_url || ''
                    };
                    customFields.value = [];
                    if (s.required_fields && typeof s.required_fields === 'object') {
                        customFields.value = Object.entries(s.required_fields).map(([k, v], idx) => ({
                            id: idx + 1,
                            name: k,
                            label: typeof v === 'object' ? (v.label || k) : String(v),
                            type: typeof v === 'object' ? (v.type || 'text') : 'text',
                            required: typeof v === 'object' ? !!v.required : true
                        }));
                    }
                    serviceModal.value = true;
                }

                function addCustomField() {
                    customFields.value.push({
                        id: Date.now(),
                        name: 'field_' + (customFields.value.length + 1),
                        label: 'فیلد جدید ' + (customFields.value.length + 1),
                        type: 'text',
                        required: true
                    });
                }

                function removeCustomField(index) {
                    customFields.value.splice(index, 1);
                }

                async function saveServiceWithFields() {
                    if (!serviceForm.value.title.trim() || !serviceForm.value.code.trim()) {
                        alert("عنوان و کد خدمت الزامی است.");
                        return;
                    }
                    isSavingService.value = true;
                    try {
                        const fieldsObj = {};
                        customFields.value.forEach(f => {
                            fieldsObj[f.name || 'field'] = {
                                label: f.label,
                                type: f.type,
                                required: f.required
                            };
                        });
                        const payload = {
                            ...serviceForm.value,
                            required_fields: fieldsObj
                        };
                        const res = await fetchWithAuth('/api/admin/service/save', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(payload)
                        });
                        const data = await res.json();
                        if (data.ok) {
                            alert("✅ خدمت و فیلدهای فرم با موفقیت ذخیره شد.");
                            serviceModal.value = false;
                            fetchServices();
                        } else {
                            alert("خطا: " + (data.error || "عدم موفقیت در ذخیره"));
                        }
                    } catch(e) {
                        alert("خطا در ذخیره خدمت.");
                    } finally {
                        isSavingService.value = false;
                    }
                }

                async function toggleServiceActive(s) {
                    s.is_active = s.is_active ? 0 : 1;
                    await fetchWithAuth('/api/admin/service/toggle', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ service_id: s.id, is_active: s.is_active })
                    });
                }

                // دسته‌بندی‌ها CRUD
                function openCategoriesModal() {
                    categoryForm.value = { id: null, code: '', title: '', description: '', order_priority: 0, is_active: true };
                    categoryModal.value = true;
                }

                function editCategory(cat) {
                    categoryForm.value = { ...cat, is_active: cat.is_active !== undefined ? Boolean(cat.is_active) : true };
                    categoryModal.value = true;
                }

                async function toggleCategoryStatus(cat) {
                    try {
                        const nextStatus = cat.is_active ? 0 : 1;
                        cat.is_active = nextStatus;
                        const res = await fetchWithAuth('/api/admin/category/toggle', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ id: cat.id, is_active: nextStatus })
                        });
                        const data = await res.json();
                        if (!data.ok) {
                            cat.is_active = nextStatus ? 0 : 1;
                            alert(data.error || "خطا در تغییر وضعیت دسته‌بندی");
                        } else {
                            fetchServices();
                        }
                    } catch(e) {
                        cat.is_active = cat.is_active ? 0 : 1;
                        alert("خطا در ارتباط با سرور");
                    }
                }

                async function saveCategoryForm() {
                    if (!categoryForm.value.title || !categoryForm.value.code) return;
                    try {
                        const payload = {
                            ...categoryForm.value,
                            is_active: categoryForm.value.is_active ? 1 : 0
                        };
                        const res = await fetchWithAuth('/api/admin/category/save', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(payload)
                        });
                        const data = await res.json();
                        if (data.ok) {
                            alert("✅ دسته‌بندی با موفقیت ذخیره شد.");
                            categoryModal.value = false;
                            fetchServices();
                        } else {
                            alert(data.error || "خطا در ذخیره.");
                        }
                    } catch(e) {
                        alert("خطای سرور.");
                    }
                }

                // کیف پول
                async function fetchWallets() {
                    try {
                        const res = await fetchWithAuth('/api/admin/wallets');
                        const data = await res.json();
                        if (data.ok) wallets.value = data.wallets || [];
                    } catch(e) {}
                }

                function openAdjustModal(w, u = null) {
                    walletForm.value = {
                        wallet_id: w?.id || null,
                        user_id: u?.id || w?.user_id || null,
                        customer_name: u?.full_name || w?.full_name || '',
                        amount: 0,
                        notes: ''
                    };
                    walletModal.value = true;
                }

                async function submitWalletAdjust() {
                    if (!walletForm.value.amount || !walletForm.value.notes.trim()) {
                        alert("مبلغ و شرح تراکنش الزامی هستند.");
                        return;
                    }
                    isAdjustingWallet.value = true;
                    try {
                        const res = await fetchWithAuth('/api/admin/wallet/adjust', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(walletForm.value)
                        });
                        const data = await res.json();
                        if (data.ok) {
                            alert("✅ تراکنش مالی با موفقیت در کیف پول ثبت شد.");
                            walletModal.value = false;
                            fetchWallets();
                            if (selectedDossier.value) openCustomerDossier(selectedDossier.value.user);
                        } else {
                            alert("خطا: " + (data.error || "عدم موفقیت"));
                        }
                    } catch(e) {
                        alert("خطا در ارتباط.");
                    } finally {
                        isAdjustingWallet.value = false;
                    }
                }

                async function toggleFreezeWallet(w) {
                    const res = await fetchWithAuth('/api/admin/wallet/toggle-freeze', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ wallet_id: w.id })
                    });
                    const data = await res.json();
                    if (data.ok) {
                        w.is_frozen = data.is_frozen;
                    }
                }

                // ثبت‌نام‌های مقطعی
                async function fetchCampaigns() {
                    try {
                        const res = await fetchWithAuth('/api/admin/seasonal/campaigns');
                        const data = await res.json();
                        if (data.ok) seasonalCampaigns.value = data.campaigns || [];
                    } catch(e) {}
                }

                function openNewCampaignModal() {
                    const today = new Date().toISOString().slice(0, 10);
                    const nextMonth = new Date(Date.now() + 30 * 86400000).toISOString().slice(0, 10);
                    campaignForm.value = {
                        id: null,
                        code: 'CAMP_' + Math.floor(1000 + Math.random() * 9000),
                        title: '',
                        description: '',
                        status: 'OPEN',
                        start_at: today,
                        end_at: nextMonth,
                        base_fee: 50000,
                        order_priority: 10,
                        is_active: 1
                    };
                    campaignModal.value = true;
                }

                function editCampaign(c) {
                    campaignForm.value = {
                        ...c,
                        start_at: (c.start_at || '').slice(0, 10),
                        end_at: (c.end_at || '').slice(0, 10),
                        base_fee: c.base_fee || 50000,
                        order_priority: c.order_priority || 0
                    };
                    campaignModal.value = true;
                }

                async function saveCampaignForm() {
                    if (!campaignForm.value.title || !campaignForm.value.title.trim()) {
                        alert('لطفاً عنوان رویداد مقطعی را وارد فرمایید.');
                        return;
                    }
                    try {
                        const res = await fetchWithAuth('/api/admin/seasonal/campaign', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(campaignForm.value)
                        });
                        const data = await res.json();
                        if (data.ok) {
                            alert('✅ رویداد مقطعی با موفقیت ذخیره شد.');
                            campaignModal.value = false;
                            await fetchCampaigns();
                        } else {
                            alert(data.error || 'خطا در ذخیره رویداد مقطعی');
                        }
                    } catch(e) {
                        alert('خطا در برقراری ارتباط با سرور: ' + e.message);
                    }
                }

                async function toggleSeasonalActive(c) {
                    c.is_active = c.is_active ? 0 : 1;
                    await fetchWithAuth('/api/admin/seasonal/status', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ id: c.id, campaign_id: c.id, is_active: c.is_active, status: c.status })
                    });
                }

                function openBroadcastModal(c) {
                    broadcastCampaign.value = c;
                    broadcastMessage.value = '';
                    broadcastModal.value = true;
                }

                async function submitBroadcast() {
                    if (!broadcastMessage.value.trim() || !broadcastCampaign.value) return;
                    isBroadcasting.value = true;
                    try {
                        const res = await fetchWithAuth('/api/admin/seasonal/broadcast', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                campaign_id: broadcastCampaign.value.id,
                                message: broadcastMessage.value.trim()
                            })
                        });
                        const data = await res.json();
                        if (data.ok) {
                            alert("✅ اطلاعیه عمومی به تمام متقاضیان ارسال شد.");
                            broadcastModal.value = false;
                        }
                    } catch(e) {
                        alert("خطا در ارسال برودکست.");
                    } finally {
                        isBroadcasting.value = false;
                    }
                }

                // چت زنده پشتیبانی
                async function fetchSupportThreads() {
                    try {
                        const res = await fetchWithAuth('/api/admin/support/threads?status=ALL');
                        const data = await res.json();
                        if (data.ok) {
                            supportThreads.value = data.threads || [];
                            if (!selectedThread.value && supportThreads.value.length > 0) {
                                selectThread(supportThreads.value[0]);
                            }
                        }
                    } catch(e) {}
                }

                async function selectThread(th) {
                    selectedThread.value = th;
                    try {
                        const res = await fetchWithAuth(`/api/admin/support/messages?thread_id=${th.id}`);
                        const data = await res.json();
                        if (data.ok) threadMessages.value = data.messages || [];
                    } catch(e) {}
                }

                async function sendSupportReply() {
                    if (!supportReplyText.value.trim() || !selectedThread.value) return;
                    isSendingReply.value = true;
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
                            threadMessages.value.push({
                                id: Date.now(),
                                sender_role: 'OPERATOR',
                                message_text: supportReplyText.value.trim(),
                                created_at: new Date().toISOString()
                            });
                            supportReplyText.value = '';
                        }
                    } catch(e) {
                        alert("خطا در ارسال پاسخ.");
                    } finally {
                        isSendingReply.value = false;
                    }
                }

                async function changeThreadStatus(threadId, status) {
                    await fetchWithAuth('/api/admin/support/status', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ thread_id: threadId, status })
                    });
                }

                // پایش سامانه‌ها
                async function fetchChannels() {
                    try {
                        const res = await fetchWithAuth('/api/admin/channels');
                        const data = await res.json();
                        if (data.ok) communicationChannels.value = data.channels || [];
                    } catch(e) {}
                }

                function openChannelEdit(ch) {
                    channelForm.value = { ...ch };
                    channelModal.value = true;
                }

                async function saveChannelForm() {
                    try {
                        const res = await fetchWithAuth('/api/admin/channel/update', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(channelForm.value)
                        });
                        const data = await res.json();
                        if (data.ok) {
                            channelModal.value = false;
                            fetchChannels();
                        }
                    } catch(e) {}
                }

                async function toggleChannelActive(ch) {
                    ch.is_active = ch.is_active ? 0 : 1;
                    await fetchWithAuth('/api/admin/channel/toggle', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ id: ch.id, is_active: ch.is_active })
                    });
                }

                // سطل زباله ۳۰ روزه (Soft Delete Trash)
                async function softDeleteItem(table, id, title) {
                    if (!confirm(`آیا از انتقال «${title}» به سطل زباله اطمینان دارید؟\nاین مورد تا ۳۰ روز در سطل زباله باقی می‌ماند و قابل بازگردانی است.`)) return;
                    try {
                        const res = await fetchWithAuth(`/api/admin/${table}/delete`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ id })
                        });
                        const data = await res.json();
                        if (data.ok) {
                            alert("🗑️ مورد با موفقیت به سطل زباله ۳۰ روزه منتقل شد.");
                            if (selectedDossier.value) selectedDossier.value = null;
                            if (selectedOrder.value) selectedOrder.value = null;
                            refreshCurrentTab();
                            fetchTrashItems();
                        }
                    } catch(e) {
                        alert("خطا در حذف.");
                    }
                }

                async function fetchTrashItems() {
                    try {
                        const res = await fetchWithAuth('/api/admin/trash/items');
                        const data = await res.json();
                        if (data.ok) trashItems.value = data.items || [];
                    } catch(e) {}
                }

                async function restoreTrashItem(item) {
                    try {
                        const res = await fetchWithAuth('/api/admin/trash/restore', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ table: item.table, id: item.id })
                        });
                        const data = await res.json();
                        if (data.ok) {
                            alert("♻️ مورد با موفقیت به بخش اصلی بازیابی شد.");
                            fetchTrashItems();
                            refreshCurrentTab();
                        }
                    } catch(e) {
                        alert("خطا در بازیابی.");
                    }
                }

                async function purgeTrashItem(item) {
                    if (!confirm(`هشدار: آیا از پاک‌سازی و حذف همیشگی این مورد اطمینان دارید؟ این عمل غیرقابل‌بازگشت است.`)) return;
                    try {
                        const res = await fetchWithAuth('/api/admin/trash/purge', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ table: item.table, id: item.id })
                        });
                        const data = await res.json();
                        if (data.ok) {
                            alert("⛔ مورد برای همیشه از دیتابیس پاک شد.");
                            fetchTrashItems();
                        }
                    } catch(e) {
                        alert("خطا در پاک‌سازی.");
                    }
                }

                // پشتیبان‌گیری و خروجی اکسل
                async function exportFullBackup() {
                    isExportingBackup.value = true;
                    try {
                        const res = await fetchWithAuth('/api/admin/backup/export');
                        if (!res.ok) throw new Error("Export failed");
                        const blob = await res.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `limo_backup_${new Date().toISOString().slice(0, 10)}.json`;
                        document.body.appendChild(a);
                        a.click();
                        a.remove();
                    } catch(e) {
                        alert("خطا در دانلود نسخه پشتیبان دیتابیس.");
                    } finally {
                        isExportingBackup.value = false;
                    }
                }

                function exportCSV() {
                    if (!orders.value.length) {
                        alert("سفارشی جهت خروجی موجود نیست.");
                        return;
                    }
                    let csvContent = "\uFEFFشناسه,کد رهگیری,مشتری,خدمت,وضعیت,تاریخ ثبت\n";
                    orders.value.forEach(o => {
                        csvContent += `"${o.id}","${o.tracking_code}","${o.full_name || ''}","${o.service_title || ''}","${statusLabel(o.status)}","${formatDate(o.created_at)}"\n`;
                    });
                    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
                    const url = URL.createObjectURL(blob);
                    const link = document.createElement("a");
                    link.setAttribute("href", url);
                    link.setAttribute("download", `limo_orders_${new Date().toISOString().slice(0,10)}.csv`);
                    document.body.appendChild(link);
                    link.click();
                    link.remove();
                }

                // تنظیمات کافی‌نت
                async function fetchSettings() {
                    try {
                        const res = await fetchWithAuth('/api/admin/settings');
                        const data = await res.json();
                        if (data.ok && data.settings) {
                            data.settings.forEach(s => {
                                if (settingsForm.value[s.key] !== undefined) {
                                    settingsForm.value[s.key] = s.value;
                                }
                            });
                        }
                    } catch(e) {}
                }

                async function saveShopSettings() {
                    isSavingSettings.value = true;
                    try {
                        const res = await fetchWithAuth('/api/admin/settings/batch', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ settings: settingsForm.value })
                        });
                        const data = await res.json();
                        if (data.ok) {
                            alert("✅ تنظیمات کاربردی کافی‌نت با موفقیت و به‌صورت اتمیک ذخیره شد.");
                            await fetchSettings();
                        } else {
                            alert(data.error || "خطا در ذخیره تنظیمات.");
                        }
                    } catch(e) {
                        alert("خطا در برقراری ارتباط جهت ذخیره تنظیمات.");
                    } finally {
                        isSavingSettings.value = false;
                    }
                }

                // فرمت‌ها و برچسب‌های کمکی
                // مدیریت اپراتورها و سطوح دسترسی (RBAC)
                async function fetchOperators() {
                    try {
                        const res = await fetchWithAuth('/api/admin/operators');
                        const data = await res.json();
                        if (data.ok) {
                            operatorsList.value = data.operators || [];
                        }
                    } catch(e) {
                        console.error("fetchOperators error:", e);
                    }
                }

                function openNewOperatorModal() {
                    operatorForm.value = { id: null, username: '', full_name: '', role: 'REGISTRAR' };
                    operatorModal.value = true;
                }

                async function saveOperatorForm() {
                    if (!operatorForm.value.username || !operatorForm.value.full_name) {
                        alert('لطفاً نام کامل و نام کاربری را وارد کنید.');
                        return;
                    }
                    isSavingOperator.value = true;
                    try {
                        const res = await fetchWithAuth('/api/admin/operators/save', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(operatorForm.value)
                        });
                        const data = await res.json();
                        if (data.ok) {
                            operatorModal.value = false;
                            await fetchOperators();
                            alert('✅ مشخصات اپراتور با موفقیت ذخیره شد.');
                        } else {
                            alert(data.error || 'خطا در ثبت اپراتور');
                        }
                    } catch(e) {
                        alert('خطا در برقراری ارتباط هنگام ثبت اپراتور');
                    } finally {
                        isSavingOperator.value = false;
                    }
                }

                async function deleteOperator(id) {
                    if (!confirm('آیا از حذف دسترسی این اپراتور اطمینان دارید؟')) return;
                    try {
                        const res = await fetchWithAuth('/api/admin/operators/delete', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ id })
                        });
                        const data = await res.json();
                        if (data.ok) {
                            await fetchOperators();
                        } else {
                            alert(data.error || 'خطا در حذف اپراتور');
                        }
                    } catch(e) {
                        alert('خطا در حذف اپراتور');
                    }
                }

                function operatorRoleLabel(role) {
                    if (role === 'SUPER_ADMIN') return 'مدیر کل';
                    if (role === 'REGISTRAR') return 'کارشناس ثبت‌نام';
                    if (role === 'SUPPORT') return 'پشتیبان مشتریان';
                    if (role === 'ACCOUNTANT') return 'حسابدار';
                    return role || 'اپراتور';
                }

                // ارسال و لینک سفارش به نرم‌افزار کافی‌نت (Cafinet_management)
                async function syncOrderToShop(orderId) {
                    try {
                        const res = await fetchWithAuth('/api/admin/order/sync-to-shop', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ order_id: orderId })
                        });
                        const data = await res.json();
                        if (data.ok) {
                            alert('سفارش با موفقیت به نرم‌افزار مدیریت کافی‌نت ارسال شد.');
                        } else {
                            alert('عدم امکان ارسال مستقیم به نرم‌افزار کافی‌نت.');
                        }
                    } catch(e) {
                        alert('خطا در ارسال سفارش به نرم‌افزار کافی‌نت: ' + e.message);
                    }
                }

                async function testShopSyncConnection() {
                    isTestingSync.value = true;
                    syncTestResult.value = null;
                    try {
                        const res = await fetchWithAuth('/api/admin/shop-sync/test', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                url: settingsForm.value.shop_sync_url,
                                apiKey: settingsForm.value.shop_sync_api_key
                            })
                        });
                        const data = await res.json();
                        syncTestResult.value = data;
                    } catch(e) {
                        syncTestResult.value = { ok: false, error: e.message };
                    } finally {
                        isTestingSync.value = false;
                    }
                }

                function updateLivePersianDate() {
                    try {
                        const now = new Date();
                        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', timeZone: 'Asia/Tehran' };
                        livePersianDate.value = new Intl.DateTimeFormat('fa-IR', options).format(now);
                    } catch(e) {
                        livePersianDate.value = new Date().toLocaleDateString('fa-IR');
                    }
                }

                
                // تغییر ترتیب و اولویت نمایش آیتم‌ها
                                // تنظیم مستقیم و سریع اولویت ترتیب نمایش
                async function updateItemPriority(table, id, priority) {
                    try {
                        const prioNum = parseInt(priority, 10) || 0;
                        const res = await fetchWithAuth('/api/admin/priority/update', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ table, id, priority: prioNum })
                        });
                        const data = await res.json();
                        if (data.ok) {
                            if (table === 'services' || table === 'categories') await fetchServices();
                            else if (table === 'campaigns') await fetchCampaigns();
                            else if (table === 'channels') await fetchChannels();
                        } else {
                            alert(data.error || 'خطا در ثبت اولویت');
                        }
                    } catch(e) {
                        alert('خطا در ارتباط با سرور هنگام ثبت اولویت');
                    }
                }

                async function moveItem(table, id, direction) {
                    try {
                        const res = await fetchWithAuth('/api/admin/reorder', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ table, id, direction })
                        });
                        const data = await res.json();
                        if (data.ok) {
                            if (table === 'services' || table === 'categories') await fetchServices();
                            else if (table === 'campaigns') await fetchCampaigns();
                            else if (table === 'channels') await fetchChannels();
                        } else {
                            alert(data.error || 'خطا در تغییر موقعیت');
                        }
                    } catch(e) {
                        alert('خطا در تغییر موقعیت آیتم');
                    }
                }

                function formatTomans(amount) {
                    return (parseInt(amount, 10) || 0).toLocaleString('fa-IR') + ' تومان';
                }

                function formatDate(dateStr) {
                    if (!dateStr) return '---';
                    try {
                        return new Date(dateStr).toLocaleString('fa-IR');
                    } catch(e) {
                        return dateStr;
                    }
                }

                function tabTitle(tab) {
                    const titles = {
                        overview: 'پیشخوان آماری و نظارت آنلاین',
                        orders: 'مدیریت سفارشات و پرونده‌های ثبتی',
                        customers: 'مدیریت مشتریان و پرونده‌های هویتی (CRM)',
                        services: 'فهرست خدمات و فرم‌ساز فیلدهای اختصاصی',
                        categories: 'دسته‌بندی‌های خدمات کافی‌نت',
                        wallets: 'کیف پول کاربران و دفاتر تراکنش‌های مالی',
                        seasonal: 'ثبت‌نام‌های مقطعی، کنکور و آزمون‌ها',
                        chats: 'مرکز گفتگوی زنده و تیکت‌های پشتیبانی',
                                                channels: 'مدیریت راه‌های ارتباطی و تماس',
                        trash: 'سطل زباله ۳۰ روزه و بایگانی امن',
                        backup: 'پشتیبان‌گیری کامل از پایگاه داده و خروجی اکسل',
                        settings: 'تنظیمات کاربردی و پل اتصال سیستم کافی‌نت'
                    };
                    return titles[tab] || 'داشبورد لیمو';
                }

                function statusBadgeClass(status) {
                    const map = {
                        PENDING: 'bg-amber-100 text-amber-800',
                        APPROVED: 'bg-blue-100 text-blue-800',
                        NEED_INFO: 'bg-purple-100 text-purple-800',
                        COMPLETED: 'bg-emerald-100 text-emerald-800',
                        REJECTED: 'bg-rose-100 text-rose-800'
                    };
                    return map[status] || 'bg-slate-100 text-slate-700';
                }

                function statusLabel(status) {
                    const map = {
                        PENDING: 'در انتظار بررسی',
                        APPROVED: 'در حال انجام',
                        NEED_INFO: 'نقص مدرک',
                        COMPLETED: 'تکمیل شده',
                        REJECTED: 'لغو شده'
                    };
                    return map[status] || status;
                }

                function supportStatusBadgeClass(st) {
                    const map = {
                        NEW: 'bg-amber-100 text-amber-800',
                        PENDING_OPERATOR: 'bg-rose-100 text-rose-800',
                        PENDING_CUSTOMER: 'bg-blue-100 text-blue-800',
                        CLOSED: 'bg-slate-100 text-slate-600'
                    };
                    return map[st] || 'bg-slate-100 text-slate-700';
                }

                function supportStatusLabel(st) {
                    const map = {
                        NEW: 'جدید',
                        PENDING_OPERATOR: 'در انتظار اپراتور',
                        PENDING_CUSTOMER: 'در انتظار متقاضی',
                        CLOSED: 'بسته شده'
                    };
                    return map[st] || st;
                }

                function seasonalBadgeClass(st) {
                    const map = {
                        COMING_SOON: 'bg-blue-100 text-blue-800',
                        OPEN: 'bg-emerald-100 text-emerald-800',
                        CLOSED: 'bg-slate-100 text-slate-600'
                    };
                    return map[st] || 'bg-slate-100 text-slate-700';
                }

                function seasonalStatusLabel(st) {
                    const map = {
                        COMING_SOON: 'به‌زودی',
                        OPEN: 'ثبت‌نام فعال',
                        CLOSED: 'پایان مهلت'
                    };
                    return map[st] || st;
                }

                function parseOrderData(formData) {
                    if (!formData) return {};
                    if (typeof formData === 'object') return formData;
                    try { return JSON.parse(formData); } catch(e) { return { data: formData }; }
                }

                function formatFieldKey(key) {
                    const dict = {
                        fullName: 'نام و نام خانوادگی',
                        phone: 'شماره همراه',
                        nationalCode: 'کد ملی',
                        alienCode: 'کد فراگیر اتباع',
                        studentId: 'شماره دانشجویی',
                        postalCode: 'کد پستی',
                        address: 'نشانی سکونت',
                        witnessChoice: 'گزینه تأمین شاهد',
                        witness1Name: 'نام شاهد اول',
                        witness1Nid: 'کدملی شاهد اول',
                        witness1Phone: 'موبایل شاهد اول',
                        witness2Name: 'نام شاهد دوم',
                        witness2Nid: 'کدملی شاهد دوم',
                        witness2Phone: 'موبایل شاهد دوم'
                    };
                    return dict[key] || key;
                }

                onMounted(() => {
                    updateLivePersianDate();
                    const token = localStorage.getItem('limo_admin_token');
                    if (token) {
                        if (isSessionExpired()) {
                            logoutDueToInactivity();
                        } else {
                            isAuthenticated.value = true;
                            adminUser.value.username = localStorage.getItem('limo_admin_username') || 'admin';
                            lastActivityTimestamp = parseInt(localStorage.getItem('limo_admin_last_activity') || String(Date.now()), 10);
                            refreshData();
                        }
                    }

                    // شنود تعاملات کاربر برای تمدید خودکار نشست فعال
                    ['mousemove', 'mousedown', 'keydown', 'touchstart', 'scroll'].forEach(evt => {
                        window.addEventListener(evt, recordUserActivity, { passive: true });
                    });

                    // بررسی وضعیت نشست هنگام بازگشت کاربر به تب مرورگر
                    document.addEventListener('visibilitychange', () => {
                        if (document.visibilityState === 'visible' && isAuthenticated.value) {
                            checkSessionExpiry();
                        }
                    });

                    // تایمر دوره‌ای بررسی عدم فعالیت (هر ۱۰ ثانیه)
                    inactivityCheckInterval = setInterval(checkSessionExpiry, 10000);
                });

                return {
                    draggedIndex,
                    draggedType,
                    dragOverIndex,
                    onDragStart,
                    onDragOver,
                    onDragEnd,
                    onDrop,
                    settingsActiveSubTab,
                    operatorsList,
                    operatorModal,
                    operatorForm,
                    isSavingOperator,
                    isTestingSync,
                    syncTestResult,
                    livePersianDate,
                    fetchOperators,
                    openNewOperatorModal,
                    saveOperatorForm,
                    deleteOperator,
                    operatorRoleLabel,
                    syncOrderToShop,
                    moveItem,
                    updateItemPriority,
                    showInactivityWarning,
                    remainingSeconds,
                    logoutDueToInactivity,
                    extendSession,
                    testShopSyncConnection,
                    isAuthenticated,
                    adminUser,
                    loginUsername,
                    loginPassword,
                    loginError,
                    isLoggingIn,
                    login,
                    logout,
                    currentTab,
                    mobileSidebarOpen,
                    isLoading,
                    stats,
                    orders,
                    customers,
                    services,
                    categories,
                    wallets,
                    seasonalCampaigns,
                    supportThreads,
                    communicationChannels,
                                        trashItems,
                    orderStatusFilter,
                    orderSearchQuery,
                    customerSearchQuery,
                    serviceCategoryFilter,
                    pendingCount,
                    pendingSupportCount,
                    filteredOrders,
                    filteredServices,
                    switchTab,
                    refreshCurrentTab,
                    debouncedFetchCustomers,
                    fetchCustomers,
                    openCustomerDossier,
                    selectedDossier,
                    dossierTab,
                    dossierChatMessages,
                    dossierReplyText,
                    isSendingDossierReply,
                    sendDossierChatReply,
                    customerEditForm,
                    isSavingCustomer,
                    saveCustomerInfo,
                    openNewCustomerModal,
                    newCustomerModal,
                    newCustomerForm,
                    isCreatingCustomer,
                    submitNewCustomer,
                    openDirectMsgModal,
                    directMsgModal,
                    directMsgTarget,
                    directMsgText,
                    isSendingDirectMsg,
                    submitDirectMsg,
                    openOrderDetail,
                    selectedOrder,
                    newOrderStatus,
                    newOperatorNotes,
                    isUpdatingStatus,
                    updateOrderStatus,
                    openNewServiceModal,
                    editService,
                    serviceModal,
                    serviceForm,
                    customFields,
                    addCustomField,
                    removeCustomField,
                    saveServiceWithFields,
                    isSavingService,
                    toggleServiceActive,
                    openCategoriesModal,
                    editCategory,
                    categoryModal,
                    categoryForm,
                    saveCategoryForm,
                    toggleCategoryStatus,
                    openCategoriesModal,
                    openAdjustModal,
                    walletModal,
                    walletForm,
                    isAdjustingWallet,
                    submitWalletAdjust,
                    toggleFreezeWallet,
                    openNewCampaignModal,
                    editCampaign,
                    campaignModal,
                    campaignForm,
                    saveCampaignForm,
                    toggleSeasonalActive,
                    openBroadcastModal,
                    broadcastModal,
                    broadcastCampaign,
                    broadcastMessage,
                    isBroadcasting,
                    submitBroadcast,
                    selectThread,
                    selectedThread,
                    threadMessages,
                    supportReplyText,
                    isSendingReply,
                    sendSupportReply,
                    changeThreadStatus,
                                                                                                                                                                openChannelEdit,
                    channelModal,
                    channelForm,
                    saveChannelForm,
                    toggleChannelActive,
                    softDeleteItem,
                    fetchTrashItems,
                    restoreTrashItem,
                    purgeTrashItem,
                    exportFullBackup,
                    isExportingBackup,
                    exportCSV,
                    settingsForm,
                    isSavingSettings,
                    saveShopSettings,
                    formatTomans,
                    formatDate,
                    tabTitle,
                    statusBadgeClass,
                    statusLabel,
                    supportStatusBadgeClass,
                    supportStatusLabel,
                    seasonalBadgeClass,
                    seasonalStatusLabel,
                    parseOrderData,
                    formatFieldKey
                };
            }
        }).mount('#admin-app');
    </script>
</body>
</html>'''
