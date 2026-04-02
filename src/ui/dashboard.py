import streamlit as st
from .styles import stat_card
from config import GEMINI_API_KEYS, VERSION
from ..utils.db_manager import db

def show_dashboard():
    st.title("📊 لوحة التحكم الذكية")
    st.markdown(f"**نظام مهووس V27** - مرحباً بك في المعمارية الجديدة الفائقة.")
    
    # جلب البيانات الحقيقية
    stats = db.get_stats()
    
    # صف البطاقات العلوية
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(stat_card("منتجاتنا", f"{stats['our_products']:,}", "📦"), unsafe_allow_html=True)
    with col2:
        st.markdown(stat_card("المنافسين", f"{stats['active_competitors']:,}", "🏢"), unsafe_allow_html=True)
    with col3:
        st.markdown(stat_card("تحديثات اليوم", f"{stats['updates_today']:,}", "⚡"), unsafe_allow_html=True)
    with col4:
        st.markdown(stat_card("إجمالي المنافسين", f"{stats['total_competitor_products']:,}", "🎯"), unsafe_allow_html=True)
    
    st.divider()
    
    # حالة النظام والخدمات
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("🚀 التشغيل السريع")
        st.write("ابدأ عملية كشط وتحليل جديدة الآن:")
        if st.button("🕸️ الانتقال لمحرك الكشط الذكي", type="primary"):
            st.session_state.current_page = "🕸️ الكشط الذكي"
            st.rerun()
            
    with c2:
        st.subheader("🛡️ حالة الخدمات")
        
        # فحص جوميناي
        if GEMINI_API_KEYS:
            st.success(f"Gemini API: متصل ({len(GEMINI_API_KEYS)} مفاتيح) ✅")
        else:
            st.error("Gemini API: غير متصل (تحقق من الإعدادات) ❌")
            
        st.info(f"إصدار النظام: {VERSION}")
        st.info("قاعدة البيانات: SQLite (WAL Mode) ✅")

    st.divider()
    st.markdown("---")
    st.caption("تم بناء هذه النسخة بمعمارية Modular لضمان أقصى درجات السرعة والاستقرار.")
        
