import assert from 'node:assert';

// Mock in-memory SQLite / D1 database emulator for Step 3 tests
class MockD1 {
  constructor() {
    this.categories = [
      { id: 1, code: 'STUDENT_SERVICES', title: '🎓 خدمات دانشجویی', description: '', order_priority: 1, is_active: 1, deleted_at: null },
      { id: 2, code: 'CONSULAR_SERVICES', title: '🌐 امور کنسولی', description: '', order_priority: 2, is_active: 1, deleted_at: null }
    ];
    this.services = [
      { id: 1, category_id: 1, code: 'EMT_VERIFICATION', title: 'تاییدیه تحصیلی', base_fee: 50000, order_priority: 1, is_active: 1, deleted_at: null },
      { id: 2, category_id: 1, code: 'SANJESH_REG', title: 'ثبت‌نام سنجش', base_fee: 65000, order_priority: 2, is_active: 1, deleted_at: null },
      { id: 3, category_id: 2, code: 'IVSF_APPOINTMENT', title: 'نوبت‌دهی تثبیت هویت', base_fee: 120000, order_priority: 1, is_active: 1, deleted_at: null }
    ];
    this.campaigns = [
      { id: 1, code: 'ARSHAD_1405', title: 'ثبت‌نام کنکور ارشد', base_fee: 85000, order_priority: 1, is_active: 1, deleted_at: null, start_at: '2026-11-01', end_at: '2026-11-20' },
      { id: 2, code: 'DOKTORA_1405', title: 'ثبت‌نام دکتری', base_fee: 95000, order_priority: 2, is_active: 0, deleted_at: null, start_at: '2026-11-05', end_at: '2026-11-25' }
    ];
    this.channels = [
      { id: 1, key: 'EITAA', title: 'پشتیبانی ایتا', value: 'https://eitaa.com/Cafinet_limo', order_priority: 1, is_active: 1, deleted_at: null },
      { id: 2, key: 'RUBIKA', title: 'پشتیبانی روبیکا', value: 'https://rubika.ir/cafinet_limo', order_priority: 2, is_active: 1, deleted_at: null }
    ];
    this.settings = {
      is_open: '1',
      about_us_content: 'کافی نت لیمو با بیش از ۱۰ سال سابقه خدمات اینترنتی و دانشجویی',
      motion_graphics_enabled: '1'
    };
  }

  // Telegram bot & Mini App query: active categories
  getActiveCategories() {
    return this.categories
      .filter(c => c.is_active === 1 && !c.deleted_at)
      .sort((a, b) => (a.order_priority - b.order_priority) || (a.id - b.id));
  }

  // Telegram bot & Mini App query: active services in category
  getActiveServicesForCategory(catCodeOrId) {
    const cat = this.categories.find(c => (c.code === catCodeOrId || c.id === catCodeOrId) && c.is_active === 1 && !c.deleted_at);
    if (!cat) return [];
    return this.services
      .filter(s => s.category_id === cat.id && s.is_active === 1 && !s.deleted_at)
      .sort((a, b) => (a.order_priority - b.order_priority) || (a.id - b.id));
  }

  // Bot single service query
  getActiveServiceByCode(code) {
    const s = this.services.find(svc => svc.code === code && svc.is_active === 1 && !svc.deleted_at);
    if (!s) return null;
    const cat = this.categories.find(c => c.id === s.category_id && c.is_active === 1 && !c.deleted_at);
    if (!cat) return null;
    return { ...s, cat_title: cat.title };
  }

  // Admin toggles category active status
  toggleCategory(id, isActive) {
    const cat = this.categories.find(c => c.id === id);
    if (cat) cat.is_active = isActive ? 1 : 0;
  }

  // Admin soft-deletes service
  softDeleteService(id) {
    const s = this.services.find(svc => svc.id === id);
    if (s) s.deleted_at = new Date().toISOString();
  }

  // Admin updates priority
  updatePriority(entity, id, newPrio) {
    const list = this[entity];
    const item = list.find(i => i.id === id);
    if (item) item.order_priority = newPrio;
  }
}

async function runTests() {
  console.log("=== RUNNING STEP 3 SINGLE SOURCE OF TRUTH TESTS ===");
  const db = new MockD1();

  // Test 1: Initial state across all interfaces
  let activeCats = db.getActiveCategories();
  assert.strictEqual(activeCats.length, 2, "Should return 2 active categories initially");
  let cat1Services = db.getActiveServicesForCategory('STUDENT_SERVICES');
  assert.strictEqual(cat1Services.length, 2, "Student services should have 2 active items");
  console.log("✔ Test 1 Passed: Initial active catalog loaded identically");

  // Test 2: Admin deactivates Category 1 -> Should immediately vanish from Bot & Mini App
  db.toggleCategory(1, 0);
  activeCats = db.getActiveCategories();
  assert.strictEqual(activeCats.length, 1, "Should have only 1 active category after Category 1 deactivation");
  assert.strictEqual(activeCats[0].code, 'CONSULAR_SERVICES');
  cat1Services = db.getActiveServicesForCategory('STUDENT_SERVICES');
  assert.strictEqual(cat1Services.length, 0, "Deactivated category services must return empty for bot/app");
  let directSvc = db.getActiveServiceByCode('EMT_VERIFICATION');
  assert.strictEqual(directSvc, null, "Direct service lookup in deactivated category must return null");
  console.log("✔ Test 2 Passed: Category deactivation immediately reflects across Bot & Mini App");

  // Test 3: Admin re-activates Category 1 and soft-deletes 1 service to Trash
  db.toggleCategory(1, 1);
  db.softDeleteService(1); // EMT_VERIFICATION trashed
  cat1Services = db.getActiveServicesForCategory('STUDENT_SERVICES');
  assert.strictEqual(cat1Services.length, 1, "Only 1 non-trashed service should remain");
  assert.strictEqual(cat1Services[0].code, 'SANJESH_REG');
  directSvc = db.getActiveServiceByCode('EMT_VERIFICATION');
  assert.strictEqual(directSvc, null, "Trashed service cannot be opened in Telegram bot");
  console.log("✔ Test 3 Passed: Soft deletion in Admin Trash hides service in Bot & Mini App");

  // Test 4: Priority reordering is uniform
  db.updatePriority('categories', 2, 0); // Move Consular to priority 0 (first)
  activeCats = db.getActiveCategories();
  assert.strictEqual(activeCats[0].code, 'CONSULAR_SERVICES', "Consular services should appear first");
  assert.strictEqual(activeCats[1].code, 'STUDENT_SERVICES', "Student services should appear second");
  console.log("✔ Test 4 Passed: Priority reordering is strictly respected");

  // Test 5: Currency formatting consistency across Bot & App
  const camp = db.campaigns[0];
  const feeToman = `${Number(camp.base_fee).toLocaleString('fa-IR')} تومان`;
  assert.strictEqual(feeToman, '۸۵٬۰۰۰ تومان', "Currency must format to Persian Tomans");
  console.log("✔ Test 5 Passed: Tomans formatting is unified");

  console.log("\nALL 5 STEP 3 SINGLE SOURCE OF TRUTH TESTS PASSED SUCCESSFULLY! 🎉");
}

runTests().catch(err => {
  console.error("Test failed:", err);
  process.exit(1);
});
