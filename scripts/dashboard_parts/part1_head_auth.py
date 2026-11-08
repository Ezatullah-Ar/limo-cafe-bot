# -*- coding: utf-8 -*-
# Part 1: Head, Tailwind styling, Auth Login screen (Custom Limo Citrus & Obsidian Theme)

HEAD_AND_AUTH = r'''<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>پیشخوان مدیریت کافی‌نت لیمو | Limo Portal</title>
    <link rel="icon" type="image/png" href="/logo.png">
    
    <!-- فونت فارسی با پشتیبانی از سیستم‌های داخلی بدون نیاز به فیلترشکن -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    
    <script src="/vue.global.prod.js"></script>
    <script>
        if (typeof Vue === 'undefined') {
            document.write('<script src="https://cdn.jsdelivr.net/npm/vue@3/dist/vue.global.prod.js"><\/script>');
        }
    </script>
    <script>
        if (typeof Vue === 'undefined') {
            document.write('<script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"><\/script>');
        }
    </script>
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
                        limo: { 50: '#f7fee7', 100: '#ecfccb', 200: '#d9f99d', 300: '#bef264', 400: '#a3e635', 500: '#84cc16', 600: '#65a30d', 700: '#4d7c0f', 800: '#3f6212', 900: '#365314', 950: '#1a2e05' },
                        obsidian: { 800: '#0f1f18', 850: '#0a1712', 900: '#07120e', 950: '#040b08' }
                    },
                    spacing: { '68': '17.5rem' },
                    boxShadow: {
                        'glow-limo': '0 0 25px -5px rgba(132, 204, 22, 0.3)',
                        'card-soft': '0 4px 20px -2px rgba(15, 23, 42, 0.04)',
                        'card-hover': '0 12px 30px -4px rgba(15, 23, 42, 0.08)'
                    }
                }
            }
        }
    </script>
    <style>
        [v-cloak] { display: none !important; }
        body { 
            font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'IranSans', Tahoma, sans-serif; 
            background-color: #f8fafc; 
            color: #0f172a; 
        }
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: #07120e; }
        ::-webkit-scrollbar-thumb { background: #1b382c; border-radius: 4px; }
        .main-scroll::-webkit-scrollbar-track { background: #f1f5f9; }
        .main-scroll::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
        .glass-panel { background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); }
        .sidebar-gradient { background: linear-gradient(180deg, #07140f 0%, #0d221a 45%, #06110d 100%); }
    </style>
</head>
<body class="min-h-screen bg-slate-100 antialiased text-slate-800">
    <div id="admin-app" v-cloak class="min-h-screen flex flex-col">
        
        <!-- صفحه ورود امنیتی ادمین با هویت بصری کافی‌نت لیمو -->
        <div v-if="!isAuthenticated" class="min-h-screen flex items-center justify-center p-4 relative overflow-hidden"
            style="background: radial-gradient(circle at top right, #132e23 0%, #06110d 100%);">
            
            <div class="absolute -top-32 -right-32 w-80 h-80 bg-limo-500/15 rounded-full blur-3xl"></div>
            <div class="absolute -bottom-32 -left-32 w-80 h-80 bg-emerald-500/10 rounded-full blur-3xl"></div>
            
            <div class="max-w-md w-full bg-slate-900/90 backdrop-blur-xl border border-emerald-900/40 rounded-3xl p-8 shadow-2xl space-y-6 text-center relative z-10 shadow-glow-limo">
                <div class="inline-flex p-4 rounded-3xl bg-gradient-to-b from-emerald-950 to-slate-900 border border-emerald-500/30 shadow-inner">
                    <img src="/logo.png" alt="کافی نت لیمو" class="h-16 mx-auto object-contain">
                </div>
                <div>
                    <h1 class="text-xl font-black text-white flex items-center justify-center gap-2">
                        <span>پیشخوان هوشمند</span>
                        <span class="text-limo-400">کافی‌نت لیمو</span>
                    </h1>
                    <p class="text-xs text-slate-400 mt-1.5">جهت دسترسی به پنل مدیریت، مشخصات امنیتی خود را وارد فرمایید.</p>
                </div>
                <form @submit.prevent="login" class="space-y-4 text-right">
                    <div>
                        <label class="block text-xs font-bold text-slate-300 mb-1.5">نام کاربری اپراتور / مدیر</label>
                        <input v-model="loginUsername" type="text" required placeholder="admin"
                            class="w-full px-4 py-3 bg-slate-950/70 border border-emerald-900/50 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-limo-400 focus:ring-1 focus:ring-limo-400 transition">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-300 mb-1.5">کلمه عبور امنیتی</label>
                        <input v-model="loginPassword" type="password" required placeholder="••••••••"
                            class="w-full px-4 py-3 bg-slate-950/70 border border-emerald-900/50 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-limo-400 focus:ring-1 focus:ring-limo-400 transition">
                    </div>
                    <div v-if="loginError" class="p-3 bg-rose-950/60 border border-rose-800/80 rounded-xl text-xs text-rose-300 text-center font-bold">
                        {{ loginError }}
                    </div>
                    <button type="submit" :disabled="isLoggingIn"
                        class="w-full py-3.5 bg-gradient-to-r from-limo-500 to-lime-600 hover:from-limo-400 hover:to-lime-500 text-slate-950 font-black rounded-xl text-sm transition shadow-lg shadow-limo-950/40 flex items-center justify-center gap-2">
                        <span v-if="isLoggingIn" class="animate-spin text-lg">⏳</span>
                        <span>ورود به سامانه مدیریت</span>
                    </button>
                </form>
                <div class="pt-4 border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-500">
                    <span>کافی‌نت آنلاین لیمو © ۱۴۰۵</span>
                    <span class="font-mono text-limo-400 font-bold">v2.1 (Cloudflare Edge)</span>
                </div>
            </div>
        </div>
'''
