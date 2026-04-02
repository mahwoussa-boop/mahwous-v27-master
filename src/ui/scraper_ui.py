import streamlit as st
import asyncio
import pandas as pd
import os
from datetime import datetime
from ..engines.scraper import AsyncScraper
from .styles import stat_card

def show_scraper_ui():
    st.title("🕸️ محرك الكشط الذكي V27 - تجاوز الحظر")
    st.markdown("تم تحسين المحرك لتجاوز حماية Cloudflare ومتاجر سلة.")

    # 1. إدخال الرابط
    col_u1, col_u2 = st.columns([2, 1])
    store_url = col_u1.text_input("🔗 رابط المتجر الأساسي", placeholder="https://example.com")
    direct_sitemap = col_u2.text_input("📍 رابط الخريطة المباشر (اختياري)", placeholder="sitemap.xml")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔍 اكتشاف الروابط"):
            target = direct_sitemap if direct_sitemap else store_url
            if target:
                with st.spinner("جاري استخراج الروابط..."):
                    # تفعيل الوضع الآمن تلقائياً عند البحث عن الخريطة لضمان تجاوز الحماية
                    scraper = AsyncScraper(safe_mode=True)
                    loop = asyncio.new_event_loop()
                    
                    if direct_sitemap:
                        sitemap = direct_sitemap
                        st.info("⚠️ استخدام الرابط المباشر للخريطة...")
                    else:
                        sitemap = loop.run_until_complete(scraper.resolve_sitemap(store_url))
                    
                    if sitemap:
                        st.session_state.found_sitemap = sitemap
                        urls = loop.run_until_complete(scraper.get_urls_from_sitemap(sitemap))
                        st.session_state.found_urls = urls
                        st.success(f"📦 تم استخراج {len(urls)} منتج بنجاح!")
                        if not direct_sitemap: st.info(f"الخريطة المكتشفة: {sitemap}")
                    else:
                        st.error("❌ تعذر العثور على الخريطة. يرجى إدخال الرابط المباشر يدوياً.")

    # 2. لوحة التحكم بالجلسة
    if "found_urls" in st.session_state:
        urls = st.session_state.found_urls
        st.divider()
        st.info(f"الروابط الجاهزة للكشط: {len(urls)}")
        
        c1, c2, c3 = st.columns(3)
        concurrency = c1.slider("درجة التوازي (Concurrency)", 1, 20, 5)
        safe_mode = c2.toggle("🔒 الوضع الآمن (Safe Mode)", value=True, help="تأخير عشوائي طويل لتجنب الحظر.")
        
        if st.button("⚡ ابدأ الكشط وحفظ البيانات", type="primary"):
            run_realtime_scrape(urls, concurrency, safe_mode)

def run_realtime_scrape(urls, concurrency, safe_mode):
    """تنفيذ الكشط الحقيقي مع نظام Jitter"""
    scraper = AsyncScraper(concurrency=concurrency, safe_mode=safe_mode)
    
    status = st.status("🚀 جاري تهيئة المحرك...")
    m1, m2, m3 = st.columns(3)
    p_placeholder = st.empty()
    progress_bar = p_placeholder.progress(0, "بدء الكشط...")
    
    def on_progress(pct):
        progress_bar.progress(pct, f"تم كشط {int(pct * len(urls))} منتج...")
        m1.markdown(stat_card("تم الكشط", f"{int(pct * len(urls))}", "📦"), unsafe_allow_html=True)
        m2.markdown(stat_card("المتبقي", f"{len(urls) - int(pct * len(urls))}", "⏳"), unsafe_allow_html=True)

    # التشغيل الحقيقي
    loop = asyncio.new_event_loop()
    results = loop.run_until_complete(scraper.scrape_products(urls, progress_callback=on_progress))
    
    if results:
        df = pd.DataFrame(results)
        
        # حفظ البيانات
        if not os.path.exists("data"): os.makedirs("data")
        if not os.path.exists("data/scraping_history"): os.makedirs("data/scraping_history")
        
        latest_path = "data/competitors_latest.csv"
        df.to_csv(latest_path, index=False)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_path = f"data/scraping_history/scrape_{timestamp}.csv"
        df.to_csv(history_path, index=False)
        
        status.update(label=f"✅ اكتمل الكشط بنجاح! تم حفظ {len(df)} منتج.", state="complete")
        st.session_state.scraped_data_ready = True
        
        st.success("البيانات جاهزة للتحليل الآن.")
        col_act1, col_act2 = st.columns(2)
        with col_act1:
            if st.button("📊 بدء تحليل الأسعار الآن", use_container_width=True):
                st.session_state.current_page = "🔍 تحليل المنافسين"
                st.rerun()
        with col_act2:
            if st.button("🔍 البحث عن المفقودات", use_container_width=True):
                st.session_state.current_page = "📦 المفقودات"
                st.rerun()
        st.balloons()
    else:
        st.error("❌ فشل الكشط (غالباً بسبب حظر الموقع). جرب تقليل التوازي وتفعيل الوضع الآمن.")
        status.update(label="❌ فشل العملية", state="error")