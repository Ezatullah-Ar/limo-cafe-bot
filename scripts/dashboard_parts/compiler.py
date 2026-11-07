# -*- coding: utf-8 -*-
import os
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

from part1_head_auth import HEAD_AND_AUTH
from part2_sidebar_layout import SIDEBAR_AND_LAYOUT
from part3_views import VIEWS_HTML
from part4_modals import MODALS_HTML
from part5_vue_app import VUE_APP_SCRIPT

full_html = HEAD_AND_AUTH + SIDEBAR_AND_LAYOUT + VIEWS_HTML + MODALS_HTML + VUE_APP_SCRIPT

print(f"Compiled HTML length: {len(full_html)} chars, {len(full_html.splitlines())} lines.")

# 1. Write scripts/generate_admin_dashboard.py
dashboard_py_content = f'''# -*- coding: utf-8 -*-
"""
تولید فایل جامع cloudflare/admin_html.js با طراحی ستون راست داشبورد (Right-Sidebar Layout)
و ۱۳ ماژول جامع عملیاتی مصوب بر اساس سند حاکم پروژه
"""
import os
import json

html_content = {repr(full_html)}

file_content = f"""/**
 * پنل مدیریت جامع و مستقل تحت وب کافی‌نت لیمو (Stand-alone Web Admin Dashboard)
 * ساختار بازآرایی‌شده با سایدبار راست (Right-Sidebar Layout)
 * شامل ۱۳ ماژول مستقل مصوب بر اساس سند حاکم پروژه:
 * ۱. پیشخوان و نظارت آنلاین (overview)
 * ۲. سفارشات و درخواست‌ها (orders)
 * ۳. مدیریت مشتریان و پرونده‌ها (customers / CRM)
 * ۴. خدمات و فرم‌ساز پویا (services & dynamic fields)
 * ۵. دسته‌بندی خدمات (categories CRUD)
 * ۶. کیف پول و تراکنش‌ها (wallets)
 * ۷. ثبت‌نام‌های مقطعی (seasonal campaigns)
 * ۸. گفتگوی زنده و تیکت‌ها (chats & support)
 * ۱۰. راه‌های ارتباطی (communication channels)
 * ۱۱. سطل زباله ۳۰ روزه (trash management)
 * ۱۲. پشتیبان‌گیری داده‌ها (backup & export)
 * ۱۳. تنظیمات و پل سیستم مغازه (settings & shop sync bridge)
 */

export const ADMIN_DASHBOARD_HTML = {{json.dumps(html_content, ensure_ascii=False)}};
"""

out_path = os.path.join(os.path.dirname(__file__), "..", "cloudflare", "admin_html.js")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(file_content)

print(f"Generated admin_html.js successfully. Length: {{len(file_content)}} bytes.")
'''

script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(script_dir, "..", ".."))

py_path = os.path.join(script_dir, "..", "generate_admin_dashboard.py")
with open(py_path, "w", encoding="utf-8") as f:
    f.write(dashboard_py_content)
print(f"Updated scripts/generate_admin_dashboard.py ({len(dashboard_py_content)} chars)")

# 2. Write cloudflare/admin_html.js directly
js_content = f"""/**
 * پنل مدیریت جامع و مستقل تحت وب کافی‌نت لیمو (Stand-alone Web Admin Dashboard)
 * ساختار بازآرایی‌شده با سایدبار راست (Right-Sidebar Layout)
 * شامل ۱۳ ماژول مستقل مصوب بر اساس سند حاکم پروژه:
 * ۱. پیشخوان و نظارت آنلاین (overview)
 * ۲. سفارشات و درخواست‌ها (orders)
 * ۳. مدیریت مشتریان و پرونده‌ها (customers / CRM)
 * ۴. خدمات و فرم‌ساز پویا (services & dynamic fields)
 * ۵. دسته‌بندی خدمات (categories CRUD)
 * ۶. کیف پول و تراکنش‌ها (wallets)
 * ۷. ثبت‌نام‌های مقطعی (seasonal campaigns)
 * ۸. گفتگوی زنده و تیکت‌ها (chats & support)
 * ۱۰. راه‌های ارتباطی (communication channels)
 * ۱۱. سطل زباله ۳۰ روزه (trash management)
 * ۱۲. پشتیبان‌گیری داده‌ها (backup & export)
 * ۱۳. تنظیمات و پل سیستم مغازه (settings & shop sync bridge)
 */

export const ADMIN_DASHBOARD_HTML = {json.dumps(full_html, ensure_ascii=False)};
"""

admin_html_js_path = os.path.join(script_dir, "..", "..", "cloudflare", "admin_html.js")
with open(admin_html_js_path, "w", encoding="utf-8") as f:
    f.write(js_content)
print(f"Updated cloudflare/admin_html.js directly ({len(js_content)} chars)")
