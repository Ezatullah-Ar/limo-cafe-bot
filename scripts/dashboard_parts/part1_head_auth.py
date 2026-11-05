# -*- coding: utf-8 -*-
# Part 1: Head, Tailwind styling, Auth Login screen

HEAD_AND_AUTH = r'''<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>داشبورد مدیریت کافی‌نت لیمو | Limo Admin</title>
    <link rel="icon" type="image/png" href="/logo.png">
    <script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: { sans: ['Vazirmatn', 'sans-serif'] },
                    colors: {
                        limo: { 50: '#f7fee7', 100: '#ecfccb', 200: '#d9f99d', 400: '#a3e635', 500: '#84cc16', 600: '#65a30d', 700: '#4d7c0f', 800: '#3f6212', 900: '#365314' },
                        slate: { 850: '#151f32', 900: '#0f172a', 950: '#020617' }
                    },
                    spacing: { '68': '17rem' }
                }
            }
        }
    </script>
    <style>
        [v-cloak] { display: none !important; }
        body { font-family: 'Vazirmatn', sans-serif; background-color: #f8fafc; color: #1e293b; }
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #0f172a; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
        .main-scroll::-webkit-scrollbar-track { background: #f1f5f9; }
        .main-scroll::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
    </style>
</head>
<body class="min-h-screen bg-slate-50 antialiased text-slate-800">
    <div id="admin-app" v-cloak class="min-h-screen flex flex-col">
        
        <!-- صفحه ورود امنیتی ادمین (احراز هویت دو فاکتوره: نام کاربری و کلمه عبور) -->
        <div v-if="!isAuthenticated" class="min-h-screen flex items-center justify-center p-4 bg-slate-950 relative overflow-hidden">
            <div class="absolute -top-40 -right-40 w-96 h-96 bg-limo-500/10 rounded-full blur-3xl"></div>
            <div class="absolute -bottom-40 -left-40 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"></div>
            
            <div class="max-w-md w-full bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl space-y-6 text-center relative z-10">
                <div class="inline-flex p-4 bg-slate-800 rounded-2xl border border-slate-700 shadow-inner">
                    <img src="/logo.png" alt="کافی نت لیمو" class="h-16 mx-auto object-contain">
                </div>
                <div>
                    <h1 class="text-xl font-black text-white">سامانه فرماندهی و مدیریت کافی‌نت لیمو</h1>
                    <p class="text-xs text-slate-400 mt-1">جهت دسترسی به داشبورد، اطلاعات کاربری خود را وارد فرمایید.</p>
                </div>
                <form @submit.prevent="login" class="space-y-4 text-right">
                    <div>
                        <label class="block text-xs font-bold text-slate-300 mb-1">نام کاربری مدیر</label>
                        <input v-model="loginUsername" type="text" required placeholder="admin"
                            class="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-limo-500 transition">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-300 mb-1">کلمه عبور امنیتی</label>
                        <input v-model="loginPassword" type="password" required placeholder="••••••••"
                            class="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-limo-500 transition">
                    </div>
                    <div v-if="loginError" class="p-3 bg-rose-950/60 border border-rose-800/80 rounded-xl text-xs text-rose-300 text-center font-bold">
                        {{ loginError }}
                    </div>
                    <button type="submit" :disabled="isLoggingIn"
                        class="w-full py-3.5 bg-limo-600 hover:bg-limo-500 text-slate-950 font-black rounded-xl text-sm transition shadow-lg shadow-limo-900/30 flex items-center justify-center gap-2">
                        <span v-if="isLoggingIn" class="animate-spin text-lg">⏳</span>
                        <span>ورود به داشبورد مدیریت</span>
                    </button>
                </form>
                <div class="pt-4 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500">
                    <span>کافی‌نت لیمو © ۱۴۰۵</span>
                    <span class="font-mono text-limo-400">نسخه ۲.۰.۰</span>
                </div>
            </div>
        </div>
'''
